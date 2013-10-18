from rest_framework import status
from rest_framework.views import APIView
from rest_framework.viewsets import ViewSet, ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.decorators import link
from rest_framework.renderers import StaticHTMLRenderer
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import SessionAuthentication, BasicAuthentication, TokenAuthentication
from backend.rest_api.authentication import ExpiringTokenAuthentication
from rest_framework.decorators import permission_classes

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
		Get audit list.

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

		m_return = {}
		m_return['status']  = "ok"
		m_return["results"] = self.unified_audits

		return Response(m_return)

	#----------------------------------------------------------------------
	def list_parameterized(self, request, *args, **kwargs):
		"""
		Get audit list in the state as parameter "text"

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
					m_return["results"] = self.unified_audits
				else:
					m_return["results"] = self.audits[m_state]

				return Response(m_return)



		m_return['status']      = "error"
		m_return['error_code']  = 0
		m_return['error']       = ["Unknown state"]

		return Response(m_return, status.HTTP_400_BAD_REQUEST)

	#----------------------------------------------------------------------
	def create(self, request, *args, **kwargs):
		"""

		"""
		return Response({'create':'aaaa'})

	#----------------------------------------------------------------------
	def delete(self, request, *args, **kwargs):
		"""
		This method deletes an audit, using their ID

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
	def start(self, request, *args, **kwargs):
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
	def stop(self, request, *args, **kwargs):
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

		"""
		return Response({'state':'aaaa'})

	#----------------------------------------------------------------------
	def results(self, request, *args, **kwargs):
		"""

		"""
		return Response({'results':'aaaa'})

	#----------------------------------------------------------------------
	def results_formated(self, request, *args, **kwargs):
		"""

		"""
		return Response({'results_formated':'aaaa'})

	#----------------------------------------------------------------------
	def results_summary(self, request, *args, **kwargs):
		"""

		"""
		return Response({'results_summary':'aaaa'})

	#----------------------------------------------------------------------
	def details(self, request, *args, **kwargs):
		"""

		"""
		return Response({'details':'aaaa'})

	#----------------------------------------------------------------------
	def pause(self, request, *args, **kwargs):
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
	def resume(self, request, *args, **kwargs):
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
	def log(self, request, *args, **kwargs):
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