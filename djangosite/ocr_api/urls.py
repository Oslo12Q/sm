"""sm URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.8/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import include, url, patterns

urlpatterns = patterns(
    'sm.djangosite.ocr_api.views.views',

    (r'^index/$', 'index'),
    (r'^async_analysis/$', 'async_analysis'),
    (r'^async_analysis/result/$', 'async_analysis_result'),

    (r'^case_report/$','case_report'),
    (r'^exhibition_index/$','exhibition_index'),
    (r'^get_exhibition_index/$','get_exhibition_index'),
    (r'^list_exhibition_index/$','list_exhibition_index'),

)

urlpatterns += patterns(
    'sm.djangosite.ocr_api.views.prescription',

    (r'^prescription/$','prescription'),
    (r'^prescription/async_analysis/$','async_analysis'),
    (r'^prescription/async_analysis/result/$','async_analysis_result'),
)

urlpatterns += patterns(
    'sm.djangosite.ocr_api.views.medical_api',

    (r'^medical/analysis/$', 'analysis'),
    (r'^medical/async_analysis/$', 'async_analysis'),
    (r'^medical/async_analysis/result/$', 'async_analysis_result'),
)
