#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Author: Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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

from ..main.commonstructures import GlobalParams
from .priscillapluginmanager import PriscillaPluginManager
from ..messaging.notifier import AuditNotifier
from ..messaging.message import Message
from ..database.resultdb import ResultDB
from ..api.results.information.url import Url
from ..api.results.result import Result

from multiprocessing import Queue
from datetime import datetime

__all__ = ["AuditManager", "Audit"]


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

        :param config: Configuration object
        :type config: GlobalParams
        """

        # Init audits dicts
        self.__audits = dict()

        # Init params
        self.__orchestrator = orchestrator


    @property
    def orchestrator(self):
        return self.__orchestrator


    #----------------------------------------------------------------------
    def new_audit(self, globalParams):
        """
        Creates a new audit.

        :param globalParams: Params of audit
        :type globalParams: GlobalParams

        :returns: Audit -- return just created audit

        :raises: TypeError
        """
        if not isinstance(globalParams, GlobalParams):
            raise TypeError("globalParams must be an instance of GlobalParams")

        # Create the audit
        m_audit = Audit(globalParams, self.__orchestrator)

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
        del self.__audits[auditName]


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
        if message.message_type == Message.MSG_TYPE_INFO:
            if not message.audit_name:
                raise ValueError("Info message with no target audit!")
            return self.get_audit(message.audit_name).send_msg(message)

        # Process control messages
        elif message.message_type == Message.MSG_TYPE_CONTROL:

            # Send ACKs to their target audit
            if message.message_code == Message.MSG_CONTROL_ACK:
                if message.audit_name:
                    audit = self.get_audit(message.audit_name)
                    audit.acknowledge()

                    # Check for audit termination.
                    #
                    # NOTE: This code assumes messages always arrive in order,
                    #       and ACKs are always sent AFTER responses from plugins.
                    #
                    if not audit.expecting_ack:
                        m = Message(message_type = Message.MSG_TYPE_CONTROL,
                                    message_code = Message.MSG_CONTROL_STOP_AUDIT,
                                    message_info = True,   # True for finished, False for user cancel
                                    audit_name   = message.audit_name)
                        self.__orchestrator.dispatch_msg(m)

            # Stop an audit if requested
            elif message.message_code == Message.MSG_CONTROL_STOP_AUDIT:
                if not message.audit_name:
                    raise ValueError("I don't know which audit to stop...")
                self.get_audit(message.audit_name).stop()
                self.remove_audit(message.audit_name)

            # TODO: pause and resume audits, start new audits

        return True


    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop all audits.
        """
        for a in self.__audits.values(): # not itervalues, may be modified
            a.stop()



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

        :param auditParams: global params for an audit execution
        :type auditParams: GlobalParams
        """

        if not isinstance(auditParams, GlobalParams):
            raise TypeError("Expected GlobalParams, got %s instead" % type(auditParams))

        # set audit params
        self.__audit_params = auditParams

        # set Receiver
        self.__orchestrator = orchestrator

        # set audit name
        self.__auditname = self.__audit_params.audit_name
        if not self.__auditname:
            self.__auditname = self.__generateAuditName()

        # Create the notifier
        self.__notifier = AuditNotifier(self)

        # create result db
        self.__database = ResultDB(self.__auditname, auditParams.audit_db)


    @property
    def name(self):
        return self.__auditname

    @property
    def orchestrator(self):
        return self.__orchestrator

    @property
    def params(self):
        return self.__audit_params

    @property
    def database(self):
        return self.__database


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
        m_audit_plugins = PriscillaPluginManager().load_plugins(self.__audit_params.plugins, "testing")

        # Register plugins with the notifier
        for l_plugin in m_audit_plugins.itervalues():
            self.__notifier.add_plugin(l_plugin)

        # Send a message to the orchestrator for each target URL
        # FIXME: this should not be done here!
        for url in self.__audit_params.targets:
            message = Message(message_info = Url(url),
                              message_type = Message.MSG_TYPE_INFO,
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
    def send_msg(self, message):
        """
        Send messages to the plugins of this audit.

        :param message: The message to send.
        :type message: Message

        :returns: bool - True if the message was sent, False if it was dropped
        """
        if not isinstance(message, Message):
            raise TypeError("Expected Message, got %s instead" % type(message))

        # Is it a result?
        if message.message_type == Message.MSG_TYPE_INFO:

            # Drop duplicate results
            if message.message_info in self.__database:
                self.__expecting_ack += 1
                m = Message(message_type = Message.MSG_TYPE_CONTROL,
                            message_code = Message.MSG_CONTROL_ACK,
                            audit_name   = self.name)
                self.orchestrator.dispatch_msg(m)
                return False

            # Add new results to the database
            self.__database.add(message.message_info)

        # Send the message to the plugins
        self.__expecting_ack += self.__notifier.notify(message)
        return True


    #----------------------------------------------------------------------
    def stop(self):
        """
        Stop audit.
        """
        #
        #
        # XXX TODO
        #
        #
        self.__database.close()
