#!/usr/bin/python

# -*- coding: utf-8 -*-
"""
GoLismero 2.0 - The web knife.

Copyright (C) 2011-2013 - Daniel Garcia Garcia a.k.a cr0hn | dani@iniqua.com

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



from core.main.commonstructures import GlobalParams
from core.messaging.interfaces import IReceiver

#--------------------------------------------------------------------------
class Audit(IReceiver):
    """
    Instance of an audit, with their custom parameters, scope, target, plugins, etc.
    """

    #----------------------------------------------------------------------
    def __init__(self, auditParams, receiver):
        """
        :param receiver: Orchester instance that will recives messages sent by audit.
        :type reciber: Orchester

        :param auditParams: global params for an audit execution
        :type auditParams: GlobalParams
        """


        if not isinstance(auditParams, GlobalParams):
            raise("Parameter type of params are not correct.")

        self.__execParams = auditParams

        # set Receiver
        self.__receiver = receiver

        # name
        self.__auditname = self.__execParams.audit_name
        if self.__auditname == "":
            self.__auditname = self.__getAuditName()



    def get_name(self):
        return self.__auditname

    def set_name(self, name):
        self.__auditname = name

    name = property(get_name, set_name)

    #----------------------------------------------------------------------
    def __generateAuditName(self):
        """
        Get a random name for audit

        :returns: str -- generated name for the audit.
        """
        import datetime

        return "golismero-".join(datetime.datetime.now().strftime("%Y-%m-%d-%H_%M"))


    #----------------------------------------------------------------------
    def get_audit_name(self):
        """
        Return the audit name

        :returns: str -- the audit name
        """
        return self.__auditname


    #----------------------------------------------------------------------
    def run(self):
        """
        Start execution of audit
        """
        # 1 - Carga los plugins necesarios
        # 2 - Configura los plugins para ser la receptora de los msg
        # 3 - Crea y configura el notificator.
        # 4 - Asocia los plugins al notificator
        # 5 - Ejecuta los plugins
        self.__execParams.Plugins
        pass

    #----------------------------------------------------------------------
    def recv_msg(self, message):
        """
        Send message to the core system

        :param message: message to send
        :type message:
        """
        self.__receiver.recv_info(message)





#--------------------------------------------------------------------------
class AuditManager:
    """
    Manage and control audits
    """

    #----------------------------------------------------------------------
    def __init__(self):
        """Constructor"""

        # Audits list
        self.__audits = dict()


    #----------------------------------------------------------------------
    def new_audit(self, globalParams):
        """
        Creates a new audit with params passed as parameter

        :param globalParams: Params of audit
        :type globalParams: GlobalParams

        :raises: TypeError
        """
        if not isinstance(globalParams, GlobalParams):
            raise TypeError("globalParams must be an instance of GlobalParams")

        # Create the audit
        m_audit = Audit(globalParams, self)
        # Store it
        self.__audits[m_audit.get_audit_name()] = Audit
        # Run!
        m_audit.run()


    #----------------------------------------------------------------------
    def get_all_audits(self):
        """
        Get the list of audits running at the momento of calling.

        :returns: dicts(str, Audit) -- Return a dict with touples (auditName, Audit instance)
        """
        return self.__audits

    #----------------------------------------------------------------------
    def get_audit(self, auditName):
        """
        Get an instance of audit by their name.

        :param auditName: audit name
        :type auditName: str

        :returns: Audit -- instance of audit
        :raises: TypeError, KeyError
        """
        if not isinstance(auditName, basestring):
            raise TypeError("Audit name must be a string")

        return self.__audits[auditName]


