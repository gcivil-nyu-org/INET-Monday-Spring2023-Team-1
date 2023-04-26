from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, update_session_auth_hash
from django.http import Http404
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.urls import reverse
from django.conf import settings
import logging
from .validators import validate_password
from doghub_app.tokens import verification_token_generator
from datetime import date
from .forms import (
    EventPostForm,
)
from .models import (
    CustomUser,
    Service,
    UserProfile,
    DogProfile,
    EventPost,
    Park,
    Chat,
    Attendee,
    Friends,
)
from _version import __version__
from datetime import datetime
from django.db.models import Q

import json


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
            reset_url = f"http://doghub-develop-env.eba-jymag3pg.us-west-2.elasticbeanstalk.com/reset_password/confirm/{uidb64}/{token}"  # noqa: E501

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
        if UserProfile.objects.filter(user_id=user.id).exists():
            return redirect("events")
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
                context["errorTitle"] = "Invalid Password"
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
            today = date.today()
            date_obj = datetime.strptime(user_profile.dob, "%Y-%m-%d").date()
            if date_obj >= date.today():
                messages.error(request, "Enter a valid Date of Birth")
                return redirect("register_details")
            elif (
                date.today().year
                - date_obj.year
                - ((today.month, today.day) < (date_obj.month, date_obj.day))
                < 18
            ):
                messages.error(
                    request, "For safety concerns, DogHub user should be 18+"
                )
                return redirect("register_details")
        else:
            messages.error(request, "Enter a valid Date of Birth.")
            return redirect("register_details")
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
            date_obj = datetime.strptime(dog_profile.dob, "%Y-%m-%d").date()
            if date_obj >= date.today() or date.today().year - date_obj.year > 31:
                messages.error(request, "Enter a valid Date of Birth")
                return redirect("register_details")
        else:
            messages.error(request, "Enter a valid Date of Birth")
            return redirect("register_details")
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
    try:
        user_prof = UserProfile.objects.get(user_id=request.user)
    except:  # noqa: E722
        return render(request, "doghub_app/register.html")

    context = {"userprof": user_prof}  # noqa: F841
    park = list(Park.objects.all())
    event_posts = list(EventPost.objects.all())
    event_posts.reverse()
    event_ls = []
    for event in event_posts:
        cur_event = {}
        cur_event["event_info"] = event
        cur_event["hostname"] = CustomUser.objects.get(id=event.user_id.id).username
        if event.user_id == request.user:
            cur_event["host"] = True
        else:
            cur_event["host"] = False
        if Attendee.objects.filter(event_id=event.event_id, user_id=request.user):
            cur_event["attendee"] = True
        else:
            cur_event["attendee"] = False
        event_ls.append(cur_event)

    friends = Friends.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user), pending=False
    )
    user_profiles = []
    for friend in friends:
        if friend.sender == request.user:
            friend_user = friend.receiver
        else:
            friend_user = friend.sender
        friend_profile = UserProfile.objects.get(user_id=friend_user.id)
        user_profiles.append(
            {
                "fname": friend_profile.fname,
                "lname": friend_profile.lname,
                "email": friend_user.email,
                "pic": friend_profile.pic,
            }
        )

        context = {
            "userprof": user_prof,
            "event_posts": event_ls,
            "media_url": settings.MEDIA_URL,
            "park": park,
            "user_profiles": user_profiles,
        }  # noqa: F841

    return render(request, "doghub_app/events_homepage.html", context=context)


