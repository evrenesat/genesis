"""genesis URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.views.defaults import server_error
from django.views.generic import RedirectView

urlpatterns = [

    url(r'^lab/', include('lab.urls')),
    url(r'^com/', include('com.urls')),
    # url(r'^settings/', include('dbsettings.urls')),
    url(r'^admin/', admin.site.urls),
    url(r'^grappelli/', include('grappelli.urls')),

    url(r'^500/$', server_error),
    url(r'^$', RedirectView.as_view(url='/admin/', permanent=False)),
]
