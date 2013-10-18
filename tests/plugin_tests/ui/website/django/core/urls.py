from django.conf.urls import patterns, include, url, handler403, handler404, handler500

urlpatterns = patterns('',
    url(r'^', include("apps.home.urls")),
    url(r'^', include("apps.rest_api.urls")),
)

handler404 = "apps.home.views.redirect_home"
handler500 = "apps.home.views.error"
handler403 = "apps.home.views.error"