def logout_request(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")  #
    return redirect("login")


@login_required
def user_profile(request):
    try:
        user_prof = UserProfile.objects.get(user_id=request.user)
    except:  # noqa: E722
        return render(request, "doghub_app/register.html")

    dog_prof = DogProfile.objects.filter(user_id=request.user)
    events_list = list(EventPost.objects.filter(user_id=request.user))
    attendee_events = list(Attendee.objects.filter(user_id=request.user))
    for attendee in attendee_events:
        event = EventPost.objects.get(event_id=attendee.event_id.event_id)
        if event.user_id != request.user:
            print(event)
            events_list.append(event)
    print(events_list)
    context = {
        "userprof": user_prof,
        "dogprof": dog_prof,
        "media_url": settings.MEDIA_URL,
        "events_list": events_list,
    }
    if request.method == "POST":
        if "save_password" in request.POST:
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")
            confirm_password = request.POST.get("confirm_password")
            errors = []

            # Check if the current password is correct
            if not request.user.check_password(current_password):
                errors.append("Current password is incorrect.")
                # errors.append("Current password is incorrect.")
                # return redirect('user_profile')

            # Check if the new password and confirmation match
            if new_password != confirm_password:
                errors.append("New password and confirmation do not match.")
                # return redirect('user_profile')

            password_errors = validate_password(new_password)
            if password_errors:
                errors.extend(password_errors)

            if errors:
                context["errors"] = errors
                if len("errors") > 0:
                    messages.error(
                        request,
                        "For you and your dog's safety, please choose a strong password.",  # noqa: #501
                    )
            else:
                # Change the user's password
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)
                messages.success(request, "Password has been changed.")
                return redirect("user_profile")
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
            today = date.today()
            user_prof.dob = request.POST.get("uDOB")
            date_obj = datetime.strptime(user_prof.dob, "%Y-%m-%d").date()
            if date_obj >= date.today():
                messages.error(request, "Enter a valid Date of Birth")
                return redirect("user_profile_edit")
            elif (
                date.today().year
                - date_obj.year
                - ((today.month, today.day) < (date_obj.month, date_obj.day))
                < 18
            ):
                messages.error(
                    request, "For safety concerns, DogHub user should be 18+"
                )
                return redirect("user_profile_edit")
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
            date_obj = datetime.strptime(dog_prof.dob, "%Y-%m-%d").date()
            if date_obj >= date.today() or date.today().year - date_obj.year > 31:
                messages.error(request, "Enter a valid Date of Birth")
                return redirect("dog_profile_edit", pk=dog_prof.pk)
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
            logging.error("here", request.POST.get("dogDOB"))
        if request.POST.get("dogDOB") != "":
            dog_profile.dob = request.POST.get("dogDOB")
            date_obj = datetime.strptime(dog_profile.dob, "%Y-%m-%d").date()
            if date_obj >= date.today() or date.today().year - date_obj.year > 31:
                messages.error(request, "Enter a valid Date of Birth")
                return redirect("dog_profile_add")
        else:
            messages.error(request, "Enter a valid Date of Birth")
            return redirect("dog_profile_add")
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
def dog_profile_delete(request, name):
    dog_name = request.POST.get("dog_name")
    dog_id = request.POST.get("dog_id")
    dog_profile = DogProfile.objects.get(dog_id=dog_id)
    # dog_id = request.POST.get('dog_name')
    # logging.debug("Dog name",dog_id)
    # fet =  DogProfile.objects.get(dog_id=int(dog_id))
    # logging.debug("Deleting dog",dog_profile.name)
    logging.debug("DELETING")
    logging.debug(str(dog_name))
    dog_profile.delete()
    return redirect("user_profile")


@login_required
def add_post(request):
    current_datetime = datetime.now().strftime("%Y-%m-%dT%H:%M")
    parks = list(Park.objects.values())
    park_data = json.dumps(parks)
    # park_data = Park.objects.all()
    # park_data_list = list(park_data)
    if request.method == "POST":
        event_post_form = EventPostForm(request.POST)
        if event_post_form.is_valid():
            event_post = event_post_form.save(commit=False)

            event_post = EventPost(
                event_title=request.POST.get("event_title"),
                event_description=request.POST.get("event_description"),
                event_time=request.POST.get("event_time"),
            )

            location = request.POST.get("location")
            if "," not in location:
                messages.error(request, "Invalid location format")
                return redirect("add_post")
            latitude, longitude = location.split(",")
            # latitude, longitude = location[0], location[1]
            try:
                park = Park.objects.get(latitude=latitude, longitude=longitude)
            except Park.DoesNotExist:
                messages.error(request, "No park found for the given info")
                return redirect("add_post")
            event_post.park_id = park

            user = request.user
            user = CustomUser.objects.get(id=user.id)
            if not user.email_verified:
                messages.error(request, "Verify your email before posting an Event.")
                return redirect("events")

            event_post.user_id = request.user
            event_post.save()
            attendee = Attendee(user_id=request.user, event_id=event_post)
            attendee.save()
            messages.success(request, "Your post has been added!")
            return redirect("events")
    else:
        event_post_form = EventPostForm()

    context = {
        "event_post_form": event_post_form,
        "current_datetime": current_datetime,
        "park_data": park_data,
    }
    return render(
        request=request, template_name="doghub_app/add_event.html", context=context
    )


