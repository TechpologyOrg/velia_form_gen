from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='cardgen_index'),
    path('org/<int:org_id>/', views.get_card_templates, name='cardgen_templates'),
    path('editor/<int:template_id>/', views.editor, name='cardgen_editor'),
    path('create/', views.create_card_template, name='create_card_template'),
    path('save/<int:template_id>/', views.save_card_template_schema, name='save_card_template_schema'),
    path('import/', views.import_card_template, name='import_card_template'),
    path('delete/<int:template_id>/', views.delete_card_template, name='delete_card_template'),
    path('generate/<int:template_id>/', views.generate_card, name='generate_card'),
]
