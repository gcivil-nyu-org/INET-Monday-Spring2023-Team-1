from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404
from django.conf import settings
from .models import CustomUser, UserProfile, DogProfile
from _version import __version__


# Create your views here.
def home(request):
    return HttpResponse(f"Welcome to DogHub {__version__}")


def register_request(request):
    context = {}
    context["version"] = __version__
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

    return render(
        request=request, template_name="doghub_app/login.html", context=context
    )


def register_details_request(request):
    context = {}
    if request.method == "POST":
        user_profile = UserProfile(
            user_id=request.user,
            fname=request.POST.get("ufirstname"),
            lname=request.POST.get("ulastname"),
            bio=request.POST.get("uBio"),
        )
        if "upic" in request.FILES:
            user_profile.pic = request.FILES["upic"]
        if request.POST.get("uDOB") != "":
            user_profile.dob = request.POST.get("uDOB")
        user_profile.save()
        return redirect("events")
    if DogProfile.objects.filter(user_id=request.user).exists():
        dogprofiles = DogProfile.objects.filter(user_id=request.user)
        context = {"dogList": list(dogprofiles), "media_url": settings.MEDIA_URL}
        for dog in dogprofiles:
            print(dog.pic)
    context["version"] = __version__
    return render(
        request=request, template_name="doghub_app/register.html", context=context
    )


def dog_profile_create(request):
    if request.method == "POST":
        dog_profile = DogProfile(
            user_id=request.user,
            name=request.POST.get("dogName"),
            bio=request.POST.get("dogBio"),
        )
        if "dogPic" in request.FILES:
            dog_profile.pic = request.FILES["dogPic"]
        if request.POST.get("dogDOB") != "":
            dog_profile.dob = request.POST.get("dogDOB")
        dog_profile.save()
        return redirect("register_details")
    return render(request=request, template_name="doghub_app/register.html")


def login_request(request):
    context = {}
    context["version"] = __version__
    if request.method == "POST":
        user_email = request.POST.get("uemail")
        password = request.POST.get("psw")
        try:
            user = CustomUser.objects.get(email=user_email)
        except CustomUser.DoesNotExist:  # noqa: E722
            messages.error(request, "User Does Not Exist")
            return render(request=request, template_name="doghub_app/login.html")
        user = authenticate(request, email=user_email, password=password)
        if user is not None:
            login(request, user)
            return redirect("events")
        else:
            messages.error(request, "Wrong User Email or Password")
    return render(
        request=request, template_name="doghub_app/login.html", context=context
    )


@login_required
def events(request):
    user_prof = UserProfile.objects.get(user_id=request.user)
    context = {"userprof": user_prof}
    if request.method == "GET":
        return render(
            request=request,
            template_name="doghub_app/events_homepage.html",
            context=context,
        )


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")  #
    return redirect("login")


@login_required
def user_profile(request):
    user_prof = UserProfile.objects.get(user_id=request.user)
    dog_prof = DogProfile.objects.filter(user_id=request.user)
    context = {
        "userprof": user_prof,
        "dogprof": list(dog_prof),
        "media_url": settings.MEDIA_URL,
    }
    return render(
        request=request, template_name="doghub_app/user_profile.html", context=context
    )


@login_required
def user_profile_edit(request):
    context = {}
    user_prof = UserProfile.objects.get(user_id=request.user)
    if request.method == "POST":
        user_prof.fname = request.POST.get("ufirstname")
        user_prof.lname = request.POST.get("ulastname")
        user_prof.bio = request.POST.get("uBio")
        if "upic" in request.FILES:
            user_prof.pic = request.FILES["upic"]
        if request.POST.get("uDOB") != "":
            user_prof.dob = request.POST.get("uDOB")
        user_prof.save()
        return redirect("user_profile")
    else:
        user_dob = user_prof.dob.strftime("%Y-%m-%d")
        context = {
            "user_prof": user_prof,
            "media_url": settings.MEDIA_URL,
            "user_dob": user_dob,
        }
    return render(request, "doghub_app/user_profile_edit.html", context=context)


@login_required
def dog_profile_edit(request, pk):
    context = {}
    dog_prof = get_object_or_404(DogProfile, pk=pk)

    if not dog_prof:
        raise Http404("Dog profile does not exist.")
    if request.method == "POST":
        dog_prof.name = request.POST.get("dogName")
        dog_prof.bio = request.POST.get("dogBio")
        if "dogPic" in request.FILES:
            dog_prof.pic = request.FILES["dogPic"]
        if request.POST.get("dogDOB") != "":
            dog_prof.dob = request.POST.get("dogDOB")
        dog_prof.save()
        return redirect("user_profile")
    else:
        dog_dob = dog_prof.dob.strftime("%Y-%m-%d")
        context = {
            "dog_prof": dog_prof,
            "media_url": settings.MEDIA_URL,
            "dog_dob": dog_dob,
        }
        print(dog_dob)
    return render(
        request=request,
        template_name="doghub_app/dog_profile_edit.html",
        context=context,
    )


@login_required
def dog_profile_add(request):
    context = {}
    if request.method == "POST":
        dog_profile = DogProfile(
            user_id=request.user,
            name=request.POST.get("dogName"),
            bio=request.POST.get("dogBio"),
        )
        if "dogPic" in request.FILES:
            dog_profile.pic = request.FILES["dogPic"]
        if request.POST.get("dogDOB") != "":
            dog_profile.dob = request.POST.get("dogDOB")
        dog_profile.save()
        return redirect("dog_profile_add")
    else:
        # dog_profile_form = DogProfileForm()
        if DogProfile.objects.filter(user_id=request.user).exists():
            dogprofiles = DogProfile.objects.filter(user_id=request.user)
            context = {"dogList": list(dogprofiles), "media_url": settings.MEDIA_URL}
            for dog in dogprofiles:
                print(dog.pic)
    return render(
        request=request,
        template_name="doghub_app/dog_profile_add.html",
        context=context,
    )


@login_required
def dog_profile_delete(request, pk):
    dog_profile = get_object_or_404(DogProfile, pk=pk)
    dog_profile.delete()
    return redirect("user_profile")
