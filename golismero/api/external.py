#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
External tools API.

Use this module to run external tools and grab their output.
This makes an easy way to integrate GoLismero with any command line tools.
"""

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

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

__all__ = [

    # Run an external tool.
    "run_external_tool",

    # Utility functions.
    "is_executable",
    "get_interpreter",
    "find_binary_in_path",

    # Cygwin utility functions.
    "is_cygwin_binary",
    "get_cygwin_binary",
    "find_cygwin_binary_in_path",
    "win_to_cygwin_path",
    "cygwin_to_win_path",
]

import re
import os
import os.path
import ntpath
import subprocess
import stat
import shlex

# Needed on non-Windows platforms to prevent a syntax error.
if not hasattr(__builtins__, "WindowsError"):
    class WindowsError(OSError): pass

# TODO: Use pexpect to run tools interactively.
# TODO: A callback in run_external_tool() to receive the output line by line.


#------------------------------------------------------------------------------
def run_external_tool(command, args = None, env = None, curdir = None):
    """
    Run an external tool and fetch the output.

    Standard and error output are combined.

    .. warning: SECURITY WARNING: Be *extremely* careful when passing
                data coming from the target servers to this function.
                Failure to properly validate the data may result in
                complete compromise of your machine! See:
                https://www.owasp.org/index.php/Command_Injection

    :param command: Command to execute.
    :type command: str

    :param args: Arguments to be passed to the command.
    :type args: list(str)

    :param env: Environment variables to be passed to the command.
    :type env: dict(str -> str)

    :param curdir: If given, change the current directory to this one while
        running the tool, and switch back to the previous directory when done.
        If not given, run the tool normally.

        This is useful for tools that require you to be standing on a specific
        directory when running them.
    :type curdir: str | None

    :returns: Output from the tool and the exit status code.
    :rtype: tuple(str, int)
    """

    # We put a large and nasty security warning here mostly to scare the noobs,
    # because subprocess is generally safe when you don't run in "shell" mode
    # nor invoke bash directly - i.e. when you know what the hell you're doing.
    #
    # Still, especially on Windows, some external programs are really stupid
    # when it comes to parsing their own command line, so caveat emptor.

    # Make a copy of the command line arguments.
    if not args:
        args = []
    else:
        args = list(args)
        if not command:
            command = args[0]
            del args[0]
        elif args and args[0] == command:
            del args[0]
    if not command:
        raise ValueError("Bad arguments for run_external_tool()")

    # Check if the command is executable.
    if not is_executable(command):

        # Check if the command is a script.
        try:
            interpreter = get_interpreter(command, force = False)
        except IOError:
            interpreter = None
        if interpreter:

            # Prepend the interpreter to the command line.
            command = interpreter[0]
            args = interpreter + args

        # If it's not a script...
        else:

            # Find the target in the path.
            binary_list = find_binary_in_path(command)
            if not binary_list:
                raise IOError("File not found: %r" % command)

            # On Windows, prefer Cygwin binaries over native binaries.
            # Otherwise, just pick the first one in the PATH.
            if os.path.sep == "\\":
                binary = get_cygwin_binary(binary_list)
                if binary:
                    command = binary
                else:
                    command = binary_list[0]
            else:
                command = binary_list[0]

    # Prepend the binary to the command line.
    args.insert(0, command)

    # Turn off DOS path warnings for Cygwin.
    if os.path.sep == "\\":
        if env is None:
            env = os.environ.copy()
        else:
            env = env.copy()
        cygwin = env.get("CYGWIN", "")
        if "nodosfilewarning" not in cygwin:
            if cygwin:
                cygwin += " "
            cygwin += "nodosfilewarning"
        env["CYGWIN"] = cygwin

    # Switch the working directory.
    old_wd = os.getcwd()
    try:
        if curdir:
            os.chdir(curdir)

        # Run the command.
        try:
            code   = 0
            output = subprocess.check_output(args,
                                             executable = command,
                                             env = env)
        except subprocess.CalledProcessError, e:
            code   = e.returncode
            output = e.output
        except WindowsError, e:
            code   = e.winerror
            output = str(e)
            if "%1" in output:
                output = output.replace("%1", command)

    # Restore the working directory.
    finally:
        os.chdir(old_wd)

    # Return the output and the exit code.
    return output, code


#------------------------------------------------------------------------------
def is_executable(binary):
    """
    Tests if the given file exists and is executable.

    :param binary: Path to the binary.
    :type binary: str

    :returns: True if the file exists and is executable, False otherwise.
    :rtype: bool
    """
    return os.path.isfile(binary) and (
        (os.path.sep == "\\" and binary.lower().endswith(".exe")) or
        (os.path.sep == "/" and
         os.stat(binary)[stat.ST_MODE] & stat.S_IXUSR == 0)
    )


#------------------------------------------------------------------------------

# Default interpreter for each script file extension.
DEFAULT_INTERPRETER = {

    ".lua":  ["lua"],
    ".php":  ["php", "-f"],
    ".pl":   ["perl"],
    ".rb":   ["ruby"],
    ".sh":   ["sh", "-c"],
    ".tcl":  ["tcl"],

    ".py":   ["python"],
    ".pyc":  ["python"],
    ".pyo":  ["python"],
    ".pyw":  ["python"],

    ".js":   ["WScript.exe"],
    ".jse":  ["WScript.exe"],
    ".pls":  ["WScript.exe"],
    ".phps": ["WScript.exe"],
    ".pys":  ["WScript.exe"],
    ".rbs":  ["WScript.exe"],
    ".tcls": ["WScript.exe"],
    ".vbs":  ["WScript.exe"],
    ".vbe":  ["WScript.exe"],
    ".wsf":  ["WScript.exe"],
}


#------------------------------------------------------------------------------
def get_interpreter(script, force = False):
    """
    Get the correct interpreter for the given script.

    :param script: Path to the script file.
    :type script: str

    :param force: True to force a result always (defaults to the shell),
        False to only return a result if a valid interpreter was found.
    :type force: bool

    :returns: Command line arguments to replace the script with.
        Normally this will be the path to the interpreter followed
        by the path to the script, but not always.
    :rtype: list(str)
    :raises IOError: An error occurred, the file was not a script, or the
        interpreter was not found and the 'force' argument was set to False.
    """

    # Get the file extension.
    ext = os.path.splitext(script)[1].lower()

    # On Windows...
    if os.path.sep == "\\":

        # EXE files are executable.
        if ext == ".exe":
            binary_list = find_binary_in_path(script)
            if binary_list:
                cygwin = get_cygwin_binary(binary_list)
                if cygwin:
                    return [ cygwin ]
                return [ binary_list[0] ]
            return [ script ]

        # Batch files use cmd.exe.
        if ext in (".bat", ".cmd"):
            return [ os.environ["COMSPEC"], "/C", script ]

    # On Unix, the script may be marked as executable.
    elif is_executable(script):
        return [ script ]

    # Get the name of the default interpreter for each extension.
    interpreter = DEFAULT_INTERPRETER.get(ext, None)
    if interpreter:
        interpreter = list(interpreter) # must be a copy!

        # Add the .exe extension on Windows.
        if os.path.sep == "\\" and not interpreter[0].endswith(".exe"):
            interpreter[0] += ".exe"

        # Look for the interpreter binary on the PATH.
        binary_list = find_binary_in_path(interpreter[0])
        if binary_list:
            cygwin = get_cygwin_binary(binary_list)
            if cygwin:
                interpreter[0] = cygwin
            else:
                interpreter[0] = binary_list[0]

        # Add the script and return it.
        interpreter.append(script)
        return interpreter

    # Try getting the interpreter from the first line of code.
    # This works for scripts that follow the shebang convention.
    # See: https://en.wikipedia.org/wiki/Shebang_(Unix)
    with open(script, "rb") as f:
        signature = f.read(128)
    signature = signature.strip()
    if signature and signature[:1] == "#!":
        signature = signature[1:].split("\n", 1)[0]
        signature = signature.strip()
        args = shlex.split(signature)
        if args:
            if is_executable(args[0]):
                args.append(script)
                return args
            for ext, interpreter in DEFAULT_INTERPRETER.iteritems():
                if re.search("\\b%s\\b" % interpreter[0], args[0]):
                    return interpreter + [script] # must be a copy!

    # If all fails use the shell, but only if 'force' is set to True.
    if not force:
        raise IOError("Interpreter not found for script: %s" % script)
    if os.path.sep == "\\":
        binary_list = find_binary_in_path("bash.exe")
        if binary_list:
            bash = get_cygwin_binary(binary_list)
            if bash:
                return [ bash, "-c", script ]
            return [ binary_list[0], "-c", script ]
        return [ os.environ["COMSPEC"], "/C", script ]
    return [ "/bin/sh", "-c", script ]


#------------------------------------------------------------------------------
def find_binary_in_path(binary):
    """
    Find the given binary in the current environment PATH.

    :param path: Path to the binary.
    :type path: str

    :returns: List of full paths to the binary.
        If not found, the list will be empty.
    :rtype: list(str)
    """

    # Get the filename.
    binary = os.path.abspath(binary)
    binary = os.path.split(binary)[1]

    # On Windows, append the ".exe" extension.
    if os.path.sep == "\\" and not binary.lower().endswith(".exe"):
        binary += ".exe"

    # Look for the file in the PATH.
    found = []
    for candidate in os.environ.get("PATH", "").split(os.path.pathsep):
        candidate = os.path.join(candidate, binary)
        if is_executable(candidate):
            found.append(candidate)

    # Return all instances found.
    return found


#------------------------------------------------------------------------------
def is_cygwin_binary(path):
    """
    Detects if the given binary is located in the Cygwin /bin directory.

    :param path: Windows path to the binary.
    :type path: str

    :returns: True if the binary belongs to Cygwin, False for native binaries.
    :rtype: bool
    """
    path = os.path.abspath(path)
    if not os.path.isdir(path):
        path = os.path.split(path)[0]
    path = os.path.join(path, "cygwin1.dll")
    return os.path.exists(path)


#------------------------------------------------------------------------------
def get_cygwin_binary(binary_list):
    """
    Take the list of binaries returned by find_binary_in_path() and grab the
    one that belongs to Cygwin.

    This is useful for commands or scripts that work different/better on Cygwin
    than the native version (for example the "find" command).

    :param binary_list: List of paths to the binaries to test.
    :type binary_list: str(list)

    :returns: Path to the Cygwin binary, or None if not found.
    :type: str | None
    """
    for binary in binary_list:
        if is_cygwin_binary(binary):
            return binary


#------------------------------------------------------------------------------
def find_cygwin_binary_in_path(binary):
    """
    Find the given binary in the current environment PATH,
    but only if it's the Cygwin version.

    This is useful for commands or scripts that work different/better on Cygwin
    than the native version (for example the "find" command).

    :param path: Path to the binary.
    :type path: str

    :returns: Path to the Cygwin binary, or None if not found.
    :type: str | None
    """
    return get_cygwin_binary( find_binary_in_path(binary) )


#------------------------------------------------------------------------------
def win_to_cygwin_path(path):
    """
    Converts a Windows path to a Cygwin path.

    :param path: Windows path to convert.
        Must be an absolute path.
    :type path: str

    :returns: Cygwin path.
    :rtype: str

    :raises ValueError: Cannot convert the path.
    """
    drive, path = ntpath.splitdrive(path)
    if not drive:
        raise ValueError("Not an absolute path!")
    t = { "\\": "/", "/": "\\/" }
    path = "".join( t.get(c, c) for c in path )
    return "/cygdrive/%s%s" % (drive[0].lower(), path)


#------------------------------------------------------------------------------
def cygwin_to_win_path(path):
    """
    Converts a Cygwin path to a Windows path.
    Only paths starting with "/cygdrive/" can be converted.

    :param path: Cygwin path to convert.
        Must be an absolute path.
    :type path: str

    :returns: Windows path.
    :rtype: str

    :raises ValueError: Cannot convert the path.
    """
    if not path.startswith("/cygdrive/"):
        raise ValueError(
            "Only paths starting with \"/cygdrive/\" can be converted.")
    drive = path[10].upper()
    path = path[11:]
    i = 0
    r = []
    while i < len(path):
        c = path[i]
        if c == "\\":
            r.append( path[i+1:i+2] )
            i += 2
            continue
        if c == "/":
            c = "\\"
        r.append(c)
        i += 1
    path = "".join(r)
    return "%s:%s" % (drive, path)