@login_required
def public_profile(request, email):
    if CustomUser.objects.filter(email=email).exists():
        user = CustomUser.objects.get(email=email)
        public_prof = UserProfile.objects.get(user_id=user.id)
        dog_prof = DogProfile.objects.filter(user_id=user.id)
        events_list = EventPost.objects.filter(user_id=request.user.id)
        user_prof = UserProfile.objects.get(user_id=request.user.id)
        friend = get_object_or_404(CustomUser, email=email)
        friend_request_sent = Friends.objects.filter(
            sender=request.user, receiver=friend, pending=True
        ).first()

        context = {
            "user": user,
            "public_prof": public_prof,
            "dogprof": list(dog_prof),
            "media_url": settings.MEDIA_URL,
            "events_list": list(events_list),
            "userprof": user_prof,
            "friend": friend,
            "friend_request_sent": friend_request_sent,
        }
        return render(
            request=request,
            template_name="doghub_app/public_user_profile.html",
            context=context,
        )
    else:
        return HttpResponse("User not found.")


@login_required
def search_user(request):
    if request.method == "POST":
        # f = open("output.txt", "w+")
        user_prof = UserProfile.objects.get(user_id=request.user.id)
        show_users = False
        show_events = False
        show_services = False
        searched = request.POST["searched"]

        if request.POST.get("filter_users") == "users":
            show_users = True

        if request.POST.get("filter_events") == "events":
            show_events = True

        if request.POST.get("filter_services") == "services":
            show_services = True

        user_profiles_fname = list(
            UserProfile.objects.filter(fname__icontains=searched)
        )
        user_profiles_lname = list(
            UserProfile.objects.filter(lname__icontains=searched)
        )
        users_list = []
        users_list.extend(user_profiles_fname)
        users_list.extend(user_profiles_lname)

        u_list = []
        for user in users_list:
            user_id = user.user_id
            user_object = CustomUser.objects.get(id=user_id.id)
            d = {
                "fname": user.fname,
                "lname": user.lname,
                "email": user_object.email,
                "pic": user.pic,
            }
            u_list.append(d)

        events = EventPost.objects.filter(event_title__icontains=searched)
        services = Service.objects.filter(title__contains=searched)

        return render(
            request,
            "doghub_app/search-results.html",
            {
                "searched": searched,
                "user_profiles_fname": user_profiles_fname,
                "user_profiles_lname": user_profiles_lname,
                "events": events,
                "services": services,
                "users_list": users_list,
                "u_list": u_list,
                "show_users": show_users,
                "show_events": show_events,
                "show_services": show_services,
                "media_url": settings.MEDIA_URL,
                "userprof": user_prof,
            },
        )
    else:
        return render(request, "doghub_app/search-results.html", {})


@login_required
def inbox(request):
    context = {}
    if request.method == "POST":
        print(request)
        receiver = CustomUser.objects.get(pk=request.POST.get("receiver"))
        message = Chat(
            receiver=receiver, text=request.POST.get("message"), sender=request.user
        )
        message.save()
        return HttpResponse(status=200)
    if Chat.objects.filter(receiver=request.user).exists():
        messages = list(Chat.objects.filter(receiver=request.user))
        messages.reverse()
        context["messageList"] = messages
    friendsLs = []
    if Friends.objects.filter(receiver=request.user, pending=False).exists():
        for relationship in list(
            Friends.objects.filter(receiver=request.user, pending=False)
        ):
            friendsLs.append(relationship.sender)
    if Friends.objects.filter(sender=request.user, pending=False).exists():
        for relationship in list(
            Friends.objects.filter(sender=request.user, pending=False)
        ):
            if relationship.receiver not in friendsLs:
                friendsLs.append(relationship.receiver)
    context["friendsLs"] = friendsLs

    return render(request, "doghub_app/inbox.html", context=context)


