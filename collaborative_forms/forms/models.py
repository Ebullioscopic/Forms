import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class Form(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forms')
    share_code = models.CharField(max_length=8, unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        return reverse('forms:collaborate', kwargs={'share_code': self.share_code})
    
    def save(self, *args, **kwargs):
        if not self.share_code:
            self.share_code = self.generate_share_code()
        super().save(*args, **kwargs)
    
    def generate_share_code(self):
        import random
        import string
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class FormField(models.Model):
    FIELD_TYPES = [
        ('text', 'Text'),
        ('number', 'Number'),
        ('email', 'Email'),
        ('dropdown', 'Dropdown'),
        ('textarea', 'Textarea'),
        ('checkbox', 'Checkbox'),
        ('radio', 'Radio'),
    ]
    
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='fields')
    label = models.CharField(max_length=200)
    field_type = models.CharField(max_length=20, choices=FIELD_TYPES)
    options = models.JSONField(default=list, blank=True)  # For dropdown/radio options
    is_required = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.form.title} - {self.label}"

class FormResponse(models.Model):
    form = models.OneToOneField(Form, on_delete=models.CASCADE, related_name='response')
    data = models.JSONField(default=dict)
    last_edited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    last_edited_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Response for {self.form.title}"

class ActiveUser(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='active_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    joined_at = models.DateTimeField(auto_now_add=True)
    last_seen = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['form', 'user']

class FieldLock(models.Model):
    form = models.ForeignKey(Form, on_delete=models.CASCADE, related_name='field_locks')
    field_id = models.CharField(max_length=100)
    locked_by = models.ForeignKey(User, on_delete=models.CASCADE)
    locked_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['form', 'field_id']
