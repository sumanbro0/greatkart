from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from core import settings
from .forms import ProfileForm
from .models import Profile
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    
    print(settings.BASE_DIR)
    return render(request, 'index.html')



def signup_view(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']

        if password == password2:
            try:
                validate_password(password)
            except ValidationError as e:
                messages.error(request, e.messages[0])
                return render(request, 'register.html')

            if User.objects.filter(email=email).exists():
                messages.error(request, 'Email already exists')
            else:
                user = User.objects.create_user(username=email, first_name=first_name, last_name=last_name, email=email, password=password)
                user.save()
                messages.success(request, 'You have successfully signed up. Please log in.')
                return redirect('login')
        else:
            messages.error(request, 'Passwords do not match')

    return render(request, 'register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'You have successfully logged in.')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'signin.html')


def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfully logged out.')
    return redirect('home')

@login_required
def update_profile(request):

    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)
        profile.full_name=request.user.first_name + ' ' + request.user.last_name
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your profile has been updated.')
            return redirect('me')
        else:
            print(form.errors.as_text())
            messages.error(request, 'Please correct the error below.' + form.errors.as_text())
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'update_profile.html', {'form': form})


@login_required
def my_profile(request):
    profile,created=Profile.objects.get_or_create(user=request.user)
    if created:
        profile.full_name=request.user.first_name + ' ' + request.user.last_name
        profile.save()
    return render(request, 'profiles.html', {'profile': profile})


@login_required
def orders(request):
    messages.error(request, 'This feature is not available yet.')
    return render(request, 'place-order.html')

@login_required
def me(request):
    return render(request, 'dashboard.html')