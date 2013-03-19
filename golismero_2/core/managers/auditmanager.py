#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com
  Mario Vilas | mvilas@gmail.com

Golismero project site: http://code.google.com/p/golismero/
Golismero project mail: golismero.project@gmail.com

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

__all__ = ["AuditManager", "Audit"]

from .priscillapluginmanager import PriscillaPluginManager
from ..api.data.data import Data
from ..api.data.resource.url import Url
from ..common import AuditConfig
from ..database.datadb import DataDB
from ..managers.reportmanager import ReportManager
from ..messaging.codes import MessageType, MessageCode, MessagePriority
from ..messaging.message import Message
from ..messaging.notifier import AuditNotifier

from datetime import datetime
from multiprocessing import Queue


#--------------------------------------------------------------------------
class AuditManager (object):
    """
    Manage and control audits.
    """

    #----------------------------------------------------------------------
    def __init__(self, orchestrator, config):
        """
        Constructor.

        :param orchestrator: Core to send messages to
        :type orchestrator: Orchestrator

        :param config: Global configuration object
        :type config: OrchestratorConfig
        """

        # Init audits dicts
        self.__audits = dict()

        # Init params
        self.__orchestrator = orchestrator


    @property
    def orchestrator(self):
        return self.__orchestrator


    #----------------------------------------------------------------------
    def new_audit(self, params):
        """
        Creates a new audit.

        :param params: Params of audit
        :type params: AuditConfig

        :returns: Audit

        :raises: TypeError
        """
        if not isinstance(params, AuditConfig):
            raise TypeError("Expected AuditConfig, got %r instead" % type(params))

        # Create the audit
        m_audit = Audit(params, self.__orchestrator)

        # Store it
        self.__audits[m_audit.name] = m_audit

        # Run!
        m_audit.run()

        # Return it
        return m_audit


    #----------------------------------------------------------------------
    def has_audits(self):
        """
        Determine if there are audits currently runnning.

        :returns: True if there are audits in progress, False otherwise.
        """
        return bool(self.__audits)


    #----------------------------------------------------------------------
    def get_all_audits(self):
        """
        Get the list of audits currently running.

        :returns: dicts(str, Audit) -- Mapping of audit names to instances
        """
        return self.__audits


    #----------------------------------------------------------------------
    def get_audit(self, auditName):
        """
        Get an instance of an audit by its name.

        :param auditName: audit name
        :type auditName: str

        :returns: Audit -- instance of audit
        :raises: KeyError
        """
        return self.__audits[auditName]


    #----------------------------------------------------------------------
    def remove_audit(self, auditName):
        """
        Delete an instance of an audit by its name.

        :param auditName: audit name
        :type auditName: str

        :raises: KeyError
        """
        audit = self.__audits[auditName]
        try:
            audit.close()
        finally:
            del self.__audits[auditName]
            self.orchestrator.cacheManager.clean(auditName)


    #----------------------------------------------------------------------
    def dispatch_msg(self, message):
        """
        Process an incoming message from the orchestrator.

        :param message: incoming message
        :type message: Message

        :returns: bool - True if the message was sent, False if it was dropped

        :raises: TypeError, ValueError, KeyError
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Send info messages to their target audit
        if message.message_type == MessageType.MSG_TYPE_DATA:
            if not message.audit_name:
                raise ValueError("Info message with no target audit!")
            return self.get_audit(message.audit_name).dispatch_msg(message)

        # Process control messages
        elif message.message_type == MessageType.MSG_TYPE_CONTROL:

            # Send ACKs to their target audit
            if message.message_code == MessageCode.MSG_CONTROL_ACK:
                if message.audit_name:
                    audit = self.get_audit(message.audit_name)
                    audit.acknowledge()

                    # Check for audit termination.
                    #
                    # NOTE: This code assumes messages always arrive in order,
                    #       and ACKs are always sent AFTER responses from plugins.
                    #
                    if not audit.expecting_ack:

                        # Generate reports
                        if not audit.is_report_started:
                            audit.generate_reports()

                        # Send finish message
                        else:
                            m = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                                        message_code = MessageCode.MSG_CONTROL_STOP_AUDIT,
                                        message_info = True,   # True for finished, False for user cancel
                                        audit_name   = message.audit_name)
                            self.__orchestrator.dispatch_msg(m)

            # Stop an audit if requested
            elif message.message_code == MessageCode.MSG_CONTROL_STOP_AUDIT:
                if not message.audit_name:
                    raise ValueError("I don't know which audit to stop...")
                self.get_audit(message.audit_name).close()
                self.remove_audit(message.audit_name)

            # TODO: pause and resume audits, start new audits

        return True


    #----------------------------------------------------------------------
    def close(self):
        """
        Release all resources held by all audits.
        """
        for name in self.__audits.keys(): # not iterkeys, will be modified
            try:
                self.remove_audit(name)
            except:
                pass


#--------------------------------------------------------------------------
class Audit (object):
    """
    Instance of an audit, with its custom parameters, scope, target, plugins, etc.
    """


    #----------------------------------------------------------------------
    def __init__(self, auditParams, orchestrator):
        """
        :param orchestrator: Orchestrator instance that will receive messages sent by this audit.
        :type orchestrator: Orchestrator

        :param auditParams: Audit configuration.
        :type auditParams: AuditConfig
        """

        if not isinstance(auditParams, AuditConfig):
            raise TypeError("Expected AuditConfig, got %s instead" % type(auditParams))

        # Keep the audit settings.
        self.__params = auditParams

        # Keep a reference to the Orchestrator.
        self.__orchestrator = orchestrator

        # Set the audit name.
        self.__name = self.__params.audit_name
        if not self.__name:
            self.__name = self.__generateAuditName()
            self.__params.audit_name = self.__name

        # Initialize the "report started" flag.
        self.__is_report_started = False

        # Create the notifier.
        self.__notifier = AuditNotifier(self)

        # Create the report manager.
        self.__report_manager = ReportManager(auditParams, orchestrator)

        # Create the database.
        self.__database = DataDB(self.__name, auditParams.audit_db)


    @property
    def name(self):
        return self.__name

    @property
    def orchestrator(self):
        return self.__orchestrator

    @property
    def params(self):
        return self.__params

    @property
    def database(self):
        return self.__database

    @property
    def reportManager(self):
        return self.__report_manager

    @property
    def is_report_started(self):
        return self.__is_report_started


    #----------------------------------------------------------------------
    def __generateAuditName(self):
        """
        Get a random name for an audit.

        :returns: str -- generated name for the audit.
        """
        return "golismero-" + datetime.now().strftime("%Y-%m-%d-%H_%M")


    #----------------------------------------------------------------------
    def run(self):
        """
        Start execution of an audit.
        """

        # Reset the number of unacknowledged messages
        self.__expecting_ack = 0

        # Load testing plugins
        m_audit_plugins = PriscillaPluginManager().load_plugins(self.params.enabled_plugins,
                                                                self.params.disabled_plugins,
                                                                category = "testing")

        # Register plugins with the notifier
        for l_plugin in m_audit_plugins.itervalues():
            self.__notifier.add_plugin(l_plugin)

        # Send a message to the orchestrator for each target URL
        for url in self.params.targets:
            message = Message(message_info = Url(url),
                              message_type = MessageType.MSG_TYPE_DATA,
                              audit_name   = self.name)
            self.orchestrator.dispatch_msg(message)


    #----------------------------------------------------------------------
    def acknowledge(self):
        """
        Got an ACK for a message sent from this audit to the plugins.
        """
        self.__expecting_ack -= 1


    #----------------------------------------------------------------------
    @property
    def expecting_ack(self):
        """
        Return the number of ACKs expected by this audit.
        """
        return self.__expecting_ack


    #----------------------------------------------------------------------
    def dispatch_msg(self, message):
        """
        Send messages to the plugins of this audit.

        :param message: The message to send.
        :type message: Message

        :returns: bool - True if the message was sent, False if it was dropped
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Is it data?
        if message.message_type == MessageType.MSG_TYPE_DATA:

            # Add the data to the database
            is_new = self.database.add(message.message_info)

            # Is it duplicated data?
            if not is_new:

                # Send the ACK to the queue to make sure all
                # messages in-between are processed correctly.
                self.__expecting_ack += 1
                m = Message(message_type = MessageType.MSG_TYPE_CONTROL,
                            message_code = MessageCode.MSG_CONTROL_ACK,
                                priority = MessagePriority.MSG_PRIORITY_LOW,
                            audit_name   = self.name)
                self.orchestrator.dispatch_msg(m)

                # Drop the message.
                return False

            #
            #
            # XXX TODO: extract the domain names here
            #
            #

        # Send the message to the plugins
        self.__expecting_ack += self.__notifier.notify(message)
        return True


    #----------------------------------------------------------------------
    def generate_reports(self):
        """
        Start the generation of all the requested reports for the audit.
        """
        if self.__is_report_started:
            raise RuntimeError("Why are you asking for the report twice?")
        self.__is_report_started = True
        self.__expecting_ack += self.__report_manager.generate_reports(self.__notifier)


    #----------------------------------------------------------------------
    def close(self):
        """
        Release all resources held by this audit.
        """
        try:
            self.database.compact()
        finally:
            self.database.close()
