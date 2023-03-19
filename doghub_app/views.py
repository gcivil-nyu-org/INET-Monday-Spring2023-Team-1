# from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import CustomUser, UserProfile, DogProfile
from django.http import HttpResponse
from _version import __version__


# Create your views here.
def home(request):
    return HttpResponse(f"Welcome to DogHub {__version__}")


def register_request(request):
    if request.method == "POST":
        user_email = request.POST.get("reg_uemail")
        password = request.POST.get("reg_psw")
        if CustomUser.objects.filter(email=user_email).exists():
            messages.error(request, "User Exists")
        else:
            user = CustomUser.objects.create_user(
                username=user_email, email=user_email, password=password
            )
            login(request, user)
            request.session["uemail"] = user_email
            return redirect("register_details")

    return render(request=request, template_name="doghub_app/login.html")


def register_details_request(request):
    context = {}
    if request.method == "POST":
        user_profile = UserProfile(
            user_id=request.user,
            fname=request.POST.get("ufirstname"),
            lname=request.POST.get("ulastname"),
            bio=request.POST.get("uBio"),
            dob=request.POST.get("uDOB"),
        )
        user_profile.save()
        return redirect("events")
    if DogProfile.objects.filter(user_id=request.user).exists():
        dogprofiles = DogProfile.objects.filter(user_id=request.user)
        context = {"dogList": list(dogprofiles)}
    return render(
        request=request, template_name="doghub_app/register.html", context=context
    )


def dog_profile_create(request):
    if request.method == "POST":
        dog_profile = DogProfile(
            user_id=request.user,
            name=request.POST.get("dogName"),
            bio=request.POST.get("dogBio"),
            dob=request.POST.get("dogDOB"),
        )
        dog_profile.save()
        return redirect("register_details")
    return render(request=request, template_name="doghub_app/register.html")


def login_request(request):
    if request.method == "POST":
        user_email = request.POST.get("uemail")
        password = request.POST.get("psw")
        try:
            user = CustomUser.objects.get(email=user_email)
        except:  # noqa: E722
            messages.error(request, "User Does Not Exist")
        user = authenticate(request, email=user_email, password=password)
        print(user_email)
        print(password)
        if user is not None:
            login(request, user)
            return redirect("events")
        else:
            messages.error(request, "Wrong User Email or Password")
    return render(request=request, template_name="doghub_app/login.html")


@login_required
def events(request):
    if request.method == "GET":
        return render(request=request, template_name="doghub_app/events_homepage.html")


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")  #
    return redirect("login")


@login_required
def user_profile(request):
    # useri = CustomUser.objects.get(request.user)
    # CustomUser.objects.filter(email=request.user)
    # //user_email = user.email
    # //user = CustomUser.objects.get(email=user_email)
    # user_profile = UserProfile.objects.get('fname')
    # user=user_profile.user
    # first_name = user_profile.first_name
    user_prof = UserProfile.objects.get(user_id=request.user)
    # first_name = user_prof.fname
    # last_name = user_prof.lname
    context = {"userprof": user_prof, "user": request.user}
    # user = CustomUser.objects.get(uemail=request.email)
    # user_prof = UserProfile.objects.get(user=user)
    # print("User first name:", first_name )
    # print("User last name:", last_name)
    return render(
        request=request, template_name="doghub_app/user_profile.html", context=context
    )
