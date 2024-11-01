from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('Data/',views.Data,name='Data'),
    path('Ratio/',views.Ratio,name='Ratio'),
    path('Contact/',views.Contact,name='Contact')
]
