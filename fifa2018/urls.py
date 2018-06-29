from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home1, name='home'),
    path('schedule/', views.schedule, name='schedule'),
    path('admin/', views.admin, name='admin'),
    path('admin/8877', views.setdata1, name='admin'),
    path('cockpit/', views.cockpit, name='cockpit'),
    path('bet/', views.betlist, name='betList'),
    path('bet/<uuid:betid>', views.bet, name='bet'),
    path('fullreport/', views.fullreport, name='fullreport'),
    path('register/', views.RegisterFormView.as_view()),
]

