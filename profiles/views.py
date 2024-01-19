from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from .models import Address, Profile
from django.contrib.auth.decorators import login_required
from .forms import ProfileForm

# Create your views here.
def index(request):
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
    if request.method == 'POST':
        profile = Profile.objects.get(user=request.user)
        avatar = request.FILES.get('avatar')
        if avatar:
            profile.avatar = avatar
        profile.full_name = request.POST.get('full_name')
        profile.bio = request.POST.get('bio')
        profile.save()
        # profile_html = render_to_string('profiles.html', {'profile': profile}, request=request)
        # return HttpResponse(profile_html)
        return render(request, 'profiles.html', {'profile': profile})
    return redirect('me')
    

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

@login_required
def add_address(request):
    addresses = Address.objects.filter(profile__user=request.user)
    if request.method == "POST":
        address = request.POST.get('address')
        city = request.POST.get('city')
        state = request.POST.get('state')
        country = request.POST.get('country')
        zip_code = request.POST.get('zip_code')
        address,created=Address.objects.get_or_create(address=address, city=city, state=state, country=country, zip_code=zip_code, profile=request.user.profile)
        if created:
            messages.success(request, 'Address has been added.')
        else:
            messages.error(request, 'Address already exists.')
    return render(request, 'add_address.html', {'addresses': addresses})


@login_required
def delete_address(request, pk):
    if pk:
        address = Address.objects.get(id=pk)
        address.delete()
        messages.success(request, 'Address has been deleted.')
    return redirect('address')
