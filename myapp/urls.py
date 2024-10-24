from django.urls import path
from . import views

app_name = 'myapp'
urlpatterns = [
    path('resource/', views.get_resource),
]
