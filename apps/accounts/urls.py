from django.urls import path, include
from . import views

urlpatterns = [
    path("", include("rest_auth.urls")),
    path("register/", views.register_view, name="ppast_register_user"),
    path("register/confirm/", views.conf_register_view, name="ppast_confirm_registration"),
    path("profile", views.user_profile_view, name="ppast_user_profile"),
    path("delete_profile", views.delete_profile_view, name="ppast_delete_profile"),
    path("profile/<int:user_id>/", views.user_profile_view, name="ppast_user_profile"),
    path("create_enterprise_member/", views.create_enterprise_member_view, name="create_enterprise_member"),
    path("delete_enterprise_member/<int:member_id>/<str:status>/", views.delete_enterprise_member_view, name="delete_enterprise_member"),
    path("create_enterprise_project_role/", views.create_enterprise_role_view, name="create_enterprise_role_view"),
    path("list_enterprise_project_role_view/", views.list_enterprise_project_role_view, name="list_enterprise_project_role_view"),
    path("update_enterprise_project_role/<int:role_id>/", views.update_enterprise_role_view, name="update_enterprise_role_view"),
    path("list_enterprise_project_role/<int:project_id>/", views.list_enterprise_role_view, name="list_enterprise_project_role"),
    path("user_licenses/", views.list_user_licenses_view, name="list_user_licenses"),
    path("list_user_licenses/", views.list_user_licenses_view, name="list_user_licenses"),
    path("list_enterprise_licenses/", views.list_enterprise_licenses_view, name="list_enterprise_licenses"),
    path("active_license/", views.active_licenses_view, name="active_license"),
    path("licenses_history/", views.list_licenses_history_view, name="licenses_history"),
    path("user_invoicehistory/<int:user_id>/", views.user_invoicehistory_view, name="user_invoicehistory"),
    path("user_claimhistory/<int:user_id>/", views.user_claimhistory_view, name="user_claimhistory"),
]
