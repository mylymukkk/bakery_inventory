from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

from .forms import RegistrationForm, UpdateUserForm

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('user-login')
    else:
        form = RegistrationForm()

    context = {'form':form}

    return render(request, 'user/register.html', context)

@login_required
def profile(request):
    return render(request, 'user/profile.html')

@login_required
def profile_update(request):
    if request.method == 'POST':
        form = UpdateUserForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('user-profile')
    else:
        form = UpdateUserForm(instance=request.user)

    context = {'form':form}
    
    return render(request, 'user/profile_update.html', context)