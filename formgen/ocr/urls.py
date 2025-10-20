from django.urls import path
from . import views

app_name = 'ocr'

urlpatterns = [
    path('', views.ocr_reader, name='reader'),
    path('extract', views.extract_ocr, name='extract'),
]

