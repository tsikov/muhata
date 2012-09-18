from django.conf.urls import patterns, include, url

urlpatterns = patterns('muhataapp.views',
    url(r'^$', 'home'),
    url(r'^register-user/$', 'add_user_to_database'),
    url(r'^login-user/$', 'authenticate_and_login_user'),
    url(r'^izhod/$', 'logout_user'),
    url(r'^dobavi-obqva/$', 'display_add_ad_page'),
    url(r'^add-ad-to-database/$', 'add_ad_to_database'),
    url(r'^obqva/(\d+)/redaktirai/$', 'display_edit_ad'),
    url(r'^obqva/(\d+)/$', 'add_slug'),
    url(ur'^obqva/(\d+)/([\w-]+)/$', 'display_ad'),
    url(r'^obqva/(\d+)/redaktirai$', 'edit_ad'),
    url(r'^obqva/(\d+)/iztrii$', 'delete_ad'),
    url(r'^search-by-tags/$', 'tag_search'),

    url(r'^get-suggestions/$', 'return_suggestions'),
    url(r'^report-ad/(\d+)/$', 'report_ad'),
    url(r'^delete-ad/(\d+)/$', 'delete_ad'),
    url(r'^change-to-database/(\d+)/$', 'change_ad'),
    url(r'^delete-pic/(\d+)/$', 'delete_pic'),
)
