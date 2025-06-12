from django.urls import path
from . import views

app_name = 'forms'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('create/', views.create_form, name='create_form'),
    path('edit/<uuid:form_id>/', views.edit_form, name='edit_form'),
    path('join/', views.join_form, name='join_form'),
    path('collaborate/<str:share_code>/', views.collaborate, name='collaborate'),
    path('api/fields/<int:field_id>/delete/', views.delete_field, name='delete_field'),
]