@login_required
def rsvp_event(request, pk):
    event = get_object_or_404(EventPost, pk=pk)
    if request.method == "POST":
        if Attendee.objects.filter(event_id=pk, user_id=request.user):
            Attendee.objects.filter(event_id=pk, user_id=request.user).delete()
        else:
            rsvp = Attendee(event_id=event, user_id=request.user)
            rsvp.save()
    return HttpResponse(status=200)


@login_required
def add_friend(request, email):
    friend = get_object_or_404(CustomUser, email=email)
    if request.user == friend:
        messages.warning(request, "You cannot add yourself as a friend.")
        return redirect("public-profile", email=email)

    if Friends.objects.filter(sender=request.user, receiver=friend).exists():
        messages.warning(
            request, f"You have already sent a friend request to {friend.email}."
        )
        return redirect("public-profile", email=email)

    if Friends.objects.filter(
        sender=friend, receiver=request.user, pending=True
    ).exists():
        messages.warning(
            request, f"{friend.email} has already sent you a friend request."
        )
        return redirect("public-profile", email=email)

    Friends.objects.create(sender=request.user, receiver=friend, pending=True)
    messages.success(request, f"Friend request sent to {friend.email}.")
    return redirect("public-profile", email=email)


# @login_required
# def friend_requests(request):
#    incoming_requests = Friends.objects.filter(receiver=request.user, pending=True)
#    outgoing_requests = Friends.objects.filter(sender=request.user, pending=True)
#
#    context = {
#        "incoming_requests": incoming_requests,
#        "outgoing_requests": outgoing_requests,
#    }
#    return render(request, "doghub_app/friend_requests.html", context)
@login_required
def friend_requests(request):
    friend_requests = Friends.objects.filter(receiver=request.user, pending=True)
    # friend_profiles=[]
    # userprof = UserProfile.objects.get(user_id=request.user)
    # for friend in friend_requests:
    #     if friend.receiver == request.user:
    #         friend_user = friend.sender
    #     else:
    #         friend_user = friend.receiver
    #     friend_profile = UserProfile.objects.get(user_id=friend_user.id)
    #     friend_profiles.append(
    #         {
    #             "fname": friend_profile.fname,
    #             "lname": friend_profile.lname,
    #             "email": friend_user.email,
    #             "pic": friend_profile.pic,
    #         }
    #     )
    # context = {
    #     "friend_profiles": friend_profiles,
    #     "media_url": settings.MEDIA_URL,
    #     "userprof": userprof,
    # }
    return render(
        request, "doghub_app/friend_requests.html", {"friend_requests": friend_requests}
    )


@login_required
def accept_friend_request(request, fid):
    friend_request = get_object_or_404(
        Friends, fid=fid, receiver=request.user, pending=True
    )
    friend_request.pending = False
    friend_request.save()

    messages.success(
        request, f"You are now friends with {friend_request.sender.email}."
    )
    return redirect("friend_requests")


@login_required
def decline_friend_request(request, fid):
    friend_request = get_object_or_404(
        Friends, fid=fid, receiver=request.user, pending=True
    )
    friend_request.delete()

    messages.success(request, "Friend request declined.")
    return redirect("friend_requests")


@login_required
def friends(request):
    friends = Friends.objects.filter(
        Q(sender=request.user) | Q(receiver=request.user), pending=False
    )
    user_profiles = []
    userprof = UserProfile.objects.get(user_id=request.user)
    for friend in friends:
        if friend.sender == request.user:
            friend_user = friend.receiver
        else:
            friend_user = friend.sender
        friend_profile = UserProfile.objects.get(user_id=friend_user.id)
        user_profiles.append(
            {
                "fname": friend_profile.fname,
                "lname": friend_profile.lname,
                "email": friend_user.email,
                "pic": friend_profile.pic,
            }
        )
    context = {
        "user_profiles": user_profiles,
        "media_url": settings.MEDIA_URL,
        "userprof": userprof,
    }
    return render(request, "doghub_app/friends.html", context)
