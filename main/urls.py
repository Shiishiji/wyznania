"""anonimowe URL Configuration

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
from main import views

urlpatterns = [
    url(r'^swap$', views.swap),

    # basic functionality
    url(r'^', include([
        url(r'^$', views.Home.as_view(), {'data': 'home'}, name='home'),
        url(r'^queue$', views.Home.as_view(), {'data': 'queue'}, name='queue'),
        url(r'^bests$', views.Home.as_view(), {'data': 'bests'}, name='bests'),
        url(r'^staff/queue$', views.Home.as_view(), {'data': 'staff_queue'}, name='staff_queue'),
        url(r'^staff/thrash$', views.Home.as_view(), {'data': 'staff_thrash'}, name='staff_thrash'),
        ])),
    url(r'^dodaj_wyznanie$', views.WyznanieCreate.as_view(), name='wyznanie_create'),
    url(r'^w/(?P<code>[A-z0-9]{12})/', include([
        url(r'^$', views.wyznanie, name='detail'),
        url(r'^accept$', views.post_judge, {'option': 3}, name='detail_accept'),
        url(r'^reject$', views.post_judge, {'option': 0}, name='detail_reject'),
        url(r'^move$', views.post_judge, {'option': 1}, name='detail_move'),
        url(r'^remove', views.post_judge, {'option': 2}, name='detail_remove'),
    ])),

    # api functionality
    url(r'^api/w/(?P<code>[A-z0-9]{12})/favourite$', views.toggle_favourite, name='api_toggle_favourite'),
    url(r'^api/(?P<mdl>[wca])/(?P<code>[A-z0-9]{12})/(?P<option>[0-1])$', views.likes_api, name='api_likes'),
    url(r'^api/(?P<code>[A-z0-9]{12})/get_answer_form$', views.GetAnswerForm.as_view(), name='api_answer_form'),

    # authentication section
    url(r'^rejestracja$', views.AuthenticationUserRegister.as_view(), name='register'),
    url(r'^logowanie$', views.AuthenticationUserLogin.as_view(), name='login'),
    url(r'^wyloguj$', views.user_logout, name='logout'),

    # user section
    url(r'^user/profile/', include([
        url(r'^$', views.settings, name='user_settings'),
        url(r'^change_password$', views.change_password, name='user_change_password'),
    ])),
    url(r'^user/(?P<username>[A-z0-9]{1,150})/', include([
        url(r'^$', views.user_profile, name='user_profile'),
        url(r'^ban', views.user_profile_ban_toggle, name='user_profile_ban_toggle'),
        url(r'^favourites', views.user_favorites, name='user_favourites'),
        url(r'^posts', views.user_posts, name='user_posts'),
    ])),
]
