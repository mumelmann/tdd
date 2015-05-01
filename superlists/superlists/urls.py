from django.conf.urls import include, url
from django.contrib import admin

from lists import views as lists_views
from lists import urls as lists_urls


urlpatterns = [
    # Examples:
    url(r'^$', lists_views.home_page, name='home'),
    url(r'^lists/', include(lists_urls)),
    # url(r'^blog/', include('blog.urls')),
    # url(r'^admin/', include(admin.site.urls)),
]
