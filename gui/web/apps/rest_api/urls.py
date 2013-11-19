from django.conf.urls import patterns, url, include
from views import *
from routes import *
import rest_framework.urls

#
# Full information of routers in:
#
# http://django-rest-framework.org/api-guide/routers.html#usage
#

pooling_routes  = PoolingRouters()
pooling_routes.register(r'pooling', PoolingViewSet, base_name="pooling")

audit_routes    = AuditsRouters()
audit_routes.register(r'^audits', AuditViewSet, base_name="plugins")

user_routes     = UsersRouters()
user_routes.register(r'users', UsersViewSet, base_name="users")

plugin_routes   = PluginsRouters()
plugin_routes.register(r'plugins', PluginsViewSet, base_name="plugins")

profiles_routes = ProfilesRouters()
profiles_routes.register(r'profiles', ProfilesViewSet, base_name="profiles")

nodes_routes    = NodesRouters()
nodes_routes.register(r'nodes', NodesViewSet, base_name="nodes")

urlpatterns = patterns('',

    # Pooling methods
    url(r'pooling', include(pooling_routes.urls)),

    # Audits methods
    url(r'^api/', include(audit_routes.urls)),

    # Users methods
    url(r'^api/', include(user_routes.urls)),

    # PLugins methods
    url(r'^api/', include(plugin_routes.urls)),

    # Profiles methods
    url(r'^api/', include(profiles_routes.urls)),

    # Nodes methods
    url(r'^api/', include(nodes_routes.urls)),

    #
    # Authentication API
    #

    # - Web login
    #url(r'^api/auth/', include('rest_framework.urls', namespace="rest_framework")),
    # Token authentication
    url(r'^api/auth/login/$', 'backend.rest_api.views.obtain_expiring_auth_token'),
    url(r'^api/auth/logout/$', 'backend.rest_api.views.logout_token'),

)
