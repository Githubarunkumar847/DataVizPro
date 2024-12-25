from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),  # Directly point to the 'home' view
    path('download_plot/', views.download_plot, name='download_plot'),
]
