from django.conf.urls import url

from .views import BlogDetailView, BlogListView

urlpatterns = [
                url(r'^(?P<year>\d{4})/(?P<month>\d{2})/(?P<day>\d{2})/(?P<slug>[-_\w]+)/$',
                    BlogDetailView.as_view(),
                    name='blog_detail',
                    ),
                url(r'^$', BlogListView.as_view(), name='blog_index'),
            ]
