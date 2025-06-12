from django import forms
from .models import Form, FormField

class FormCreationForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class FormFieldForm(forms.ModelForm):
    options_text = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Enter options separated by new lines (for dropdown/radio fields)'
        }),
        help_text='One option per line'
    )
    
    class Meta:
        model = FormField
        fields = ['label', 'field_type', 'is_required']
        widgets = {
            'label': forms.TextInput(attrs={'class': 'form-control'}),
            'field_type': forms.Select(attrs={'class': 'form-select'}),
            'is_required': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean_options_text(self):
        options_text = self.cleaned_data.get('options_text', '')
        if options_text:
            return [opt.strip() for opt in options_text.split('\n') if opt.strip()]
        return []
    
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.options = self.cleaned_data['options_text']
        if commit:
            instance.save()
        return instance
