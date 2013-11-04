from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import link
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from rest_framework.decorators import permission_classes

from backend.rest_api.authentication import ExpiringTokenAuthentication
from backend.rest_api.serializers import *

from backend.managers.golismero_facade import *
from backend.managers import GoLismeroAuditData

#
# This file defines the actions for the API-REST
#

__all__ = ["AuditViewSet", "UsersViewSet", "PluginsViewSet", "ProfilesViewSet", "NodesViewSet"]

#------------------------------------------------------------------------------
#
# Audit actions
#
#------------------------------------------------------------------------------
class AuditViewSet(ViewSet):
	"""
	Actions with plugins
	"""

	AUDIT_STATES = ["running", "stopped", "paused", "canceled", "new", "all"]


	#----------------------------------------------------------------------
	def __init__(self):
		""""""

		# Dummy data
		self.audits = {}
		self.audits["running"] = [
				{
		            'id'     : '11',
					'name'    : 'audit1',
					'user'    : 'user1',
					'state'   : 'running'
				},
				{
		            'id'      : '12',
					'name'    : 'audit2',
					'user'    : 'user1',
					'state'   : 'running'
				}
		]
		self.audits["stopped"] = [
				{
		            'id'      : '10',
					'name'    : 'audit3',
					'user'    : 'user2',
					'state'   : 'stopped'
				},
		]
		self.audits["paused"] = [
				{
		            'id'      : '7',
					'name'    : 'audit4',
					'user'    : 'user4',
					'state'   : 'paused'
				},
		        {
		            'id'      : '8',
		            'name'    : 'audit9',
		            'user'    : 'user4',
		            'state'   : 'paused'
		        },
		]
		self.audits["canceled"] = [
				{
		            'id'      : '5',
					'name'    : 'audit6',
					'user'    : 'user4',
					'state'   : 'canceled'
				},
		        {
		            'id'      : '6',
		            'name'    : 'audit8',
		            'user'    : 'user10',
		            'state'   : 'canceled'
		        },
		]
		self.audits["new"] = [
				{
		            'id'      : '3',
					'name'    : 'audit20',
					'user'    : 'user11',
					'state'   : 'new'
				},
		        {
		            'id'      : '4',
		            'name'    : 'audit12',
		            'user'    : 'user10',
		            'state'   : 'new'
		        },
		]


		self.unified_audits = [v[0] for k,v in self.audits.iteritems()]



	#----------------------------------------------------------------------
	#
	# LIST methods
	#
	#----------------------------------------------------------------------
	def list(self, request, *args, **kwargs):
		"""
		Get audit list returning a maximun of 100 audits

		States availables:
		- running
		- stopped
		- paused
		- canceled
		- new
		- all

		:return: Response format:
		[
		   {
		      'name'  : 'AUDIT NAME',
			  'user'  : 'OWNER OF AUDIT',
			  'state' : 'A VALID STATE'
		   }
		]

		"""

		m_return = {
	        'results' : self.__audit2json(Audits.objects.all()[:100])
	    }

		return Response(m_return)

	#----------------------------------------------------------------------
	def list_parameterized(self, request, *args, **kwargs):
		"""
		Get audit list in the state as parameter "text", returning a maximun of 100 results.

		States availables:
		- running
		- stopped
		- paused
		- canceled
		- new
		- all

		:param text: in kwargs var, parameter with the state
		:type text: str

		:return: Response format:
		[
		   {
		      'name'  : 'AUDIT NAME',
			  'user'  : 'OWNER OF AUDIT',
			  'state' : 'A VALID STATE'
		   }
		]
		"""


		m_return = {}
		m_state  = str(kwargs.get("text", None))

		if m_state:
			if m_state in self.AUDIT_STATES:
				m_return['status']  = "ok"

				if m_state == "all":
					m_return["results"] = self.__audit2json(Audits.objects.all()[:100])
				else:
					m_return["results"] = self.__audit2json(Audits.objects.filter(audit_state=m_state).all()[:100])

				return Response(m_return)


		#
		# If errors...
		#
		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Unknown state"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)


	#----------------------------------------------------------------------
	#
	# CRUD methods
	#
	#----------------------------------------------------------------------
	def create(self, request, *args, **kwargs):
		"""

		"""



		m_return = {}
		m_info   = None


		#
		# AUDIT INFO
		#
		audit    = AuditSerializer(data=request.DATA)
		# Audit is valid?
		if not audit.is_valid():
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["%s: %s" %(x, y.pop()) for x, y in audit.errors.iteritems()]
			return Response(m_return, status.HTTP_400_BAD_REQUEST)

		# Store into global info
		m_info = { k : str(v) for k, v in audit.data.iteritems()}
		if m_info.get("disable_plugins", None):
			m_info["disable_plugins"] = [x.strip() for x in m_info["disable_plugins"].split(",")]

		#
		# TARGETS
		#
		# :: Targets available?
		m_targets_in = request.DATA.get("targets", None)
		if not m_targets_in:
			m_return['status']      = "error"
			m_return['error_code']  = 2
			m_return['error']       = ["Targets are missing."]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)

		# :: Recover targets
		m_targets = [] # Target lists
		for t in m_targets_in:
			l_target = TargetSerializer(data=t)
			if not l_target.is_valid():
				m_return['status']      = "error"
				m_return['error_code']  = 1
				m_return['error']       = ["Target parameter '%s' are invalid." % l_target.target_name]
				return Response(m_return, status.HTTP_400_BAD_REQUEST)

			# Add to target list
			m_targets.append({ k : str(v) for k, v in l_target.data.iteritems()})

		# Append to global info
		m_info['targets'] = m_targets


		#
		# PLUGINS
		#
		m_plugins_in = request.DATA.get("enabled_plugins", [])
		m_plugins    = [] # Plugins lists
		for p in m_plugins_in:

			l_plugin = PluginsSerializer(data=p)
			if not l_plugin.is_valid():
				m_return['status']      = "error"
				m_return['error_code']  = 1
				m_return['error']       = ["Plugin '%s' are invalid." % l_plugin]
				return Response(m_return, status.HTTP_400_BAD_REQUEST)

			# Store info
			l_plugin = { k : str(v) for k, v in l_plugin.data.iteritems()}


			pp = p['params']
			if pp:
				l_plugin_results = []
				for plug_p in pp:
					l_p = PluginsParametersSerializer(data=plug_p)

					if not l_p.is_valid():
						m_return['status']      = "error"
						m_return['error_code']  = 1
						m_return['error']       = ["Param '%s' for '%s' plugin are invalid." % (l_p, l_plugin['plugin_name'])]
						return Response(m_return, status.HTTP_400_BAD_REQUEST)

					l_plugin_results.append({ k : str(v) for k, v in l_p.data.iteritems()})

				# Add to plugin
				l_plugin['params'] = l_plugin_results

			# Add to plugins store
			m_plugins.append(l_plugin)

		# Add to global info
		m_info['enabled_plugins'] = m_plugins


		#
		# Request for new audit
		#
		m_audit_id = GoLismeroFacadeAudit.create(m_info)

		m_return['status']        = "ok"
		m_return['audit_id']      = m_audit_id

		return Response(m_return)





	#----------------------------------------------------------------------
	def delete(self, request, *args, **kwargs):
		"""
		This method deletes an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""

		# Search
		pk      = str(kwargs.get("pk", None))

		# Checks if audit exits
		m_audit = self.__get_audit(pk)
		if not m_audit:
			m_return                = {}
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["Provided audit ID not found"]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)


		return Response({'status' : 'ok'})


	#----------------------------------------------------------------------
	def details(self, request, *args, **kwargs): ##
		"""

		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']           = "ok"
			m_return['start_date']       = "2013-10-18 16:03:32"
			m_return['end_date']         = "2013-10-14 10:23:32"
			m_return['user']             = "user1"
			m_return['config']           = {
			    "targets"               : ["www.target1.com", "target2.com"],
			    "only_vulns"            : "False",
			    "audit_name"            : "audit1",
			    "imports"               : [""],
			    "enable_plugins"        : ["spider", "sqlmap", "openvas"],
			    "disable_plugins"       : [""],
			    "include_subdomains"    : "True",
			    "subdomain_regex"       : "",
			    "depth"                 : "0",
			    "max_links"             : "0",
			    "follow_redirects"      : "True",
			    "follow_first_redirect" : "True",
			    "proxy_addr"            : "",
			    "proxy_user"            : "",
			    "proxy_pass"            : "",
			    "cookie"                : "",
			    "user_agent"            : "random",
			}

			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)


	#----------------------------------------------------------------------
	#
	# Management
	#
	#----------------------------------------------------------------------
	def start(self, request, *args, **kwargs): ##
		"""
		This method starts an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']      = "ok"
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not found"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)

	#----------------------------------------------------------------------
	def stop(self, request, *args, **kwargs): ##
		"""
		This method stops an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']      = "ok"
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)

	#----------------------------------------------------------------------
	def state(self, request, *args, **kwargs):
		"""
		Get audit state as format:

		{
		   'state' : str
		}

		:return: dict with state
		:rtype: dict(str)
		"""
		# Info
		m_audit_id  = str(kwargs.get("pk", None))
		m_return    = {}

		m_info = None
		try:
			m_info = GoLismeroFacadeAudit.get_state(m_audit_id)

			#
			# Returns info
			#
			m_return['status']      = "ok"
			m_return['state']       = m_info

			return Response(m_return)

		# Audit not exits
		except GoLismeroFacadeAuditNotFoundException, e:
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["Provided audit ID not found"]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)

		# Unknown exception
		except Exception, e:
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["Unknown error: %s" % str(e)]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)

	#----------------------------------------------------------------------
	def progress(self, request, *args, **kwargs):
		"""
		Get audit progress as format:

		:return: return the progress in format:
		{
		  'current_stage' : str,
		  'steps'         : int,
		  'tests_remain'  : int,
		  'test_done'     : int
		}
		:rtype: dict(str)
		"""
		# Info
		m_audit_id  = str(kwargs.get("pk", None))
		m_return    = {}

		m_info = None
		try:
			m_info = GoLismeroFacadeAudit.get_progress(m_audit_id)
			m_info = m_info.to_json()

			#
			# Returns info
			#
			m_return['status']      = "ok"
			m_return.update(m_info)

			return Response(m_return)

		# Audit not exits
		except GoLismeroFacadeAuditNotFoundException, e:
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["Provided audit ID not found"]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)

		# Unknown exception
		except Exception, e:
			m_return['status']      = "error"
			m_return['error_code']  = 0
			m_return['error']       = ["Unknown error: %s" % str(e)]

			return Response(m_return, status.HTTP_400_BAD_REQUEST)




	#----------------------------------------------------------------------
	def pause(self, request, *args, **kwargs): ##
		"""
		This method pauses an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']      = "ok"
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)


	#----------------------------------------------------------------------
	def resume(self, request, *args, **kwargs): ##
		"""
		This method resumes an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']      = "ok"
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)



	#----------------------------------------------------------------------
	def log(self, request, *args, **kwargs): ##
		"""
		This method return audit logs, using their ID

		:param pk: audit ID
		:type pk: str
		"""
		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return['status']      = "ok"
			m_return['log']         = "Log dummy info"
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)




	#----------------------------------------------------------------------
	#
	# Results
	#
	#----------------------------------------------------------------------
	def results(self, request, *args, **kwargs): ##
		"""

		"""
		return Response({'results':'aaaa'})

	#----------------------------------------------------------------------
	def results_formated(self, request, *args, **kwargs): ##
		"""

		"""
		return Response({'results_formated':'aaaa'})

	#----------------------------------------------------------------------
	def results_summary(self, request, *args, **kwargs): ##
		"""
		This method summary an audit, using their ID

		:param pk: audit ID
		:type pk: str
		"""

		# Search
		pk     = str(kwargs.get("pk", ""))
		res    = [v for v in self.unified_audits if v['id'] == pk]

		m_return = {}
		if res:
			m_return                            = {}
			m_return['status']                  = 'ok'
			m_return['vulns_number']            = '12'
			m_return['discovered_hosts']        = '3'
			m_return['total_hosts']             = '4'
			m_return['vulns_by_level']          = {
				'info'     : '5',
				'low'      : '2',
				'medium'   : '2',
				'high'     : '2',
				'critical' : '1',
			}
			return Response(m_return)


		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Provided audit ID not exits"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)













