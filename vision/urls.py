
from django.urls import path
from . import views

urlpatterns = [
    path('process_data/', views.process_data, name='process_data'),
]