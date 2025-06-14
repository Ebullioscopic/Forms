from rest_framework import serializers
from .models import Form, FormField, FormResponse

class FormFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormField
        fields = '__all__'

class FormSerializer(serializers.ModelSerializer):
    fields = FormFieldSerializer(many=True, read_only=True)
    
    class Meta:
        model = Form
        fields = ['id', 'title', 'description', 'share_code', 'is_active', 'created_at', 'fields']

class FormResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormResponse
        fields = '__all__'
