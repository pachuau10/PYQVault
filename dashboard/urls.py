from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard_home, name="dashboard_home"),
    path("pdfs/", views.dashboard_pdfs, name="dashboard_pdfs"),
    path("messages/", views.dashboard_messages, name="dashboard_messages"),
    path("analytics/", views.dashboard_analytics, name="dashboard_analytics"),
    path("settings/", views.dashboard_settings, name="dashboard_settings"),
    path("messages/<int:msg_id>/delete/", views.dashboard_delete_message, name="dashboard_delete_message"),
    path("logout/", views.dashboard_logout, name="dashboard_logout"),
]
