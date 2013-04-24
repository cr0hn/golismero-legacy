#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__="""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn@cr0hn.com
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
from ..api.data.resource.resource import Resource
from ..api.data.resource.url import Url
from ..api.data.resource.domain import Domain
from ..common import AuditConfig
from ..database.auditdb import AuditDB
from ..managers.reportmanager import ReportManager
from ..messaging.codes import MessageType, MessageCode, MessagePriority
from ..messaging.message import Message
from ..messaging.notifier import AuditNotifier

from datetime import datetime
from multiprocessing import Queue
from collections import Counter


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

        # Create the dictionary where we'll store the Audit objects.
        self.__audits = dict()

        # Keep a reference to the Orchestrator.
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
        m_audit = Audit(params, self.orchestrator)

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
        try:
            self.orchestrator.netManager.release_all_slots(auditName)
        finally:
            try:
                audit = self.__audits[auditName]
                try:
                    audit.close()
                finally:
                    del self.__audits[auditName]
            finally:
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
                    audit.acknowledge(message)

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
                            self.__orchestrator.enqueue_msg(m)

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
        self.__database = AuditDB(self.__name, auditParams.audit_db)

        # Maximum number of links to follow.
        self.__followed_links = 0
        self.__show_max_links_warning = True


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
        Get a default name for an audit.

        :returns: str -- generated name for the audit.
        """
        return "golismero-" + datetime.now().strftime("%Y-%m-%d-%H_%M_%S")


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
        self.__notifier.add_multiple_plugins(m_audit_plugins)

        # Send a message to the orchestrator for each target URL
        for url in self.params.targets:
            self.send_info(Url(url))


    #----------------------------------------------------------------------
    def send_info(self, data):
        """
        Send data to the orchestrator.

        :param data: Data to send
        :type data: Data
        """
        return self.send_msg(message_type = MessageType.MSG_TYPE_DATA,
                             message_info = [data])


    #----------------------------------------------------------------------
    def send_msg(self, message_type = MessageType.MSG_TYPE_DATA,
                       message_code = 0,
                       message_info = None,
                       priority = MessagePriority.MSG_PRIORITY_MEDIUM):
        """
        Send messages to the orchestrator.

        :param message_type: specifies the type of message.
        :type mesage_type: int -- specified in a constant of Message class.

        :param message_code: specifies the code of message.
        :type message_code: int -- specified in a constant of Message class.

        :param message_info: the payload of the message.
        :type message_info: object -- type must be resolved at run time.
        """
        m = Message(message_type = message_type,
                    message_code = message_code,
                    message_info = message_info,
                      audit_name = self.name,
                        priority = priority)
        self.orchestrator.enqueue_msg(m)


    #----------------------------------------------------------------------
    def acknowledge(self, message):
        """
        Got an ACK for a message sent from this audit to the plugins.

        :param message: The message with the ACK.
        :type message: Message
        """

        # Decrease the expected ACK count.
        # The audit manager will check when this reaches zero.
        self.__expecting_ack -= 1

        # Tell the notifier about this ACK.
        self.__notifier.acknowledge(message)


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

            # Here we'll store the data to be resent to the plugins.
            data_for_plugins = []

            # For each data object sent...
            if isinstance(message.message_info, Data):
                message.message_info = [message.message_info]
            for data in message.message_info:

                # Increase the number of links followed.
                if data.data_type == Data.TYPE_RESOURCE and data.resource_type == Resource.RESOURCE_URL:
                    self.__followed_links += 1

                # Add the data to the database.
                # This automatically merges the data if it already exists.
                is_new = self.database.add_data(data)

                # Is the data new?
                if is_new:

                    # Maximum number of links reached?
                    if self.__params.max_links > 0 and self.__followed_links >= self.__params.max_links:

                        # Show a warning.
                        if self.__show_max_links_warning:
                            self.__show_max_links_warning = False
                            w = "Maximum number of links (%d) reached! Audit: %s"
                            w = w % (self.__params.max_links, self.name)
                            self.send_msg(message_type = MessageType.MSG_TYPE_CONTROL,
                                          message_code = MessageCode.MSG_CONTROL_WARNING,
                                          message_info = (RuntimeWarning(w),))
                    else:

                        # The data will be sent to the plugins.
                        data_for_plugins.append(data)

                        # Process the embedded resources too, if any.
                        for resource in data.discovered_resources:
                            is_new = self.database.add_data(resource)
                            if is_new:
                                data_for_plugins.append(resource)

            # If we have data to be sent...
            if data_for_plugins:

                # Modify the message in-place with the filtered list of data objects.
                message._update_data(data_for_plugins)

                # Send the message to the plugins, and track the expected ACKs.
                self.__expecting_ack += self.__notifier.notify(message)

                # Tell the Orchestrator we sent the message.
                return True

            # If we don't have data to be sent...
            else:

                # Drop the message. An ACK is still expected.
                self.__expecting_ack += 1
                self.send_msg(message_type = MessageType.MSG_TYPE_CONTROL,
                              message_code = MessageCode.MSG_CONTROL_ACK,
                                  priority = MessagePriority.MSG_PRIORITY_LOW)

                # Tell the Orchestrator we dropped the message.
                return False


    #----------------------------------------------------------------------
    def generate_reports(self):
        """
        Start the generation of all the requested reports for the audit.
        """

        # Check if the report generation is already started.
        if self.__is_report_started:
            raise RuntimeError("Why are you asking for the report twice?")

        # An ACK is expected after launching the report plugins.
        self.__expecting_ack += 1
        try:

            # Mark the report generation as started for this audit.
            self.__is_report_started = True

            # Start the report generation.
            self.__expecting_ack += self.__report_manager.generate_reports(self.__notifier)

        # Send the ACK after launching the report plugins.
        finally:
            self.send_msg(message_type = MessageType.MSG_TYPE_CONTROL,
                          message_code = MessageCode.MSG_CONTROL_ACK,
                              priority = MessagePriority.MSG_PRIORITY_LOW)


    #----------------------------------------------------------------------
    def close(self):
        """
        Release all resources held by this audit.
        """
        try:
            self.database.compact()
        finally:
            self.database.close()
