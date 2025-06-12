from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Form, FormField, FormResponse
from .forms import FormCreationForm, FormFieldForm

@login_required
def dashboard(request):
    if request.user.is_admin():
        user_forms = Form.objects.filter(creator=request.user).order_by('-created_at')
    else:
        user_forms = []
    
    return render(request, 'forms/dashboard.html', {
        'user_forms': user_forms,
        'is_admin': request.user.is_admin(),
    })

@login_required
def create_form(request):
    if not request.user.is_admin():
        messages.error(request, 'Only admins can create forms.')
        return redirect('forms:dashboard')
    
    if request.method == 'POST':
        form = FormCreationForm(request.POST)
        if form.is_valid():
            new_form = form.save(commit=False)
            new_form.creator = request.user
            new_form.save()
            messages.success(request, f'Form created successfully! Share code: {new_form.share_code}')
            return redirect('forms:edit_form', form_id=new_form.id)
    else:
        form = FormCreationForm()
    
    return render(request, 'forms/create_form.html', {'form': form})

@login_required
def edit_form(request, form_id):
    form_obj = get_object_or_404(Form, id=form_id, creator=request.user)
    fields = form_obj.fields.all().order_by('order')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add_field':
            field_form = FormFieldForm(request.POST)
            if field_form.is_valid():
                field = field_form.save(commit=False)
                field.form = form_obj
                field.order = fields.count()
                field.save()
                messages.success(request, 'Field added successfully!')
                return redirect('forms:edit_form', form_id=form_id)
    
    field_form = FormFieldForm()
    return render(request, 'forms/edit_form.html', {
        'form_obj': form_obj,
        'fields': fields,
        'field_form': field_form,
    })

@login_required
def join_form(request):
    if request.method == 'POST':
        share_code = request.POST.get('share_code', '').upper()
        try:
            form = Form.objects.get(share_code=share_code, is_active=True)
            return redirect('forms:collaborate', share_code=share_code)
        except Form.DoesNotExist:
            messages.error(request, 'Invalid share code or form is not active.')
    
    return render(request, 'forms/join_form.html')

@login_required
def collaborate(request, share_code):
    form = get_object_or_404(Form, share_code=share_code, is_active=True)
    return render(request, 'forms/collaborate.html', {
        'form': form,
        'share_code': share_code,
    })

@require_http_methods(["DELETE"])
@login_required
def delete_field(request, field_id):
    field = get_object_or_404(FormField, id=field_id, form__creator=request.user)
    field.delete()
    return JsonResponse({'success': True})
