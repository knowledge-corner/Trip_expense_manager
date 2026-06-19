from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.backup_page, name="backup_page"),
    path("download/", views.backup_download, name="backup_download"),
    path("restore/", views.backup_restore, name="backup_restore"),
    path("expense-template/", views.expense_import_template, name="expense_import_template"),
    path("trips/<int:trip_id>/import/", views.expense_import, name="expense_import"),
]
