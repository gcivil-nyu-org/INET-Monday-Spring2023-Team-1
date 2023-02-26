from django.http import HttpResponse
from django.shortcuts import  render, redirect
from django.contrib.auth import login
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib.auth import login, authenticate 
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout

from .forms import CustomUserCreationForm
from .models import CustomUser


# Create your views here.
def home(request):
    return HttpResponse("Hello DogHub users.")

def register_request(request):
	if request.method == "POST":
		form = CustomUserCreationForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, "Registration successful." )
			return redirect("events")
		messages.error(request, "Unsuccessful registration. Invalid information.")
	form = CustomUserCreationForm()
	return render (request=request, template_name="doghub_app/register.html", context={"register_form":form})

def login_request(request):
	if request.method == "POST":
		user_email=request.POST.get('uemail')
		password = request.POST.get('psw')
		try:
			user = CustomUser.objects.get(email= user_email)
		except:
			messages.error(request,'User Does Not Exist')
		user = authenticate(request, email=user_email, password = password)
		print(user_email)
		print(password)
		if user is not None:
			login(request, user)
			return redirect('events')
		else:
			messages.error(request, 'Wrong User Email or Password')
	return render(request=request, template_name="doghub_app/login.html")

@login_required
def events(request):
	if request.method == "GET":
	    return render(request=request, template_name="doghub_app/events_homepage.html")

def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.") # 
    return redirect("login")
