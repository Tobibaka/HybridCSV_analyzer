from django.db import models
from django.contrib.auth.models import User
import json


class Dataset(models.Model):
    """Model to store uploaded CSV datasets."""
    
    name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True
    )
    file_name = models.CharField(max_length=255)
    total_records = models.IntegerField(default=0)
    summary_data = models.TextField(default='{}')  # JSON string
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"{self.name} - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"
    
    def get_summary(self):
        """Return summary data as dictionary."""
        return json.loads(self.summary_data)
    
    def set_summary(self, data):
        """Set summary data from dictionary."""
        self.summary_data = json.dumps(data)


class EquipmentRecord(models.Model):
    """Model to store individual equipment records from uploaded CSV."""
    
    dataset = models.ForeignKey(
        Dataset, 
        on_delete=models.CASCADE, 
        related_name='records'
    )
    equipment_name = models.CharField(max_length=255)
    equipment_type = models.CharField(max_length=100)
    flowrate = models.FloatField(default=0.0)
    pressure = models.FloatField(default=0.0)
    temperature = models.FloatField(default=0.0)
    
    class Meta:
        ordering = ['equipment_name']
    
    def __str__(self):
        return f"{self.equipment_name} ({self.equipment_type})"
