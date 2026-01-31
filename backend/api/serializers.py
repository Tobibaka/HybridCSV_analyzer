from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Dataset, EquipmentRecord


class EquipmentRecordSerializer(serializers.ModelSerializer):
    """Serializer for individual equipment records."""
    
    class Meta:
        model = EquipmentRecord
        fields = [
            'id', 
            'equipment_name', 
            'equipment_type', 
            'flowrate', 
            'pressure', 
            'temperature'
        ]


class DatasetListSerializer(serializers.ModelSerializer):
    """Serializer for dataset list view."""
    
    uploaded_by_username = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 
            'name', 
            'uploaded_at', 
            'uploaded_by_username',
            'file_name', 
            'total_records'
        ]
    
    def get_uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else 'Anonymous'


class DatasetDetailSerializer(serializers.ModelSerializer):
    """Serializer for detailed dataset view with records."""
    
    records = EquipmentRecordSerializer(many=True, read_only=True)
    uploaded_by_username = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    
    class Meta:
        model = Dataset
        fields = [
            'id', 
            'name', 
            'uploaded_at', 
            'uploaded_by_username',
            'file_name', 
            'total_records',
            'summary',
            'records'
        ]
    
    def get_uploaded_by_username(self, obj):
        return obj.uploaded_by.username if obj.uploaded_by else 'Anonymous'
    
    def get_summary(self, obj):
        return obj.get_summary()


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user registration and info."""
    
    password = serializers.CharField(write_only=True, min_length=6)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
    
    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login."""
    
    username = serializers.CharField()
    password = serializers.CharField()
