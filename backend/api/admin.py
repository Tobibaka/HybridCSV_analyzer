from django.contrib import admin
from .models import Dataset, EquipmentRecord


@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ['name', 'file_name', 'total_records', 'uploaded_at', 'uploaded_by']
    list_filter = ['uploaded_at']
    search_fields = ['name', 'file_name']


@admin.register(EquipmentRecord)
class EquipmentRecordAdmin(admin.ModelAdmin):
    list_display = ['equipment_name', 'equipment_type', 'flowrate', 'pressure', 'temperature', 'dataset']
    list_filter = ['equipment_type', 'dataset']
    search_fields = ['equipment_name']
