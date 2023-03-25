from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404


from .forms import (
    CustomUserChangeForm,
    UserProfileForm,
    DogProfileForm,
)
from .models import CustomUser, UserProfile, DogProfile
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
        except CustomUser.DoesNotExist:  # noqa: E722
            messages.error(request, "User Does Not Exist")
            return render(request=request, template_name="doghub_app/login.html")
        user = authenticate(request, email=user_email, password=password)
        if user is not None:
            login(request, user)
            return redirect("events")
        else:
            messages.error(request, "Wrong User Email or Password")
    return render(request=request, template_name="doghub_app/login.html")


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
    context = {"userprof": user_prof, "dogprof": dog_prof}
    return render(
        request=request, template_name="doghub_app/user_profile.html", context=context
    )


@login_required
def user_profile_edit(request):
    user = request.user
    user_prof = UserProfile.objects.get(user_id=request.user)
    if request.method == "POST":
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user_prof)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect("user_profile")
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_form = UserProfileForm(instance=user_prof)
    return render(
        request,
        "doghub_app/user_profile_edit.html",
        {"user_form": user_form, "profile_form": profile_form},
    )


@login_required
def dog_profile_edit(request, pk):
    dog_prof = get_object_or_404(DogProfile, pk=pk)
    if not dog_prof:
        raise Http404("Dog profile does not exist.")
    if request.method == "POST":
        form = DogProfileForm(request.POST, request.FILES, instance=dog_prof)
        if form.is_valid():
            form.save()
            return redirect("user_profile")
    else:
        form = DogProfileForm(instance=dog_prof)
    return render(
        request=request,
        template_name="doghub_app/dog_profile_edit.html",
        context={"form": form},
    )

@login_required
def dog_profile_add(request):
    if request.method == "POST":
        dog_profile_form = DogProfileForm(request.POST, request.FILES)
        if dog_profile_form.is_valid():
            dog_profile = dog_profile_form.save(commit=False)
            dog_profile.user_id = request.user
            dog_profile.save()
            return redirect("user_profile")
    else:
        dog_profile_form = DogProfileForm()
        
    context = {'dog_profile_form': dog_profile_form}
    if dog_profile_form.errors:
        context['form_errors'] = dog_profile_form.errors

    return render(request=request, template_name="doghub_app/dog_profile_add.html", context=context)

@login_required
def dog_profile_delete(request, pk):
    dog_profile = get_object_or_404(DogProfile, pk=pk)
    if request.method == "POST":
        dog_profile.delete()
        return redirect("user_profile")
    return render(request=request, template_name="doghub_app/dog_profile_delete.html")

#save every feature manually instead of form cause you cannot add a template
#look at the register page

