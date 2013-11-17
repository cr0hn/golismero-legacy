from django.conf.urls import patterns, url

urlpatterns = patterns('',
                       url(r'index.html$', 'apps.home.views.home', name="view_home_home"),
                       url(r'login.html$', 'apps.home.views.login', name="view_home_login"),
                       url(r'^$', 'apps.home.views.master', name="view_home_login"),
)