#------------------------------------------------------------------------------
#
# Users actions
#
#------------------------------------------------------------------------------
class UsersViewSet(ViewSet):
	"""
	Actions with plugins
	"""
	pass


#------------------------------------------------------------------------------
#
# Plugins actions
#
#------------------------------------------------------------------------------
class PluginsViewSet(ViewSet):
	"""
	Actions with plugins
	"""

	#authentication_classes = (BasicAuthentication, SessionAuthentication, TokenAuthentication)
	authentication_classes  = (ExpiringTokenAuthentication,)
	permission_classes = (IsAuthenticated,)

	#----------------------------------------------------------------------
	def list(self, request, *args, **kwargs):
		"""
		List all available plugins and their params in format:

		>>> return = [
		   {
			  'stage'       : 'recon',
			  'plugin_name' : 'spider',
			  'params'      : [
				 {
					'name'    : 'param1',
					'type'    : 'str',
					'default' : ''
				 },
				 {
					'name'    : 'param2',
					'type'    : 'int',
					'default' : '0'
				 }
			  ]
			}
		]
		"""
		return Response({'as':'aaaa'})

	def search(self, request, *args, **kwargs):
		s = kwargs['text']
		return Response({'search text' : s})


	#----------------------------------------------------------------------
	def detail(self, request, *args, **kwargs):
		"""
		Get details from a concrete plugin
		"""
		return Response({'details':kwargs['pk']})


#------------------------------------------------------------------------------
#
# Profiles actions
#
#------------------------------------------------------------------------------
class ProfilesViewSet(ViewSet):
	"""
	Actions with plugins
	"""
	pass


#------------------------------------------------------------------------------
#
# Nodes actions
#
#------------------------------------------------------------------------------
class NodesViewSet(ViewSet):
	"""
	Actions with plugins
	"""
	pass