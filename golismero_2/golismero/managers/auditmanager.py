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
from ..api.data.resource.domain import Domain
from ..api.net.web_utils import parse_url
from ..common import AuditConfig
from ..database.datadb import DataDB
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

        # To follow orphan info and vuln types
        self.__orphan_data_attemps = Counter()
        self.__orphan_data_resources = dict()



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
            message_url    = Message(message_info = Url(url),
                                     message_type = MessageType.MSG_TYPE_DATA,
                                     audit_name   = self.name)
            #message_domain = Message(message_info = Domain(parse_url(url).host),
            #                         message_type = MessageType.MSG_TYPE_DATA,
            #                         audit_name   = self.name)
            self.orchestrator.dispatch_msg(message_url)
            #self.orchestrator.dispatch_msg(message_domain)


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

            # ------------------------------------------------------
            # Algorithm explanation:
            #
            # The structure for information are:
            #
            # Info_type <-----<> Resource <>------> Vuln_type
            #
            # For each type of message data we distinguish if
            # data is an info, resource or vuln.
            #
            # If type of data is vuln or info, we search if the
            # associated resource is already stored:
            #
            # - If not: put the info in queue until resource arrives.
            #
            # - Is stored: search in the database and extract the
            #              resource associated and add the new info.
            #
            # ------------------------------------------------------



            m_msg_data = message.message_info
            m_msg_type = m_msg_data.data_type
            m_is_new   = False # var to control if received data is new in database

            # Checks if data has associated a resource
            if (m_msg_type == Data.TYPE_INFORMATION or \
                m_msg_type == Data.TYPE_VULNERABILITY) and \
                not m_msg_data.associated_resource:
                raise ValueError("Vulnerability o Information types must have a resource associated. Error data: '%s'" % str(m_msg_data))


            # Add the data to the database
            m_is_new = self.database.add(m_msg_data)
            #print "### " + str(m_msg_data) + " | " + str(m_is_new)

            # Data is new in database
            if m_is_new:
                #
                # Differenciate the type of data:
                #
                # Type: INFORMATION or VULNERABILITY
                if m_msg_type == Data.TYPE_INFORMATION or \
                   m_msg_type == Data.TYPE_VULNERABILITY:

                    # Search in database for the associated resource
                    m_tmp_resource = self.database.get(m_msg_data.associated_resource)

                    if not m_tmp_resource:
                        # Associated resource not found -> add as orphan data
                        self.__orphan_data_attemps[m_msg_data.identity] += 1
                        self.__orphan_data_resources[m_msg_data.identity] = m_msg_data.associated_resource
                    else:
                        # Update resource
                        self.__update_resource(m_msg_type, m_tmp_resource, m_msg_data)

                # When a resource arrives check if some of orphan data can be associted with them
                elif m_msg_type == Data.TYPE_RESOURCE:

                    # Check associated resource of any orphan data matches with received resource
                    for l_info, l_resource in self.__orphan_data_resources.iteritems():
                        if l_resource == m_msg_data.identity:
                            self.__update_resource(m_msg_type, m_msg_data, l_info)
                            break

                    # Delete old orphan data
                    for l_info, l_attemp in self.__orphan_data_attemps.iteritems():
                        if l_attemp > 5:
                            self.database.remove(l_info)


            # Not new -> is it duplicated data?
            else:

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

        # Send the message to the plugins
        self.__expecting_ack += self.__notifier.notify(message)

        # Look for discovered resources in info:
        #
        if m_msg_data.discovered_resources:
            for l_discovered in m_msg_data.discovered_resources:
                # Check for correct type and also check if resource is already stored
                if l_discovered.data_type == Data.TYPE_RESOURCE and \
                   not self.database.has_key(l_discovered.identity):
                    # Send to orchestrator
                    #print "@@@ " + str(l_discovered)
                    m = Message(message_info = l_discovered,
                                message_type = MessageType.MSG_TYPE_DATA,
                                audit_name   = self.name)
                    self.orchestrator.dispatch_msg(m)

        return True

    #----------------------------------------------------------------------
    def __update_resource(self, msg_type, resource, data):
        """
        Update an associated resource, from database, with a info o vuln type.

        :param msg_type: type of data specified at data
        :type msg_type: int

        :param resource: the resource to update
        :type resource: Resource

        :param data: Information or Vulnerability data
        :type data: Information | Vulnerability
        """
        # Associated resourse found -> add new info or vuln

        # Info or result type?
        m_bind_add = resource.add_information if msg_type == Data.TYPE_INFORMATION else resource.add_vulnerability

        # Add the data
        m_bind_add(data)

        # Add modified resource
        self.database.add(resource)


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
