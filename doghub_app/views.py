from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import Http404
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings
from .validators import validate_password

from doghub_app.tokens import verification_token_generator

from .forms import (
    CustomUserChangeForm,
    UserProfileForm,
    DogProfileForm,
    EventPostForm,
)
from .models import CustomUser, UserProfile, DogProfile, EventPost
from _version import __version__


# Create your views here.
def home(request):
    return HttpResponse(f"Welcome to DogHub {__version__}")


def forgot_password_page(request):
    return render(request=request, template_name="doghub_app/forgot_password_page.html")


def forgot_password_email(request):
    if request.method == "POST":
        user_email = request.POST.get("email_id")
        user = CustomUser.objects.filter(email=user_email).first()
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = PasswordResetTokenGenerator().make_token(user)
            reset_url = f"http://127.0.0.1:8000/reset_password/confirm/{uidb64}/{token}"

            email = EmailMessage(
                "Reset Password",
                f"Click the link to reset your password: {reset_url}",
                settings.EMAIL_HOST_USER,
                [user_email],
            )
            email.fail_silently = False
            email.send()
        else:
            messages.error(
                request, "The email you provided is not associated with an account."
            )

    return render(request=request, template_name="doghub_app/login.html")


def reset_password_page(request, uidb64, token):
    return render(request=request, template_name="doghub_app/reset_password.html")


def send_verification_email(user):
    token = verification_token_generator.make_token(user)
    verification_url = reverse("verify-email", kwargs={"token": token})
    subject = "Verify your email address"
    message = f"Hi {user.username},\n\nPlease click the following link to verify your email address:\n\n{settings.BASE_URL}{verification_url}"  # noqa: E501
    from_email = settings.EMAIL_HOST_USER
    recipient_list = [user.email]
    email = EmailMessage(
        subject,
        message,
        from_email,
        recipient_list,
    )
    email.fail_silently = False
    email.send()


@login_required
def verify_email(request, token):
    user = request.user
    if verification_token_generator.check_token(user, token):
        user.email_verified = True
        user.save()
        return redirect("register_details")
    else:
        return redirect("login")


def register_request(request):
    context = {}
    context["version"] = __version__
    if request.method == "POST":
        user_email = request.POST.get("reg_uemail")
        password = request.POST.get("reg_psw")
        errors = validate_password(password)

        if CustomUser.objects.filter(email=user_email).exists():
            messages.error(request, "User Exists")
        elif not password:
            messages.error(request, "Password is required")
        elif errors:
            context["errors"] = errors
            if len(errors) > 0:
                context['errorTitle'] = "Invalid Password"
                # messages.error(
                #     request,
                #     "There was an issue with your password. Please try again with a stronger password.",  # noqa: E501
                # )
        else:
            user = CustomUser.objects.create_user(
                username=user_email, email=user_email, password=password
            )
            login(request, user)
            send_verification_email(user)
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
    context = {"userprof": user_prof}  # noqa: F841

    event_posts = list(EventPost.objects.all())
    event_posts.reverse()
    return render(
        request, "doghub_app/events_homepage.html", {"event_posts": event_posts}
    )


# if request.method == "GET":
#    return render(
#       request=request,
#      template_name="doghub_app/events_homepage.html",
#     context=context,
# )


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

    context = {"dog_profile_form": dog_profile_form}
    if dog_profile_form.errors:
        context["form_errors"] = dog_profile_form.errors

    return render(
        request=request,
        template_name="doghub_app/dog_profile_add.html",
        context=context,
    )


@login_required
def dog_profile_delete(request, pk):
    dog_profile = get_object_or_404(DogProfile, pk=pk)
    if request.method == "POST":
        dog_profile.delete()
        return redirect("user_profile")
    return render(request=request, template_name="doghub_app/dog_profile_delete.html")


@login_required
def add_post(request):
    if request.method == "POST":
        event_post_form = EventPostForm(request.POST)
        if event_post_form.is_valid():
            event_post = event_post_form.save(commit=False)
            event_post.user_id = request.user
            event_post.save()
            return redirect("events")
    else:
        event_post_form = EventPostForm()

    context = {"event_post_form": event_post_form}
    return render(
        request=request, template_name="doghub_app/add_event.html", context=context
    )


# save every feature manually instead of form cause you cannot add a template
# look at the register page


def public_profile(request, email):
    user = CustomUser.objects.get(email=email)
    user_prof = UserProfile.objects.get(user_id=user.id)
    dog_prof = DogProfile.objects.filter(user_id=user.id)
    context = {
        "user": user,
        "userprof": user_prof,
        "dogprof": list(dog_prof),
        "media_url": settings.MEDIA_URL,
    }
    return render(
        request=request,
        template_name="doghub_app/public_user_profile.html",
        context=context,
    )
