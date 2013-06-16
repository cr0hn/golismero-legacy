#!/usr/bin/env python
# Socket test

from platform import uname, system_alias, python_implementation, python_version, architecture
from select import select
from socket import socket, AF_INET, SOCK_STREAM

def print_current_platform():
    (system, node, release, version, machine, processor) = uname()
    bits = architecture()[0]
    alias = "%s %s %s" % system_alias(system, release, version)
    python = "%s %s" % (python_implementation(), python_version())
    print "Using %s (%s) on %s, %s" % (python, bits, alias, machine)

def test_fd_limit():
    print "Testing the maximum number of sockets that can be created..."
    top = 1024 * 1024
    limit = top
    fds = []
    try:
        try:
            while limit > 0:
                fds.append(socket(AF_INET, SOCK_STREAM))
                limit -= 1
        finally:
            for fd in fds:
                try:
                    fd.close()
                except Exception:
                    pass
    except Exception:
        pass
    if limit:
        print "--> Limit found at %d sockets" % (top - limit)
    else:
        print "--> No limit found, stopped trying at %d" % top


def test_select_limit():
    print "Testing the maximum number of sockets that can be selected..."
    top = 1024 * 1024
    limit = top
    fds = []
    try:
        try:
            while limit > 0:
                fds.append(socket(AF_INET, SOCK_STREAM))
                select(fds, fds, fds, 0.1)
                limit -= 1
        finally:
            for fd in fds:
                try:
                    fd.close()
                except Exception:
                    pass
    except Exception:
        pass
    if limit:
        print "--> Limit found at %d sockets" % (top - limit)
    else:
        print "--> No limit found, stopped trying at %d" % top


if __name__ == "__main__":
    print_current_platform()
    test_fd_limit()
    test_select_limit()
