# Fix the module path for the tests.
import sys
import os
from os import path
try:
	_FIXED_PATH_
except NameError:
	here = path.split(path.abspath(__file__))[0]
	if not here:  # if it fails use cwd instead
		here = path.abspath(os.getcwd())
	golismero = path.join(here, "..")
	thirdparty_libs = path.join(golismero, "thirdparty_libs")
	if path.exists(thirdparty_libs):
		sys.path.insert(0, thirdparty_libs)
		sys.path.insert(0, golismero)
	_FIXED_PATH_ = True


# Imports
from golismero.api.net.dns import *
from golismero.api.data.information.dns import *

def test_registers():

	d = Dns()
	cname = d.resolve("www.terra.es", "CNAME")

	for c in cname:
		t = d.get_ips(c)
		if c.type == "CNAME":
			print c.target

		for kk in t:
			print kk.address

	a = d.get_aaaa("www.google.es")
	for t in a:
		if t.type == "AAAA":
			print t.address


if __name__ == "__main__":
	test_registers()