from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout, update_session_auth_hash
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from .forms import UserRegistrationForm, UserProfileForm
from .models import UserProfile

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/register.html', {'form': form})

@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '') or request.GET.get('username', '')
        password = request.POST.get('password', '') or request.GET.get('password', '')
        # Also support JSON body
        if not username:
            import json
            try:
                body = json.loads(request.body)
                username = body.get('username', '')
                password = body.get('password', '')
            except Exception:
                pass

        user = authenticate(request, username=username, password=password)
        wants_json = (
            request.headers.get('Accept', '').startswith('application/json') or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest' or
            request.headers.get('Content-Type', '').startswith('application/json')
        )

        if user is not None:
            login(request, user)
            if wants_json:
                return JsonResponse({'success': True, 'redirect': '/', 'username': username}, status=200)
            messages.success(request, f'Welcome back, {username}!')
            return redirect('home')
        else:
            if wants_json:
                return JsonResponse({'success': False, 'error': 'Invalid username or password.'}, status=401)
            messages.error(request, 'Invalid username or password.')
            form = AuthenticationForm()
    else:
        form = AuthenticationForm()
    return render(request, 'accounts/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')

@login_required
def profile_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=profile)

    return render(request, 'accounts/profile.html', {
        'form': form,
        'profile': profile
    })

@login_required
def change_password_view(request):
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            messages.success(request, 'Your password was successfully updated!')
            return redirect('profile')
        else:
            messages.error(request, 'Please correct the error below.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'accounts/change_password.html', {
        'form': form
    })
