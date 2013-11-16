#!/usr/bin/env python
# -*- coding: utf-8 -*-

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com
  Raul Requero | rareq1987<@>gmail.com

Golismero project site: https://github.com/golismero
Golismero project mail: golismero.project<@>gmail.com

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

from golismero.api.audit import start_audit, stop_audit, \
     get_audit_names, get_audit_count, get_audit_config, \
     get_audit_stats, get_audit_log_lines, get_audit_scope
from golismero.api.data import Data
from golismero.api.data.resource import Resource
from golismero.api.data.db import Database
from golismero.api.config import Config, get_orchestrator_config
from golismero.api.logger import Logger
from golismero.api.plugin import UIPlugin, get_plugin_info, get_plugin_ids, \
     get_stage_display_name
from golismero.common import AuditConfig
from golismero.managers.processmanager import PluginContext
from golismero.messaging.codes import MessageType, MessageCode, \
     MessagePriority

import collections
import functools
import threading
import traceback
import warnings

# Import the XML-RPC <-> GoLismero bridge.
from imp import load_source
from os.path import abspath, join, split
server_bridge = load_source(
    "server_bridge",
    abspath(join(split(__file__)[0], "server_bridge.py"))
)


#------------------------------------------------------------------------------
class SwitchToAudit(object):
    """
    Context manager that allows UI plugins to run API calls as if they came
    from within an audit. This is useful, for example, to have access to the
    audit database APIs.

    Example::
        >>> from golismero.api.data.db import Database
        >>> with SwitchToAudit("my_audit"):
        ...     data_ids = Database.keys()
        ...     print "Ok!"
        ...
        Ok!
        >>> try:
        ...     Database.keys()
        ... except Exception:
        ...     print "Error!"
        ...
        Error!
    """

    def __init__(self, audit_name):
        self.audit_name = audit_name

    def __enter__(self):

        # Keep the original execution context.
        self.old_context = Config._context

        # Update the execution context for this audit.
        Config._context = PluginContext(
                   msg_queue = self.old_context.msg_queue,
                  audit_name = self.audit_name,
                audit_config = get_audit_config(self.audit_name),
                 audit_scope = get_audit_scope(self.audit_name),
            orchestrator_pid = self.old_context._orchestrator_pid,
            orchestrator_tid = self.old_context._orchestrator_tid)

    def __exit__(self, *args, **kwargs):

        # Restore the original execution context.
        Config._context = self.old_context


