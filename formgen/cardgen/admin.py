from django.contrib import admin
from .models import card_template, generated_card

@admin.register(card_template)
class CardTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'organisation', 'created_at', 'updated_at']
    list_filter = ['organisation', 'created_at']
    search_fields = ['name', 'organisation__name']

@admin.register(generated_card)
class GeneratedCardAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'created_at', 'updated_at']
    list_filter = ['template', 'created_at']
    search_fields = ['name', 'template__name']