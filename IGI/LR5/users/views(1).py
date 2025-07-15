from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import CustomUserCreationForm, CustomUserChangeForm
from books.forms import CustomerForm
from books.models import Customer
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.views.decorators.csrf import ensure_csrf_cookie
import pytz

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('core:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def profile(request):
    try:
        customer = request.user.customer
    except Customer.DoesNotExist:
        customer = None

    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=request.user)
        customer_form = CustomerForm(request.POST, instance=customer)
        
        if user_form.is_valid() and customer_form.is_valid():
            user_form.save()
            # Always save customer data if the form is valid
            customer = customer_form.save(commit=False)
            customer.user = request.user
            customer.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('users:profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = CustomUserChangeForm(instance=request.user)
        customer_form = CustomerForm(instance=customer)
    
    return render(request, 'registration/profile.html', {
        'user_form': user_form,
        'customer_form': customer_form,
        'customer': customer
    })

@require_POST
@ensure_csrf_cookie
def set_timezone(request):
    try:
        timezone = request.POST.get('timezone')
        if timezone in pytz.all_timezones:
            request.session['django_timezone'] = timezone
            return JsonResponse({'status': 'success'})
        return JsonResponse({'status': 'error', 'message': 'Invalid timezone'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

@require_http_methods(["POST"])
def logout_view(request):
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('core:home') 