#------------------------------------------------------------------------------
class WebUIPlugin(UIPlugin):
    """
    Web UI plugin.
    """

    # This is where the Bridge will be stored on instances.
    bridge = None


    #--------------------------------------------------------------------------
    def __init__(self):

        # audit_name -> plugin_name -> ack_identity -> simple_id
        self.current_plugins = collections.defaultdict(
            functools.partial(collections.defaultdict, dict) )


    #--------------------------------------------------------------------------
    def check_params(self, options, *audits):
        pass


    #--------------------------------------------------------------------------
    def get_accepted_info(self):
        "This method tells the Orchestrator we don't want to receive any Data."
        return []


    #--------------------------------------------------------------------------
    def recv_info(self, info):
        "This method won't be called, because we don't receive any Data."
        pass


    #--------------------------------------------------------------------------
    def recv_msg(self, message):
        """
        This method receives messages from the Orchestrator, parses them, and
        calls the appropriate notification methods defined below.

        :param message: Message received from the Orchestrator.
        :type message: Message
        """
        print message
        # Control messages.
        if message.message_type == MessageType.MSG_TYPE_CONTROL:

            # This UI plugin must be started.
            if message.message_code == MessageCode.MSG_CONTROL_START_UI:
                self.start_ui()

            # This UI plugin must be shut down.
            elif message.message_code == MessageCode.MSG_CONTROL_STOP_UI:
                self.stop_ui()

            # An audit has started.
            elif message.message_code == MessageCode.MSG_CONTROL_START_AUDIT:
                self.notify_stage(message.audit_name, "start")

            # An audit has finished.
            elif message.message_code == MessageCode.MSG_CONTROL_STOP_AUDIT:
                try:
                    del self.current_plugins[Config.audit_name]
                except KeyError:
                    pass
                self.notify_stage(message.audit_name,
                            "finish" if message.message_info else "cancel")

            # A plugin has sent a log message.
            elif message.message_code == MessageCode.MSG_CONTROL_LOG:
                (text, level, is_error) = message.message_info
                if is_error:
                    self.notify_error(
                        message.audit_name, message.plugin_id,
                        message.ack_identity, text, level)
                else:
                    self.notify_log(
                        message.audit_name, message.plugin_id,
                        message.ack_identity, text, level)

            # A plugin has sent an error message.
            elif message.message_code == MessageCode.MSG_CONTROL_ERROR:
                (description, tb) = message.message_info
                text = "Error: " + description
                self.notify_error(
                    message.audit_name, message.plugin_id,
                    message.ack_identity, text, Logger.STANDARD)
                text = "Exception raised: %s\n%s" % (description, tb)
                self.notify_error(
                    message.audit_name, message.plugin_id,
                    message.ack_identity, text,
                    Logger.MORE_VERBOSE)

            # A plugin has sent a warning message.
            elif message.message_code == MessageCode.MSG_CONTROL_WARNING:
                for w in message.message_info:
                    formatted = warnings.formatwarning(
                        w.message, w.category, w.filename, w.lineno, w.line)
                    text = "Warning: " + str(w.message)
                    self.notify_warning(
                        message.audit_name, message.plugin_id,
                        message.ack_identity, text,
                        Logger.STANDARD)
                    text = "Warning details: " + formatted
                    self.notify_warning(
                        message.audit_name, message.plugin_id,
                        message.ack_identity, text,
                        Logger.MORE_VERBOSE)

        # Status messages.
        elif message.message_type == MessageType.MSG_TYPE_STATUS:

            # A plugin has started processing a Data object.
            if message.message_code == MessageCode.MSG_STATUS_PLUGIN_BEGIN:

                # Create a simple ID for the plugin execution.
                aud_dict  = self.current_plugins[message.audit_name]
                id_dict   = aud_dict[message.plugin_id]
                simple_id = len(id_dict)
                id_dict[message.ack_identity] = simple_id

                # Call the notification method.
                self.notify_progress(
                    message.audit_name, message.plugin_id,
                    message.ack_identity, 0.0)

            # A plugin has finished processing a Data object.
            elif message.message_code == MessageCode.MSG_STATUS_PLUGIN_END:

                # Call the notification method.
                self.notify_progress(
                    message.audit_name, message.plugin_id,
                    message.ack_identity, 100.0)

                # Free the simple ID for the plugin execution.
                del self.current_plugins[message.audit_name]\
                                        [message.plugin_id]\
                                        [message.ack_identity]

            # A plugin is currently processing a Data object.
            elif message.message_code == MessageCode.MSG_STATUS_PLUGIN_STEP:
                self.notify_progress(
                    message.audit_name, message.plugin_id,
                    message.ack_identity, message.message_info)

            # An audit has switched to another execution stage.
            elif message.message_code == MessageCode.MSG_STATUS_STAGE_UPDATE:
                self.notify_stage(message.audit_name, message.message_info)


    #--------------------------------------------------------------------------
    def get_plugin_name(self, audit_name, plugin_id, identity):
        """
        Helper method to get a user-friendly name
        for the plugin that sent a given message.

        :param audit_name: Name of the audit.
        :type audit_name: str | None

        :param plugin_id: ID of the plugin.
        :type plugin_id: str | None

        :param identity: Identity hash of the Data object being processed.
        :type identity: str | None

        :returns: User-friendly name for the plugin.
        :rtype: str
        """

        # If the message comes from the Orchestrator.
        if not plugin_id:
            return "GoLismero"

        # If the message is for us, just return our name.
        if plugin_id == Config.plugin_id:
            return Config.plugin_info.display_name

        # Get the plugin display name.
        plugin_name = get_plugin_info(plugin_id).display_name

        # Append the simple ID if it's greater than zero.
        if identity:
            simple_id = self.current_plugins[audit_name][plugin_id][identity]
            if simple_id:
                plugin_name = "%s (%d)" % (plugin_name, simple_id + 1)

        # Return the display name.
        return plugin_name


    #--------------------------------------------------------------------------
    def start_ui(self):
        """
        This method is called when the UI start message arrives.
        It reads the plugin configuration, starts the consumer thread, and
        launches the XML-RPC server.
        """

        # Log the event.
        print "Starting XML-RPC server..."

        # Initialize the audit and plugin state caches.
        self.state_lock   = threading.RLock()
        self.steps        = collections.Counter() # Count number of stage "recon" was reached
        self.audit_state  = {}  # audit -> stage
        self.plugin_state = collections.defaultdict(
            functools.partial(collections.defaultdict, dict)
            )  # audit -> (plugin, identity) -> progress

        # Create the consumer thread object.
        self.thread_continue = True
        self.thread = threading.Thread(
            target = self.consumer_thread,
            kwargs = {"context" : Config._context}
        )
        self.thread.daemon = True

        # Get the configuration.
        orchestrator_config = get_orchestrator_config().to_dictionary()
        plugin_config       = Config.plugin_config
        plugin_extra_config = Config.plugin_extra_config

        # Launch the XML-RPC server.
        self.bridge = server_bridge.launch_server(
            orchestrator_config, plugin_config, plugin_extra_config)

        # Start the consumer thread.
        self.thread.start()


    #--------------------------------------------------------------------------
    def stop_ui(self):
        """
        This method is called when the UI stop message arrives.
        It shuts down the web UI.
        """

        # Log the event.
        print "Stopping XML-RPC server..."

        # Tell the consumer thread to stop.
        self.thread_continue = False

        # Tell the server to stop.
        try:
            if self.bridge:
                self.bridge.send( ("stop",) )
        except:
            pass

        # Shut down the communication pipe.
        # This should wake up the consumer thread.
        if self.bridge:
            self.bridge.close()

        # Wait for the consumer thread to stop.
        if self.thread.isAlive():
            self.thread.join(2.0)

        # If a timeout occurs...
        if self.thread.isAlive():

            # Forcefully kill the thread. Ignore errors.
            # http://stackoverflow.com/a/15274929/426293
            import ctypes
            exc = ctypes.py_object(KeyboardInterrupt)
            res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.thread.ident), exc)
            if res > 1:
                ctypes.pythonapi.PyThreadState_SetAsyncExc(
                    ctypes.c_long(self.thread.ident), None)

            # Wait again.
            try:
                self.thread.join(2.0)
            except:
                pass

        # Clear the state cache.
        self.state_lock = threading.RLock()
        self.audit_state.clear()
        self.plugin_state.clear()


    #--------------------------------------------------------------------------
    def consumer_thread(self, context):
        """
        This method implements the consumer thread code: it reads data sent by
        the XML-RPC server though a pipe, and sends the appropriate messages to
        the Orchestrator.
        """

        try:

            # Initialize the plugin execution context.
            Config._context = context

            # Loop until they tell us to quit.
            while self.thread_continue:

                # Read the next packet from the pipe.
                packet = self.bridge.recv()

                # Success responses start with "ok",
                # failure responses start with "fail".
                response = ("ok",)

                try:

                    # The first field is always the command.
                    # The rest are the arguments.
                    command   = packet[0]
                    arguments = packet[1:]

                    # Special command "fail" means the server died.
                    if command == "fail":

                        # Stop GoLismero.
                        self.do_admin_service_stop()

                        # Kill the consumer thread.
                        break

                    # Parse the command to get the method name.
                    # The command is the path to the webservice.
                    method_name = command
                    while "//" in method_name:
                        method_name = method_name.replace("//", "/")
                    if method_name.startswith("/"):
                        method_name = method_name[1:]
                    if method_name.endswith("/"):
                        method_name = method_name[:-1]
                    method_name = "do_" + method_name.replace("/", "_")

                    # Get the method that implements the command.
                    # Fail if it doesn't exist.
                    try:
                        method = getattr(self, method_name)
                    except AttributeError:
                        raise NotImplementedError(
                            "Command not implemented: %s" % command)

                    # Run the command and get the response.
                    retval   = method( *arguments )
                    response = ("ok", retval)

                # On error send an failure response.
                except Exception, e:
                    msg = str(e) + "\n" + traceback.format_exc()
                    self.bridge.send( ("fail", msg) )
                    continue

                # On success send the response.
                self.bridge.send(response)

        # This catch prevents exceptions from being shown in stderr.
        except:
            ##raise # XXX DEBUG
            pass


    #--------------------------------------------------------------------------
    #
    # Notification methods
    # ====================
    #
    # They run in the context of the main thread, invoked from recv_msg().
    #
    #--------------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def notify_log(self, audit_name, plugin_id, identity, text, level):
        """
        This method is called when a plugin sends a log message.

        :param audit_name: Name of the audit.
        :type audit_name: str | None

        :param plugin_id: ID of the plugin.
        :type plugin_id: str | None

        :param identity: Identity hash of the Data object being processed.
        :type identity: str | None

        :param text: Log text.
        :type text: str

        :param level: Log level (0 through 3).
        :type level: int
        """

        # Log the event.
        plugin_name = self.get_plugin_name(audit_name, plugin_id, identity)
        print "[%s - %s] %s" % (audit_name, plugin_name, text)

        # Send the packet.
        packet = ("log", audit_name, plugin_id, identity, text, level)
        self.bridge.send(packet)


    #--------------------------------------------------------------------------
    def notify_error(self, audit_name, plugin_id, identity, text, level):
        """
        This method is called when a plugin sends an error message.

        :param audit_name: Name of the audit.
        :type audit_name: str | None

        :param plugin_id: ID of the plugin.
        :type plugin_id: str | None

        :param identity: Identity hash of the Data object being processed.
        :type identity: str | None

        :param text: Log text.
        :type text: str

        :param level: Log level (0 through 3).
        :type level: int
        """

        # Log the event.
        plugin_name = self.get_plugin_name(audit_name, plugin_id, identity)
        print "[%s - %s] %s" % (audit_name, plugin_name, text)

        # Send the packet.
        packet = ("error", audit_name, plugin_id, identity, text, level)
        self.bridge.send(packet)


    #--------------------------------------------------------------------------
    def notify_warning(self, audit_name, plugin_id, identity, text, level):
        """
        This method is called when a plugin sends a warning message.

        :param audit_name: Name of the audit.
        :type audit_name: str | None

        :param plugin_id: ID of the plugin.
        :type plugin_id: str | None

        :param identity: Identity hash of the Data object being processed.
        :type identity: str | None

        :param text: Log text.
        :type text: str

        :param level: Log level (0 through 3).
        :type level: int
        """

        # Log the event.
        plugin_name = self.get_plugin_name(audit_name, plugin_id, identity)
        print "[%s - %s] %s" % (audit_name, plugin_name, text)

        # Send the packet.
        packet = ("warn", audit_name, plugin_id, identity, text, level)
        self.bridge.send(packet)


    #--------------------------------------------------------------------------
    def notify_progress(self, audit_name, plugin_id, identity, progress):
        """
        This method is called when a plugin sends a status update.

        :param audit_name: Name of the audit.
        :type audit_name: str | None

        :param plugin_id: ID of the plugin.
        :type plugin_id: str | None

        :param identity: Identity hash of the Data object being processed.
        :type identity: str | None

        :param progress: Progress percentage (0.0 through 100.0).
        :type progress: float
        """

        # Log the event.
        plugin_name = self.get_plugin_name(audit_name, plugin_id, identity)
        if progress is not None:
            progress_h = int(progress)
            progress_l = int((progress - float(progress_h)) * 100)
            text = "%i.%.2i%% percent done..." % (progress_h, progress_l)
        else:
            text = "Working..."
        print "[%s - %s] %s" % (audit_name, plugin_name, text)

        # Save the plugin state.
        self.plugin_state[audit_name][(plugin_id, identity)] = progress

        # Send the plugin state.
        packet = ("progress", audit_name, plugin_id, identity, progress)
        self.bridge.send(packet)


    #--------------------------------------------------------------------------
    def notify_stage(self, audit_name, stage):
        """
        This method is called when an audit moves to another execution stage.

        :param audit_name: Name of the audit.
        :type audit_name: str

        :param stage: Name of the execution stage.
            Must be one of the following:
             - "start" - The audit has just started.
             - "import" - Importing external data into the database.
             - "recon" - Performing reconnaisance on the targets.
             - "scan" - Scanning the targets for vulnerabilities.
             - "attack" - Attacking the target using the vulnerabilities found.
             - "intrude" - Gathering information after a successful attack.
             - "cleanup" - Cleaning up after an attack.
             - "report" - Generating a report for the audit.
             - "finish" - The audit has finished.
             - "cancel" - The audit has been canceled by the user.
        :type stage: str
        """

        # Log the event.
        print "[%s] Entering stage: %s" % (audit_name,
                                           get_stage_display_name(stage))

        # Save the audit state.
        self.audit_state[audit_name] = stage

        # Increase steps if recon stage was reached
        if stage == "recon":
            self.steps[audit_name] += 1

        # Send the audit state.
        packet = ("stage", audit_name, stage)
        self.bridge.send(packet)


    #--------------------------------------------------------------------------
    #
    # Command methods
    # ===============
    #
    # They run in background, invoked by consumer_thread().
    #
    #--------------------------------------------------------------------------


    #--------------------------------------------------------------------------
    #
    # Audit methods
    #
    #--------------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def do_audit_create(self, audit_config):
        """
        Implementation of: /scan/create

        :param audit_config: Audit configuration.
        :type audit_config: dict(str -> \\*)
        """


        # Load the audit configuration from the dictionary.
        o_audit_config = AuditConfig()
        o_audit_config.from_dictionary(audit_config)

        # Create the new audit.
        start_audit(o_audit_config)


    #--------------------------------------------------------------------------
    def do_audit_cancel(self, audit_name):
        """
        Implementation of: /scan/cancel

        :param audit_name: Name of the audit to cancel.
        :type audit_name: str
        """

        # Stop the audit.
        stop_audit(audit_name)


    #--------------------------------------------------------------------------
    def do_audit_list(self):
        """
        Implementation of: /scan/list

        :returns: Dictionary mapping audit names to their configurations.
        :rtype: dict(str -> dict(str -> \\*))
        """
        result = {}
        for audit_name in get_audit_names():
            audit_config = get_audit_config(audit_name)
            result[audit_name] = audit_config.to_dictionary()
        return result


    #--------------------------------------------------------------------------
    def do_audit_state(self, audit_name):
        """
        Implementation of: /scan/state

        Returns a tuple with the following format::
          (
            'STEPS' # Count number that "recon" stage was reached
            'STAGE_NAME',
            (
              (PLUGIN_NAME::str, IDENTITY::int, PROGRESS::float(0.0-100.0)),
            )
          )

        :param audit_name: Name of the audit to query.
        :type audit_name: str

        :returns: Current audit stage, followed by the progress status of
            every plugin (plugin name, data identity, progress percentage).
        :rtype: tuple(int, tuple( tuple(str, str, float) ... ))
        """

        # Return the current stage and the status of every plugin.
        r = None
        try:
            r = (
                self.steps[audit_name],
                self.audit_state[audit_name],
                tuple(
                    (plugin_name, identity, progress)
                    for ((plugin_name, identity), progress)
                    in self.plugin_state[audit_name].iteritems()
                )
            )
        except Exception,e:
            pass

        return r


    #--------------------------------------------------------------------------
    def do_audit_results(self, audit_name, data_type = "all"):
        """
        Implementation of: /scan/results

        :param audit_name: Name of the audit to query.
        :type audit_name: str

        :param data_type: Data type to request. Case insensitive.
            Must be one of the following values:
             - "all": All data types.
             - "information": Information type.
             - "resource": Resource type.
             - "vulnerability": Vulnerability type.
        :type data_type: str

        :returns: Result IDs.
        :rtype: list(str)

        :raises KeyError: Data type unknown.
        """
        with SwitchToAudit(audit_name):
            i_data_type = {
                "all": None,
                "information": Data.TYPE_INFORMATION,
                "resource": Data.TYPE_RESOURCE,
                "vulnerability": Data.TYPE_VULNERABILITY,
                }[data_type.strip().lower()]
            return sorted( Database.keys(i_data_type) )


    #--------------------------------------------------------------------------
    def do_audit_details(self, audit_name, id_list):
        """
        Implementation of: /scan/details

        :param audit_name: Name of the audit to query.
        :type audit_name: str

        :param id_list: List of result IDs.
        :type id_list: list(str)
        """
        with SwitchToAudit(audit_name):
            return Database.get_many(id_list)


    #----------------------------------------------------------------------
    def do_audit_summary(self, audit_name):
        """
        Get results summary for an audit.

        :param audit_name: Name of the audit to query.
        :type audit_name: str

        :returns: return dict as format:
        {
        'vulns_number'            : int,
        'discovered_hosts'        : int,
        'total_hosts'             : int,
        'vulns_by_level'          : {
        'info'     : int,
        'low'      : int,
        'medium'   : int,
        'high'     : int,
        'critical' : int,
        }
        :rtype: dict
        """
        with SwitchToAudit(audit_name):

            # Get vulns
            tmp_vulns = Database.keys(data_type=Data.TYPE_VULNERABILITY)

            # Get each type of vuln level
            vulns_counter = collections.Counter()
            for l_vuln in tmp_vulns:
                vulns_counter[l_vuln.level] += 1

            # Get discovered host
            discovered_hosts = 0
            discovered_hosts += len(Database.keys(data_type=Data.TYPE_RESOURCE, data_subtype=Resource.RESOURCE_DOMAIN))
            discovered_hosts += len(Database.keys(data_type=Data.TYPE_RESOURCE, data_subtype=Resource.RESOURCE_IP))

            # Get audit targets number
            total_hosts       = len(AuditConfig.targets)

            #
            # Make the response
            return {
                'vulns_number'            : len(tmp_vulns),
                'discovered_hosts'        : discovered_hosts,
                'total_hosts'             : total_hosts,
                'vulns_by_level'          : {
                    'info'     : vulns_counter['info'],
                    'low'      : vulns_counter['low'],
                    'medium'   : vulns_counter['medium'],
                    'high'     : vulns_counter['high'],
                    'critical' : vulns_counter['critical']
                }
            }


    #----------------------------------------------------------------------
    def do_audit_log(self, audit_name):
        """

        :param audit_name: Name of the audit to query.
        :type audit_name: str

        :returns: List of tuples.
            Each tuple contains the following elements:
             - Plugin ID.
             - Data object ID (plugin instance).
             - Log line text. May contain newline characters.
             - Log level.
             - True if the message is an error, False otherwise.
             - Timestamp.
        :rtype: list( tuple(str, str, str, int, bool, float) )
        """
        return get_audit_log_lines(audit_name)


    #--------------------------------------------------------------------------
    #
    # Plugin methods
    #
    #--------------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def do_plugin_list(self):
        """
        Implementation of: /plugin/list

        :returns: List of plugin names.
        :rtype: list(str)
        """
        return sorted( get_plugin_ids() )


    #--------------------------------------------------------------------------
    def do_plugin_details(self, plugin_id):
        """
        Implementation of: /plugin/details

        :param plugin_id: ID of the plugin to query.
        :type plugin_id: str

        :returns: Plugin information.
        :rtype: PluginInfo
        """
        return get_plugin_info(plugin_id)    # XXX TODO encode as JSON


    #----------------------------------------------------------------------
    #
    # Management methods
    #
    #----------------------------------------------------------------------


    #--------------------------------------------------------------------------
    def do_admin_service_stop(self):
        """
        Implementation of: /admin/service/stop
        """
        Config._context.send_msg(
            message_type = MessageType.MSG_TYPE_CONTROL,
            message_code = MessageCode.MSG_CONTROL_STOP,
            message_info = False,    # True for finished, False for user cancel
            priority = MessagePriority.MSG_PRIORITY_LOW
        )


    #--------------------------------------------------------------------------
    def do_admin_config_details(self):
        """
        Implementation of: /admin/config/details

        :returns: Orchestrator configuration.
        :rtype: dict(str -> \\*)
        """
        return get_orchestrator_config().to_dictionary()