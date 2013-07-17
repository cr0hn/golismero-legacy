#!/usr/bin/python
# -*- coding: utf-8 -*-

# Required since "dns" is both an external module and the name of this file.
from __future__ import absolute_import

__license__ = """
GoLismero 2.0 - The web knife - Copyright (C) 2011-2013

Authors:
  Daniel Garcia Garcia a.k.a cr0hn | cr0hn<@>cr0hn.com
  Mario Vilas | mvilas<@>gmail.com

Golismero project site: http://golismero-project.com
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

__all__ = ["DNS"]

from ..data.information.dns import *

import re
import dns.query
import dns.resolver
import dns.reversename
import socket
from dns.zone import *
from dns.dnssec import algorithm_to_text


#------------------------------------------------------------------------------
#
# DNS
#
#------------------------------------------------------------------------------
#
# This code has been based in the borrowed code from dnsrecon project:
#
# Project site: https://github.com/darkoperator/dnsrecon
#
class DNS(object):

	REQUEST_TIMEOUT = 3.0 # In seconds


	#----------------------------------------------------------------------
	def check_tcp_dns(self, address, dns_port=53):
		"""
		Function to check if a server is listening at port 53 TCP. This will aid
		in IDS/IPS detection since a AXFR will not be tried if port 53 is found to
		be closed.

		:param address: IP or domain name.
		:type address: str

		:param dns_port: port number to connect to the server.
		:type dns_port: int

		:return: True if server accepts TCP connections. False otherwise.
		:rtype: bool
		"""
		if not isinstance(address, basestring):
			raise TypeError("Expected basestring, got '%s'" % type(address))

		if not isinstance(dns_port, int):
			raise TypeError("Expected int, got '%s'" % type(dns_port))
		if dns_port < 1:
			raise ValueError("Port number must be greater than 0.")

		s = socket.socket()
		s.settimeout(DNS_QUERY_TIMEOUT)

		try:
			s.connect((address, dns_port))
		except Exception:
			return False
		else:
			return True
		finally:
			s.close()


	#----------------------------------------------------------------------
	def resolve(self, target, type, nameservers=None):
		"""
		Function for performing general resolution types.

		Special type of register is "ALL", that returns all of the registers
		returned by the query.

		:param target: the name to resolve.
		:type target: str

		:param type: The type of query: ALL, A, AAAA, NS, PTR...
		:type type: int or str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: return a DnsRegister type.
		:rtype: DnsRegister
		"""
		return self._make_request(type, target, nameservers)


	#----------------------------------------------------------------------
	def get_a(self, host, nameservers=None):
		"""
		Function for resolving the A Record for a given host.

		Returns an Array of the A registers.

		:param host: String with name of host to get the registers.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with A registers.
		:rtype: list(DnsRegisterA)
		"""
		return self._make_request("A", host, nameservers)


	#----------------------------------------------------------------------
	def get_aaaa(self, host, nameservers=None):
		"""
		Function for resolving the A Record for a given host.

		Returns an Array of the AAAA registers.

		:param host: String with name of host to get the registers.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with AAAA registers
		:rtype: list(DnsRegisterAAAA)
		"""
		return self._make_request("AAAA", host, nameservers)


	#----------------------------------------------------------------------
	def get_mx(self, host, nameservers=None):
		"""
		Function for resolving the MX Record for a given host.

		Returns an Array of the MX registers.

		:param host: String with name of host to get the registers.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with MX registers
		:rtype: list(DnsRegisterMX)
		"""
		return self._make_request("MX", host, nameservers)


	#----------------------------------------------------------------------
	def get_ns(self, host, nameservers=None):
		"""
		Function for NS Record resolving. Returns all NS records. Returns also the IP
		address of the host both in IPv4 and IPv6. Returns an Array.

		:param host: the target to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with NS registers
		:rtype: list(DnsRegisterNS)
		"""
		return self._make_request("NS", host, nameservers)


	#----------------------------------------------------------------------
	def get_soa(self, host, nameservers=None):
		"""
		Function for SOA Record resolving. Returns all SOA records. Returns also the IP
		address of the host both in IPv4 and IPv6. Returns an Array.

		:param host: the target to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with SOA registers
		:rtype: list(DnsRegisterSOA)
		"""
		return self._make_request("SOA", host, nameservers)


	#----------------------------------------------------------------------
	def get_spf(self, host, nameservers=None):
		"""
		Function for SPF Record resolving returns the string with the SPF definition.

		:param host: the target to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with SPF registers
		:rtype: list(DnsRegisterSPF)
		"""
		return self._make_request("SPF", host, nameservers)


	#----------------------------------------------------------------------
	def get_txt(self, host, nameservers=None):
		"""
		Function for TXT Record resolving returns the string.

		:param host: the target to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with TXT registers
		:rtype: list(DnsRegisterTXT)
		"""
		return self._make_request("TXT", host, nameservers)


	#----------------------------------------------------------------------
	def get_ptr(self, ipaddress, nameservers=None):
		"""
		Function for resolving PTR Record given it's IPv4 or IPv6 Address.

		:param ipaddress: IP address to make the request.
		:type ipaddress: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with PTR registers
		:rtype: list(DnsRegisterPTR)
		"""
		return self._make_request("PTR", ipaddress, nameservers)


	#----------------------------------------------------------------------
	def get_srv(self, host, nameservers=None):
		"""
		Function for resolving SRV Records.

		:param host: host to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with SRV registers
		:rtype: list(DnsRegisterSRV)
		"""
		return self._make_request("SRV", host, nameservers)


	#----------------------------------------------------------------------
	def get_nsec(self, host, nameservers=None):
		"""
		Function for querying for a NSEC record and retriving the rdata object.
		This function is used mostly for performing a Zone Walk against a zone.

		:param host: host to make the request.
		:type host: str

		:param nameservers: nameserver to use.
		:type nameservers: list(str)

		:return: list with NSEC registers
		:rtype: list(DnsRegisterNSEC)
		"""
		return self._make_request("NSEC", host, nameservers)


	#----------------------------------------------------------------------
	def zone_transfer(self):
		"""
		Function for testing for zone transfers for a given Domain, it will parse the
		output by record type.

		The format of the returns is a dict that can contains:

		{ 'info' }

		:return: a dict with the info of the zone transfer.
		:rtype: dict()
		"""
		# if anyone reports a record not parsed I will add it, the list is a long one
		# I tried to include those I thought where the most common.
		raise NotImplemented()


		zone_records = []
		ns_records = []

		# Find SOA for Domain
		try:
			soa_srvs = self.get_soa()
			for s in soa_srvs:
				print_good("\t {0}".format(" ".join(s)))
				ns_records.append(s[2])
		except:
			raise ValueError("Could not obtain the domains SOA Record.")

		# Find NS for Domain
		ns_srvs = []
		try:
			ns_srvs = self.get_ns()
			for ns in ns_srvs:
				ns_ip = ''.join(ns[2])
				ns_records.append(ns_ip)
		except Exception as s:
			pass

		# Remove duplicates
		ns_records = list(set(ns_records))
		# Test each NS Server
		for ns_srv in ns_records:
			if self.check_tcp_dns(ns_srv):
				try:
					zone = self.from_wire(dns.query.xfr(ns_srv, self._domain))
					# Zone Transfer was successful!!
					zone_records.append({'type': 'info',
										 'zone_transfer': 'success',
										 'ns_server': ns_srv})
					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.SOA):
						for rdata in rdataset:
							for mn_ip in self.get_ip(rdata.mname.to_text()):
								if re.search(r'^A', mn_ip[0]):
									zone_records.append({'zone_server': ns_srv,
														 'type': 'SOA',
														 'mname': rdata.mname.to_text()[:-1],
														 'address': mn_ip[2]})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NS):
						for rdata in rdataset:
							for n_ip in self.get_ip(rdata.target.to_text()):
								if re.search(r'^A', n_ip[0]):
									zone_records.append({'zone_server': ns_srv,
														 'type': 'NS',
														 'target': rdata.target.to_text()[:-1],
														 'address': n_ip[2]})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.TXT):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'TXT',
												 'strings': ''.join(rdata.strings)})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.SPF):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'SPF',
												 'strings': ''.join(rdata.strings)})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.PTR):
						for rdata in rdataset:
							for n_ip in self.get_ip(rdata.target.to_text() + "." + self._domain):
								if re.search(r'^A', n_ip[0]):
									zone_records.append({'zone_server': ns_srv,
														 'type': 'PTR',
														 'name': "%s.%s" % (rdata.target.to_text(), self._domain),
														 'address': n_ip[2]})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.MX):
						for rdata in rdataset:
							for e_ip in self.get_ip(rdata.exchange.to_text()):
								zone_records.append({'zone_server': ns_srv,
													 'type': 'MX',
													 'name': "%s.%s" % (str(name), self._domain),
													 'exchange': rdata.exchange.to_text()[:-1],
													 'address': e_ip[2]})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.AAAA):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'AAAA',
												 'name': "%s.%s" % (str(name), self._domain),
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.A):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'A',
												 'name': "%s.%s" % (str(name), self._domain),
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.CNAME):
						for rdata in rdataset:
							for t_ip in self.get_ip(rdata.target.to_text()):
								if re.search(r'^A', t_ip[0]):
									zone_records.append({'zone_server': ns_srv,
														 'type': 'CNAME',
														 'name': "%s.%s" % (str(name), self._domain),
														 'target': str(rdata.target.to_text())[:-1],
														 'address': t_ip[2]})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.SRV):
						for rdata in rdataset:
							ip_list = self.get_ip(rdata.target.to_text())
							if ip_list:
								for t_ip in self.get_ip(rdata.target.to_text()):
									if re.search(r'^A', t_ip[0]):
										zone_records.append({'zone_server': ns_srv,
															 'type': 'SRV',
															 'name': "%s.%s" % (str(name), self._domain),
															 'target': rdata.target.to_text()[:-1],
															 'address': t_ip[2],
															 'port': str(rdata.port),
															 'weight': str(rdata.weight)})
							else:
								zone_records.append({'zone_server': ns_srv,
													 'type': 'SRV',
													 'name': "%s.%s" % (str(name), self._domain),
													 'target': rdata.target.to_text()[:-1],
													 'address': "no_ip",
													 'port': str(rdata.port),
													 'weight': str(rdata.weight)})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.HINFO):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'HINFO',
												 'cpu': rdata.cpu,
												 'os': rdata.os})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.WKS):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'WKS',
												 'address': rdata.address,
												 'bitmap': rdata.bitmap,
												 'protocol': rdata.protocol})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.RP):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'RP',
												 'mbox': rdata.mbox.to_text(),
												 'txt': rdata.txt.to_text()})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.AFSDB):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'AFSDB',
												 'subtype': str(rdata.subtype),
												 'hostname': rdata.hostname.to_text()})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.LOC):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'LOC',
												 'coordinates': rdata.to_text()})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.X25):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'X25',
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.ISDN):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'ISDN',
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.RT):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'X25',
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NSAP):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'NSAP',
												 'address': rdata.address})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NAPTR):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'NAPTR',
												 'order': str(rdata.order),
												 'preference': str(rdata.preference),
												 'regex': rdata.regexp,
												 'replacement': rdata.replacement.to_text(),
												 'service': rdata.service})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.CERT):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'CERT',
												 'algorithm': rdata.algorithm,
												 'certificate': rdata.certificate,
												 'certificate_type': rdata.certificate_type,
												 'key_tag': rdata.key_tag})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.SIG):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'SIG',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'expiration': rdata.expiration,
												 'inception': rdata.inception,
												 'key_tag': rdata.key_tag,
												 'labels': rdata.labels,
												 'original_ttl': rdata.original_ttl,
												 'signature': rdata.signature,
												 'signer': str(rdata.signer),
												 'type_covered': rdata.type_covered})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.RRSIG):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'RRSIG',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'expiration': rdata.expiration,
												 'inception': rdata.inception,
												 'key_tag': rdata.key_tag,
												 'labels': rdata.labels,
												 'original_ttl': rdata.original_ttl,
												 'signature': rdata.signature,
												 'signer': str(rdata.signer),
												 'type_covered': rdata.type_covered})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.DNSKEY):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'DNSKEY',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'flags': rdata.flags,
												 'key': dns.rdata._hexify(rdata.key),
												 'protocol': rdata.protocol})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.DS):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'DS',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'digest': dns.rdata._hexify(rdata.digest),
												 'digest_type': rdata.digest_type,
												 'key_tag': rdata.key_tag})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NSEC):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'NSEC',
												 'next': rdata.next})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NSEC3):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'NSEC3',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'flags': rdata.flags,
												 'iterations': rdata.iterations,
												 'salt': dns.rdata._hexify(rdata.salt)})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.NSEC3PARAM):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'NSEC3PARAM',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'flags': rdata.flags,
												 'iterations': rdata.iterations,
												 'salt': rdata.salt})

					for (name, rdataset) in zone.iterate_rdatasets(dns.rdatatype.IPSECKEY):
						for rdata in rdataset:
							zone_records.append({'zone_server': ns_srv,
												 'type': 'IPSECKEY',
												 'algorithm': algorithm_to_text(rdata.algorithm),
												 'gateway': rdata.gateway,
												 'gateway_type': rdata.gateway_type,
												 'key': dns.rdata._hexify(rdata.key),
												 'precedence': rdata.precedence})
				except Exception as e:
					# Zone Transfer Failed!
					zone_records.append({'type': 'info',
										 'zone_transfer': 'failed',
										 'ns_server': ns_srv})
			else:
				# Zone Transfer Failed
				# Port 53 TCP is being filtered
				zone_records.append({'type': 'info',
								     'zone_transfer': 'failed',
								     'ns_server': ns_srv})
		return zone_records


	#----------------------------------------------------------------------
	#
	# Helpers
	#
	#----------------------------------------------------------------------
	def get_ips(self, register):
		"""
		Get the list of IPs associated the register as parameter.

		If you pass CNAME register, you get an A/AAAA register:

		>> cname = DnsRegisterCNAME("myalias.mysite.com")
		>> a = Dns.get_ips(cname)
		>> print a
		[<DnsRegisterA object at 0x103ad9a50>]
		>> print a[0]
		<DnsRegisterA object at 0x103ad9a50>
		>> print a[0].target
		127.0.0.1

		:param register: A DNS Register. Valid registers are: DnsRegisterA, DnsRegisterAAAA, DnsRegisterCNAME DnsRegisterISDN, DnsRegisterNS, DnsRegisterNSAP, DnsRegisterPTR, DnsRegisterSOA, DnsRegisterSRV, DnsRegisterWKS, DnsRegisterX25
		:type register: DnsRegister

		:return: A list with the A and AAAA registers.
		:rtype : list(DnsRegisterA|DnsRegisterAAAA)
		"""
		if not isinstance(register, DnsRegister):
			raise TypeError("Expected DnsRegister, got '%s'" % type(register))
		if register.type not in ("A", "AAAA", "CNAME", "ISDN", "NS", "NSAP", "PTR", "SOA", "SRV", "WKS", "X25"):
			raise TypeError("Register type are not valid. Valid values are: A, AAAA, ISDN, NS, NSAP, PTR, SOA, SRV, WKS, X25")

		PROP = {
			"A":"target",
			"AAA":"target",
			"CNAME":"target",
			"ISDN":"address",
			"NS":"target",
			"NSAP":"address",
			"PTR":"target",
			"SOA":"mname",
			"SRV":"target",
			"WKS":"address",
			"X25":"address"
		}

		if register.type in ("A", "AAAA"):
			return register

		m_return = []
		# IPv4 address
		m_return.extend(self.get_a(getattr(register, PROP[register.type])))
		# IPv6 address
		m_return.extend(self.get_aaaa(getattr(register, PROP[register.type])))

		return m_return


	#----------------------------------------------------------------------
	def _dnslib2register(self, type, answer_in):
		"""
		Creates a DnsRegister from an dnslib input library.

		Special type of register "ALL" that converts all the types of the
		registers.

		:param type: the type of response to get: A, AAAA, CNAME...
		:type type: str

		:param answer: object with the answer of external dns lib
		:type answer: dns.resolver.Answer

		:return: Golismero DnsRegister subtype for the specific type.
		:rtype: `list(DnsRegister)`
		"""


		m_return        = []
		m_return_append = m_return.append

		for ardata in answer_in.response.answer:
			for rdata in ardata:

				register_type = DnsRegister.id2name(rdata.rdtype)

				# If register it different that we are looking for, skip it.
				if type != register_type and type != "ALL":
					continue

				answer = rdata

				if register_type == "A":
					m_return_append(DnsRegisterA(answer.address))
				elif register_type == "AAAA":
					m_return_append(DnsRegisterAAAA(answer.address))
				elif register_type == "AFSDB":
					m_return_append(DnsRegisterAFSDB(answer.subtype, answer.hostname))
				elif register_type == "CERT":
					m_return_append(DnsRegisterCERT(answer.algorithm,
										            answer.certificate,
										            answer.certificate_type,
										            answer.key_tag))
				elif register_type == "CNAME":
					m_return_append(DnsRegisterCNAME(answer.target.to_text()[:-1]))
				elif register_type == "DNSKEY":
					m_return_append(DnsRegisterDNSKEY(answer.algorithm,
										              answer.flags,
										              dns.rdata._hexify(answer.key),
										              answer.protocol))
				elif register_type == "DS":
					m_return_append(DnsRegisterDS(answer.algorithm,
										          dns.rdata._hexify(answer.digest),
										          answer.digest_type,
										          answer.key_tag))
				elif register_type == "HINFO":
					m_return_append(DnsRegisterHINFO(answer.cpu,
										             answer.os))
				elif register_type == "IPSECKEY":
					m_return_append(DnsRegisterIPSECKEY(answer.algorithm,
										                answer.gateway,
										                answer.gateway_type,
										                answer.key,
										                answer.precedence))
				elif register_type == "ISDN":
					m_return_append(DnsRegisterISDN(answer.address,
										            answer.subaddress))
				elif register_type == "LOC":
					m_return = DnsRegisterLOC(answer.latitude, answer.longitude, answer.to_text())
				elif register_type == "MX":
					m_return_append(DnsRegisterMX(answer.exchange.to_text()[:-1],
										          answer.preference))
				elif register_type == "NAPTR":
					m_return_append(DnsRegisterNAPTR(answer.order,
										             answer.preference,
										             answer.regexp,
										             answer.replacement,
										             answer.service))
				elif register_type == "NS":
					m_return_append(DnsRegisterNS(answer.target.to_text()[:-1]))
				elif register_type == "NSAP":
					m_return_append(DnsRegisterNSAP(answer.address))
				elif register_type == "NSEC":
					m_return_append(DnsRegisterNSEC(answer.next.to_text()[:-1]))
				elif register_type == "NSEC3":
					m_return_append(DnsRegisterNSEC3(answer.algorithm,
										             answer.flags,
										             answer.iterations,
										             dns.rdata._hexify(answer.salt)))
				elif register_type == "NSEC3PARAM":
					m_return_append(DnsRegisterNSEC3PARAM(answer.algorithm,
										                  answer.flags,
										                  answer.iterations,
										                  dns.rdata._hexify(answer.salt)))
				elif register_type == "PTR":
					m_return_append(DnsRegisterPTR(answer.target))
				elif register_type == "RP":
					m_return_append(DnsRegisterRP(answer.mbox,
										          answer.txt))
				elif register_type == "RPSIG":
					m_return_append(DnsRegisterRRSIG(answer.algorithm,
										             answer.expiration,
										             answer.interception,
										             answer.key_tag,
										             answer.labels,
										             answer.original_ttl,
										             answer.signer,
										             answer.type_coverded))
				elif register_type == "SOA":
					m_return_append(DnsRegisterSOA(answer.mname.to_text()[:-1],
										           answer.rname.to_text()[:-1],
										           answer.refresh,
										           answer.expire))
				elif register_type == "SPF":
					m_return_append(DnsRegisterSPF(answer.strings))
				elif register_type == "SRV":
					m_return_append(DnsRegisterSRV(answer.target.to_text()[:-1],
										           answer.priority,
										           answer.weight,
										           answer.port))
				elif register_type == "TXT":
					m_return_append(DnsRegisterTXT(answer.strings))
				elif register_type == "WKS":
					m_return_append(DnsRegisterWKS(answer.address,
										           answer.protocol,
										           answer.bitmap))
				elif register_type == "X25":
					m_return_append(DnsRegisterX25(answer.address))
				else:
					raise ValueError("DNS register type '%s' is incorrect." % register_type)

		return m_return


	#----------------------------------------------------------------------
	def _make_request(self, register_type, host, nameservers=None):
		"""
		Make a request, using dnslib, and return an unified type of data
		RegisterXXXX.

		:param: register_type: of query: A, AAAA, CNAME...
		:type register_type: str

		:param host: Host where make the resquest.
		:type host: str

		:param nameservers: list with a custom name servers
		:type nameservers: list(str)

		:return: a list with the DnsRegisters
		:type: list(DnsRegister)
		"""
		if not isinstance(register_type, basestring):
			raise TypeError("Expected str, got '%s'" % type(type))
		if not isinstance(host, basestring):
			raise TypeError("Expected basestring, got '%s'" % type(host))
		if nameservers:
			if isinstance(nameservers, list):
				for n in nameservers:
					if not isinstance(n, basestring):
						raise TypeError("Expected basestring, got '%s'" % type(n))
			else:
				raise TypeError("Expected list, got '%s'" % type(nameservers))

		m_query_obj           = None

		if nameservers:
			m_query_obj             = dns.resolver.Resolver(configure=False)
			m_query_obj.nameservers = nameservers
		else:
			m_query_obj             = dns.resolver.Resolver(configure=True)

		# Set timeouts
		m_query_obj.timeout         = self.REQUEST_TIMEOUT
		m_query_obj.lifetime        = self.REQUEST_TIMEOUT

		try:
			answer = m_query_obj.query(host, register_type)
		except Exception, e:
			return []
			#raise NetworkException("Error while make the request: " + e)

		return self._dnslib2register(register_type, answer)