
from django import views
from django.urls import path
from webscraperapp import views
import os
csvfiles = {"filename":os.listdir(os.getcwd() + '/outputfiles')}

urlpatterns = [
    path('', views.home, name='home'),
    path('download/<str:filename1>', views.download_file, name = 'download_file'),
    path("login/", views.loginUser, name="login"),
    path("logout/", views.logoutUser, name="logout"),
    path('backup-names/', views.backup_names, name='backup-names'),
    path('backup-locations/', views.backup_locations, name='backup-locations'),
    # path('progress/', views.progress, name='progress'),
]