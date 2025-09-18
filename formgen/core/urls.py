from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("forms/<int:org_id>/", views.get_forms, name="get_forms"),
    path("editor/<int:form_id>/", views.editor, name="editor"),
    path("api/create-form/", views.create_form, name="create_form"),
    path("api/import-form/", views.import_form, name="import_form"),
    path("api/save-form/<int:form_id>/", views.save_form_schema, name="save_form_schema"),
    path("api/delete-form/<int:form_id>/", views.delete_form, name="delete_form"),
]

