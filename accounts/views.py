from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from .forms import UserRegistrationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout


def signup_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('board:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'accounts/signup.html', {'form': form})
