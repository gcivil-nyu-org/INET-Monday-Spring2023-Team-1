from django.test import TestCase, Client
from django.urls import reverse

# import logging

# from django.utils import timezone
# from datetime import datetime
from django.contrib.auth import get_user_model

from unittest.mock import patch

from doghub_app.models import (
    CustomUser,
    UserProfile,
    DogProfile,
    Tag,
    Park,
    EventPost,
    Attendee,
    Chat,
    Friends,
    Groups,
    GroupMember,
)

from doghub_app.tokens import verification_token_generator

# from .forms import EventPostForm
from . import validators
from django.core import mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import get_messages
from doghub.settings import BASE_DIR
import pathlib
import yaml
from datetime import date, timedelta

# import logging

# from django.contrib.messages.middleware import MessageMiddleware


class HomeViewTestCase(TestCase):
    def test_home_view(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response, "Welcome"
        )  # Check if the response contains "DogHub"


class ResgisterViewTestCase(TestCase):
    def setUp(self):
        self.user_email = "testuser@example.com"
        self.password = "Test@password1"

    def test_register_request_valid(self):
        data = {
            "reg_uemail": self.user_email,
            "reg_psw": self.password,
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 0)
        self.assertEqual(DogProfile.objects.count(), 0)

    def test_register_request_existing_user(self):
        user = get_user_model().objects.create_user(  # noqa: F841
            username=self.user_email, email=self.user_email, password=self.password
        )
        data = {
            "reg_uemail": self.user_email,
            "reg_psw": self.password,
        }
        response = self.client.post(reverse("register"), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "User Exists")
        self.assertEqual(CustomUser.objects.count(), 1)
        self.assertEqual(UserProfile.objects.count(), 0)
        self.assertEqual(DogProfile.objects.count(), 0)


class RegisterDetailsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.register_url = reverse("register_details")
        self.dog_register_url = reverse("dogProfileCreate")
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser@test.com",
            email="testuser@test.com",
            password="testpass123",
        )
        self.client.login(email=self.user.email, password="testpass123")
        self.user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Test user bio",
            "uDOB": "2000-01-01",
        }
        self.dog_profile_data = {
            "dogName": "Test Dog",
            "dogBio": "Test dog bio",
            "dogDOB": "2010-01-01",
        }

    def test_register_details_request_success(self):
        response = self.client.post(self.register_url, data=self.user_profile_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(UserProfile.objects.filter(user_id=self.user).exists())
        self.assertRedirects(response, reverse("events"))

    def test_register_details_request_get(self):
        response = self.client.get(self.register_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doghub_app/register.html")


class LoginTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser@test.com",
            email="testuser@test.com",
            password="testpass123",
        )

    def test_login_success(self):
        self.user_data = {
            "uemail": "testuser@test.com",
            "psw": "testpass123",
        }
        response = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CustomUser.objects.filter(email=self.user_data["uemail"]).exists()
        )

    def test_login_failure(self):
        self.user_data = {
            "uemail": "none@test.com",
            "psw": "testpass123",
        }
        response = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(
            CustomUser.objects.filter(email=self.user_data["uemail"]).exists()
        )


class ValidatorTestCase(TestCase):
    def test_validate_password(self):
        # Test a valid password
        assert validators.validate_password("Abcdefg1!") == []

        # Test a password with less than 8 characters
        assert validators.validate_password("Abcd1!") == [
            "Password must be at least 8 characters long."
        ]

        # Test a password with no digits
        assert validators.validate_password("Abcdefg!") == [
            "Password must contain at least one digit."
        ]

        # Test a password with no uppercase letters
        assert validators.validate_password("abcdefg1!") == [
            "Password must contain at least one uppercase letter."
        ]

        # Test a password with no lowercase letters
        assert validators.validate_password("ABCDEFG1!") == [
            "Password must contain at least one lowercase letter."
        ]

        # Test a password with no special characters
        assert validators.validate_password("Abcdefg1") == [
            "Password must contain at least one special character."
        ]

        # Test a password with multiple errors
        assert validators.validate_password("abc12") == [
            "Password must be at least 8 characters long.",
            "Password must contain at least one uppercase letter.",
            "Password must contain at least one special character.",
        ]


class ForgotPasswordTestDemo(TestCase):
    def test_forgot_password_page(self):
        # Test that the view returns a status code of 200
        response = self.client.get(reverse("forgot_password_page"))
        self.assertEqual(response.status_code, 200)

        # Test that the correct template is used
        response = self.client.get(reverse("forgot_password_page"))
        self.assertTemplateUsed(response, "doghub_app/forgot_password_page.html")

    def setUp(self):
        self.client = Client()
        self.url = reverse("forgot_password_email")
        self.user = CustomUser.objects.create_user(
            email="test@example.com", username="testuser", password="testpassword"
        )

    def test_forgot_password_email_success(self):
        # Test sending a password reset email successfully
        with patch.object(
            PasswordResetTokenGenerator, "make_token", return_value="testtoken"
        ):
            response = self.client.post(self.url, {"email_id": "test@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn("Reset Password", mail.outbox[0].subject)
        self.assertIn(
            "http://doghub-develop-env.eba-jymag3pg.us-west-2.elasticbeanstalk.com/reset_password/confirm",  # noqa: E501
            mail.outbox[0].body,
        )

    def test_forgot_password_email_invalid_email(self):
        # Test providing an invalid email address
        with patch.object(
            PasswordResetTokenGenerator, "make_token", return_value="testtoken"
        ):
            response = self.client.post(self.url, {"email_id": "invalid@example.com"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(mail.outbox), 0)
        self.assertContains(
            response, "The email you provided is not associated with an account."
        )


class VerifyEmailViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.token = verification_token_generator.make_token(self.user)
        self.url = reverse("verify-email", kwargs={"token": self.token})

    def test_verify_email_valid_token(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("register_details"))
        self.user.refresh_from_db()
        self.assertTrue(self.user.email_verified)

    def test_verify_email_invalid_token(self):
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("verify-email", kwargs={"token": "invalid-token"})
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("login"))
        self.user.refresh_from_db()
        self.assertFalse(self.user.email_verified)


class LogoutRequestViewTestCase(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass"
        )
        self.login_url = reverse("login")
        self.logout_url = reverse("logout")

    def test_logout_request(self):
        self.client.force_login(self.user)
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.login_url)
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "You have successfully logged out.")


class AddPostViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser@test.com",
            email="testuser@test.com",
            password="Test@123",
            email_verified=True,
        )
        # self.user = get_user_model().objects.create_user(
        #   username="testuser", email="test@example.com", password="Test@123")
        self.park = Park.objects.create(
            name="Test Fishbridge",
            latitude="40.709070274158",
            longitude="-74.0013770043858",
        )
        self.url = reverse("add_post")
        self.valid_data = {
            "user_id": self.user,
            "event_title": "Test Event",
            "event_description": "This is a test event",
            "event_time": "2025-04-08T12:00",
            "location": "40.709070274158,-74.0013770043858",
        }

    def test_add_post_view_with_valid_data(self):
        self.client.login(username="testuser@test.com", password="Test@123")
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventPost.objects.count(), 1)  # noqa: F821
        event_post = EventPost.objects.first()  # noqa: F821
        self.assertEqual(event_post.event_title, self.valid_data["event_title"])
        self.assertEqual(
            event_post.event_description, self.valid_data["event_description"]
        )
        self.assertEqual(
            event_post.event_time.strftime("%Y-%m-%dT%H:%M"),
            self.valid_data["event_time"],
        )
        self.assertEqual(event_post.park_id, self.park)
        self.assertEqual(event_post.user_id, self.user)

    def test_add_post_view_with_invalid_data(self):
        self.client.login(username="testuser", password="Test@123")
        invalid_data = self.valid_data.copy()
        invalid_data["event_title"] = ""
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 302)
        # self.assertContains(response, 'Please fill out this field.')

    def test_add_post_view_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login?next=" + self.url)

    def test_add_post_view_with_unverified_user(self):
        self.user.email_verified = False
        self.user.save()
        self.client.login(username="testuser", password="Test@123")
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        # self.events_url = reverse("events")
        self.assertRedirects(response, "/login?next=" + self.url)
        # self.assertRedirects(response, self.events_url)
        self.assertEqual(EventPost.objects.count(), 0)  # noqa: F821

    def test_get(self):
        self.client.login(username="testuser@test.com", password="Test@123")
        response = self.client.get(self.url, data=self.valid_data)
        self.assertTemplateUsed(response, "doghub_app/add_event.html")

    def test_attendee(self):
        self.client.login(username="testuser@test.com", password="Test@123")
        response = self.client.post(self.url, data=self.valid_data)
        self.assertEqual(response.status_code, 302)
        event_post = EventPost.objects.first()
        self.assertNotEqual(
            Attendee.objects.filter(event_id=event_post.event_id, user_id=self.user),
            None,
        )

    # def test_add_post_view_with_invalid_location(self):
    #   self.client.login(username='testuser', password='Test@123')
    #  invalid_data = self.valid_data.copy()
    #  invalid_data['location'] = 'invalid_location'
    #  response = self.client.post(self.url, invalid_data)
    #  self.assertEqual(response.status_code, 302)
    #  self.assertRedirects(response, self.url)
    #  self.assertEqual(EventPost.objects.count(), 0)
    # messages = response.context.get('messages')
    # self.assertIsNotNone(messages)
    # self.assertIn('No park found for the given info', messages.rendered_content)


#  def test_add_post_view_with_invalid_location(self):
#     self.client.login(username='testuser', password='Test@123')
#    invalid_data = self.valid_data.copy()
#   invalid_data['location'] = 'invalid_location'
#  response = self.client.post(self.url, invalid_data)
# self.assertEqual(response.status_code, 302)
# self.assertRedirects(response, self.url)
# self.assertEqual(EventPost.objects.count(), 0)
# self.assertContains(response, 'No park found for the given info')

# def test_add_post_view_context(self):
#    self.client.login(username='testuser', password='Test@123')
#   response = self.client.get(self.url)
#   self.assertEqual(response.status_code, 302)
#   self.assertTrue('event_post_form' in response.context)
#   self.assertTrue('current_datetime' in response.context)
#   self.assertTrue('park_data' in response.context)
#   self.assertIsInstance(response.context['event_post_form'].instance, EventPost)
#   self.assertIsInstance(response.context['current_datetime'], str)
#   self.assertIsInstance(response.context['park_data'], str)
# self.assertContains(response, 'name="event_title"')
# self.assertContains(response, 'name="event_description"')
# self.assertContains(response, 'name="event_time"')
# self.assertContains(response, 'id="id_location"')


class TestFixtures(TestCase):
    """
    tests that all the data in the fixture files
    matches the data in the database
    """

    # the fixtures variable here is a Django variable used in setup
    # it tells Django to load this data into the database before testing
    fixtures = ["tag.yaml", "park.yaml"]

    # this is a local var, prefixed with dh (doghub) to not clash with Django
    # make sure your model is imported
    # extend this variable to test more fixtures files. format: (model, "filename.yaml")
    dh_fixtures = [
        (Tag, "tag.yaml"),
        (Park, "park.yaml"),
    ]

    dh_fixtures_path = pathlib.Path(BASE_DIR) / "doghub_app" / "fixtures"

    def test_if_fixtures_data_loaded(self):
        for model, fname in self.dh_fixtures:
            # logging.debug(f"testing fixture file {fname}")
            with open(self.dh_fixtures_path / fname) as file:
                data = yaml.safe_load(file)

            for rec in data:
                # logging.debug(f"testing pk: {rec['pk']}")
                try:
                    obj = model.objects.get(pk=rec["pk"])
                except model.DoesNotExist:
                    obj = None

                self.assertIsNotNone(obj)

                for field in rec["fields"]:
                    self.assertEqual(getattr(obj, field), rec["fields"][field])


class TestUserDateValidation(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username="testuser@example.com",
            email="testuser@example.com",
            password="Testpassword@123",
        )
        self.client.login(email="testuser@example.com", password="Testpassword@123")

    def test_user_age_valid(self):
        # test for valid user age
        today = date.today()
        user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Testing user",
            "uDOB": f"{today.year - 20}-01-01",
        }
        response = self.client.post(
            reverse("register_details"), data=user_profile_data, follow=True
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(UserProfile.objects.filter(user_id=self.user).exists())

    def test_user_age_invalid(self):
        # test for invalid user age (<18)
        today = date.today()
        user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Testing user",
            "uDOB": f"{today.year - 16}-01-01",
        }
        response = self.client.post(
            reverse("register_details"), data=user_profile_data, follow=True
        )
        self.assertContains(
            response,
            "For safety concerns, DogHub user should be 18+",
            status_code=200,
        )
        self.assertFalse(UserProfile.objects.filter(user_id=self.user).exists())

    def test_user_age_future_date(self):
        # test for invalid user date of birth (future date)
        today = date.today()
        user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Testing user",
            "uDOB": f"{today.year + 1}-01-01",
        }
        response = self.client.post(
            reverse("register_details"), data=user_profile_data, follow=True
        )
        self.assertContains(response, "Enter a valid Date of Birth", status_code=200)
        self.assertFalse(UserProfile.objects.filter(user_id=self.user).exists())


class TestUserProfileEdit(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="testuser", password="testpass"
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.client.login(username="testuser", password="testpass")
        self.url = reverse("user_profile_edit")

    def test_user_age_future_date(self):
        # test for invalid user date of birth (future date)
        today = date.today()
        user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Test bio",
            "uDOB": f"{today.year + 1}-01-01",
        }
        response = self.client.post(
            reverse("user_profile_edit"), data=user_profile_data, follow=True
        )
        self.assertContains(response, "Enter a valid Date of Birth", status_code=200)

    def test_user_age_invalid(self):
        # test for invalid user age (<18)
        today = date.today()
        user_profile_data = {
            "ufirstname": "Test",
            "ulastname": "User",
            "uBio": "Test bio",
            "uDOB": f"{today.year - 16}-01-01",
        }
        response = self.client.post(
            reverse("user_profile_edit"), data=user_profile_data, follow=True
        )
        self.assertContains(
            response,
            "For safety concerns, DogHub user should be 18+",
            status_code=200,
        )

    def test_valid_form_data(self):
        response = self.client.post(
            self.url,
            {
                "ufirstname": "New",
                "ulastname": "Name",
                "uDOB": date.today() - timedelta(days=365 * 25),
                "uBio": "New bio",
            },
        )
        self.assertRedirects(response, reverse("user_profile"))
        self.user_profile.refresh_from_db()
        self.assertEqual(self.user_profile.fname, "New")
        self.assertEqual(self.user_profile.lname, "Name")
        self.assertEqual(self.user_profile.bio, "New bio")

    def test_get_request(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test")
        self.assertContains(response, "User")
        self.assertContains(response, "Test bio")


class TestDogProfileSignals(TestCase):
    fixtures = ["tag.yaml"]

    def _test_tag(
        self, tag_id: int, name: str, tag_type: str, sys_tag: bool = True
    ) -> bool:
        try:
            tag = Tag.objects.get(tag_id=tag_id)
        except Tag.DoesNotExist:
            tag = None

            # check if tag exists
            self.assertIsNotNone(tag)
            # check if tag name matches (case insensitive)
            self.assertEqual(tag.tag_name.upper(), name.upper())
            # check if tag type is upper case
            self.assertEqual(tag.tag_type, tag.tag_type.upper())
            # check if tag type matches
            self.assertEqual(tag.tag_type, tag_type.upper())
            # check if sys_tag matches
            self.assertEqual(tag.sys_tag, sys_tag)

    def test_multiple_tags(self) -> None:
        # test tag_id, tag_name, tag_type, sys_tag
        self._test_tag(1, "dog owner", "U", True)
        self._test_tag(3, "puppy", "D", True)
        self._test_tag(13, "dog owner only", "E", True)

        return None


class SearchResultsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse("login")
        self.search_url = reverse("search-user")
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser@test.com",
            email="testuser@test.com",
            password="testpass123",
        )
        self.searched = {
            "searched": "test",
        }

    def test_login_success(self):
        self.user_data = {
            "uemail": "testuser@test.com",
            "psw": "testpass123",
        }
        response = self.client.post(self.login_url, data=self.user_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            CustomUser.objects.filter(email=self.user_data["uemail"]).exists()
        )

    def test_search_success(self):
        response = self.client.post(self.search_url, data=self.searched)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(CustomUser.objects.filter(email=self.user.email).exists())


class SearchUserTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@gmail.com", password="testpass123", email_verified=True
        )
        self.userprofile = UserProfile.objects.create(
            user_id=self.user,
            fname="John",
            lname="Doe",
            dob="2000-01-01",
            bio="Test user bio",
        )
        self.eventpost = EventPost.objects.create(
            user_id=self.user,
            event_title="Test Event",
            event_description="Test Description",
        )
        self.u_list = [
            {
                "fname": "John",
                "lname": "Doe",
                "email": "testuser@gmail.com",
            }
        ]

    def test_search_user_by_fname(self):
        logged_in = self.client.login(
            username="testuser@gmail.com", password="testpass123"
        )
        self.assertEqual(logged_in, True)
        response = self.client.post(
            reverse("search-user"),
            {
                "searched": "John",
                "show_users": True,
                "show_events": True,
                "u_list": self.u_list,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "John")
        u_list = response.context["u_list"]
        self.assertEqual(len(u_list), 1)
        self.assertContains(response, "events")

    def test_search_nothing(self):
        logged_in = self.client.login(
            username="testuser@gmail.com", password="testpass123"
        )
        self.assertEqual(logged_in, True)
        response = self.client.get(reverse("search-user"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doghub_app/search-results.html")


class PublicProfileTestCase(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            password="password123",
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2@example.com",
            email="user2@example.com",
            password="password456",
        )
        self.public_profile1 = UserProfile.objects.create(
            user_id=self.user1,
            fname="User",
            lname="One",
            dob="2000-01-01",
            bio="Test user bio",
        )
        self.public_profile2 = UserProfile.objects.create(
            user_id=self.user2,
            fname="User",
            lname="Two",
            dob="2000-01-01",
            bio="Test user bio",
        )

    def test_public_profile_existing_user(self):
        url = reverse("public-profile", args=["user1@example.com"])
        self.client.login(email="user2@example.com", password="password456")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doghub_app/public_user_profile.html")
        self.assertEqual(response.context["user"], self.user1)
        self.assertEqual(response.context["public_prof"], self.public_profile1)

    def test_public_profile_not_existing_user(self):
        url = reverse("public-profile", args=["user3@example.com"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)


class InboxTestCase(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user1,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2@example.com",
            email="user2@example.com",
            password="password123",
        )
        self.message = Chat.objects.create(
            receiver=self.user1,
            sender=self.user2,
            text="This is test Message",
        )

    def test_inbox_template(self):
        self.client.login(email="user1@example.com", password="password123")
        url = reverse("inbox")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doghub_app/inbox.html")
        self.assertEqual(response.context["user"], self.user1)

    def test_inbox_messages(self):
        self.client.login(email="user1@example.com", password="password123")
        url = reverse("inbox")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["messageList"]), 1)
        self.assertEqual(response.context["messageList"][0].sender, self.user2)
        self.assertEqual(response.context["messageList"][0].receiver, self.user1)
        self.assertEqual(Chat.objects.count(), 1)  # noqa: F821

    def test_retrieve_friends(self):
        Friends.objects.create(receiver=self.user1, sender=self.user2, pending=False)
        self.client.login(email="user1@example.com", password="password123")
        url = reverse("inbox")
        response = self.client.get(url)
        self.assertEqual(len(response.context["friendsLs"]), 1)
        self.assertEqual(response.context["friendsLs"][0], self.user2)


class ChatTestCases(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            password="password123",
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2@example.com",
            email="user2@example.com",
            password="password123",
        )
        self.message = Chat.objects.create(
            receiver=self.user1,
            sender=self.user2,
            text="This is test Message",
        )

    def createTest(self):
        self.assertEqual(Chat.objects.count(), 1)  # noqa: F821
        chat_message = Chat.objects.count().first()
        self.assertEqual(chat_message.sender, self.user2)
        self.assertEqual(chat_message.receiver, self.user1)
        self.assertEqual(chat_message.text, "This is test Message")


class TestRSVPfeature(TestCase):
    def setUp(self):
        self.user_attendee = CustomUser.objects.create_user(
            username="user1@attendee.com",
            email="user1@attendee1.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user_attendee,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.user_host = CustomUser.objects.create_user(
            username="user1@host.com",
            email="user1@host2.com",
            password="password123",
        )

    def testRedirectRegister(self):
        self.client.login(email="user1@host2.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "doghub_app/register.html")

    def testRsvp(self):
        self.event = EventPost.objects.create(
            user_id=self.user_host,
            event_title="Test Event",
            event_description="Test Description",
        )
        self.client.login(email="user1@attendee.com", password="password123")
        url = reverse("rsvp_event", args=[self.event.event_id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["events_list"]), 1)
        self.assertEqual(response.context["events_list"][0].user_id, self.user_host)

        self.assertNotEqual(
            Attendee.objects.filter(
                event_id=self.event.event_id, user_id=self.user_attendee
            ),
            None,
        )


class PrivateUserProfileTestCases(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1@example.com",
            email="user1@example.com",
            password="password123",
        )

        self.user_attendee = CustomUser.objects.create_user(
            username="user1@attendee.com",
            email="user1@attendee1.com",
            password="password123",
        )
        self.user_host = CustomUser.objects.create_user(
            username="user1@host.com",
            email="user1@host2.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user_host,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.event = EventPost.objects.create(
            user_id=self.user_host,
            event_title="Test Event",
            event_description="Test Description",
        )

    def testRedirectRegister(self):
        self.client.login(email="user1@example.com", password="password123")
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "doghub_app/register.html")

    def testEventRetrieve(self):
        self.client.login(email="user1@host2.com", password="password123")
        url = reverse("user_profile")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "doghub_app/user_profile.html")
        self.assertEqual(len(response.context["events_list"]), 1)
        self.assertEqual(response.context["events_list"][0].user_id, self.user_host)
        self.assertEqual(len(response.context["dogprof"]), 0)


class AddFriendTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="testuser", email="testuser@example.com", password="testpass"
        )
        self.friend = CustomUser.objects.create_user(
            username="testfriend", email="testfriend@example.com", password="testpass"
        )
        self.url = reverse("add_friend", args=[self.friend.email])
        self.client.login(username="testuser", password="testpass")
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test User",
        )

        self.friend_profile = UserProfile.objects.create(
            user_id=self.friend,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test User",
        )

    def test_add_friend(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Friends.objects.count(), 1)
        self.assertEqual(Friends.objects.first().sender, self.user)
        self.assertEqual(Friends.objects.first().receiver, self.friend)

    def test_add_self_as_friend(self):
        url = reverse("add_friend", args=[self.user.email])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Friends.objects.count(), 0)

    def test_add_existing_friend(self):
        Friends.objects.create(sender=self.user, receiver=self.friend, pending=False)
        url = reverse("add_friend", args=[self.user.email])
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Friends.objects.count(), 1)
        existing_friend = Friends.objects.first()
        self.assertEqual(existing_friend.sender, self.user)
        self.assertEqual(existing_friend.receiver, self.friend)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"You are already friends with {self.friend.email}."
        )

        url = reverse("delete_friend", args=[self.friend.email])
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


class TestCreateMessage(TestCase):
    def setUp(self):
        self.user_sender = CustomUser.objects.create_user(
            username="user1@attendee.com",
            email="user1@sender.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user_sender,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.user_receiver = CustomUser.objects.create_user(
            username="user1@host.com",
            email="user1@receiver.com",
            password="password123",
        )

    def testCreateMessage(self):
        self.client.login(email="user1@sender.com", password="password123")
        url = reverse("inbox")
        data = {"receiver": self.user_receiver.id, "message": "Test Message"}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Chat.objects.count(), 1)
        self.assertEqual(Chat.objects.first().sender, self.user_sender)
        self.assertEqual(Chat.objects.first().receiver, self.user_receiver)
        self.assertEqual(Chat.objects.first().text, "Test Message")


class TestEventPageFriendList(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="user1@test.com",
            email="user1@test.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2@test.com",
            email="user2@test.com",
            password="password123",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user2,
            fname="Test2",
            lname="User2",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        Friends.objects.create(receiver=self.user, sender=self.user2, pending=False)

    def testHtml(self):
        self.client.login(email="user1@test.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "doghub_app/events_homepage.html")

    def testRetrieveFriends(self):
        self.client.login(email="user1@test.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertEqual(len(response.context["user_profiles"]), 1)
        self.assertEqual(
            list(response.context["user_profiles"])[0]["email"], "user2@test.com"
        )
        self.assertEqual(list(response.context["user_profiles"])[0]["fname"], "Test2")

        url = reverse("support")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)

        url = reverse("about")
        response = self.client.get(url, follow=True)
        self.assertEqual(response.status_code, 200)


# class FriendsTestCase(TestCase):
#     def setUp(self):
#         self.client = Client()
#         self.user = CustomUser.objects.create_user(
#             username="testuser2@gmail.com",
#             email="testuser2@gmail.com",
#             password="password",
#         )
#         self.friend_user = CustomUser.objects.create_user(
#             username="frienduser2@gmail.com",
#             email="frienduser2@gmail.com",
#             password="password",
#         )


class FriendsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = CustomUser.objects.create_user(
            username="testuser2@gmail.com",
            email="testuser2@gmail.com",
            password="password",
        )
        self.friend_user = CustomUser.objects.create_user(
            username="frienduser2@gmail.com",
            email="frienduser2@gmail.com",
            password="password",
        )
        self.friend_user_profile = UserProfile.objects.create(
            user_id=self.friend_user,
            fname="Friend",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test Friend bio",
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="User",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test Friend bio",
        )

    def test_friend_requests(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("friend_requests"))
        self.assertEqual(response.status_code, 200)

        friend_request = Friends.objects.create(
            sender=self.friend_user, receiver=self.user, pending=True
        )
        response = self.client.get(reverse("friend_requests"))
        self.assertContains(response, self.friend_user.email)
        self.assertContains(response, self.user_profile.fname)
        self.assertContains(response, self.user_profile.lname)

        friend_request.delete()
        response = self.client.get(reverse("friend_requests"))
        self.assertContains(response, "You have no friend requests.")

    def test_accept_friend_request(self):
        friend_request = Friends.objects.create(
            sender=self.friend_user, receiver=self.user, pending=True
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("accept_friend_request", args=[friend_request.fid])
        )
        self.assertRedirects(response, reverse("friend_requests"))

        friend_request.refresh_from_db()
        self.assertFalse(friend_request.pending)
        self.assertTrue(
            Friends.objects.filter(
                sender=self.friend_user, receiver=self.user, pending=False
            ).exists()
        )

        response = self.client.get(reverse("friend_requests"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(
            str(messages[0]), f"You are now friends with {self.friend_user.email}."
        )

    def test_decline_friend_request(self):
        friend_request = Friends.objects.create(
            sender=self.friend_user, receiver=self.user, pending=True
        )
        self.client.force_login(self.user)
        response = self.client.get(
            reverse("decline_friend_request", args=[friend_request.fid])
        )
        self.assertRedirects(response, reverse("friend_requests"))

        self.assertFalse(Friends.objects.filter(fid=friend_request.fid).exists())

        response = self.client.get(reverse("friend_requests"))
        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), "Friend request declined.")


class GroupsTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="Hades", email="Hades@doghub.com", password="Test@123"
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test User",
        )
        self.user2 = CustomUser.objects.create_user(
            username="Hermes", email="Hermes@doghub.com", password="Test@123"
        )
        self.user2_profile = UserProfile.objects.create(
            user_id=self.user2,
            fname="Test",
            lname="User2",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test User2",
        )

        self.client.login(email="Hades@doghub.com", password="Test@123")

    def test_group_urls(self):
        urls = ["create_group", "join_group", "my_groups", "leave_group"]
        for u in urls:
            resp = self.client.get(reverse(u), follow=True)
            self.assertEqual(resp.status_code, 200)

    def test_create_group(self):
        new_group = {
            "group_title": "Hades Group",
            "group_description": "Hades Group Desc",
        }

        response = self.client.post(
            reverse("create_group"), data=new_group, follow=True
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Groups.objects.count(), 1)
        self.assertEqual(Groups.objects.first().group_owner, self.user)
        self.assertEqual(Groups.objects.first().group_title, new_group["group_title"])
        self.assertEqual(
            Groups.objects.first().group_description, new_group["group_description"]
        )

    def test_join_group(self):
        self.client.login(email="Hermes@doghub.com", password="Test@123")

        response = self.client.post(reverse("join_group"), data={}, follow=True)

        self.assertEqual(response.status_code, 200)


class GroupEventPage(TestCase):
    def setUp(self):
        self.user1 = CustomUser.objects.create_user(
            username="user1", email="user1@test.com", password="password123"
        )
        self.user2 = CustomUser.objects.create_user(
            username="user2", email="user2@test.com", password="password123"
        )
        self.user_profile1 = UserProfile.objects.create(
            user_id=self.user1,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )
        self.myGroup = Groups.objects.create(
            group_title="MyGroup",
            group_description="Test Group",
            group_owner=self.user1,
        )
        self.notMyGroup = Groups.objects.create(
            group_title="NotMyGroup",
            group_description="Test Group",
            group_owner=self.user2,
        )
        GroupMember.objects.create(
            group=self.notMyGroup, member=self.user1, pending=False
        )

    def testHtml(self):
        self.client.login(email="user1@test.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertTemplateUsed(response, "doghub_app/events_homepage.html")
        self.assertEqual(Groups.objects.count(), 2)
        self.assertEqual(len(list(Groups.objects.filter(group_owner=self.user1))), 1)
        self.assertEqual(len(list(Groups.objects.filter(group_owner=self.user2))), 1)

    def testMyGroup(self):
        self.client.login(email="user1@test.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertEqual(len(list(response.context["groups_owned"])), 1)
        self.assertEqual(
            list(response.context["groups_owned"])[0].group_title, "MyGroup"
        )
        self.assertEqual(
            list(response.context["groups_owned"])[0].group_owner, self.user1
        )

    def testJoinedGroup(self):
        self.client.login(email="user1@test.com", password="password123")
        url = reverse("events")
        response = self.client.get(url)
        self.assertEqual(len(response.context["groups_joined"]), 1)
        self.assertEqual(response.context["groups_joined"][0].group_title, "NotMyGroup")
        self.assertEqual(response.context["groups_joined"][0].group_owner, self.user2)


class EditPasswordViewTestCase(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser@gmail.com",
            password="testpassword123",
            email_verified=True,
        )
        self.client.login(username="testuser", password="testpassword")

    def test_get_edit_password_page(self):
        response = self.client.get(reverse("edit_password"))
        self.assertEqual(response.status_code, 302)

    def test_post_edit_password_valid_data(self):
        url = reverse("edit_password")
        data = {
            "current_password": "testpassword",
            "new_password": "Group@123",
            "confirm_password": "Group@123",
            "save_password": True,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()

    def test_post_edit_password_invalid_current_password(self):
        url = reverse("edit_password")
        data = {
            "current_password": "wrongpassword",
            "new_password": "newtestpassword",
            "confirm_password": "newtestpassword",
            "save_password": True,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_password_invalid_confirmation(self):
        url = reverse("edit_password")
        data = {
            "current_password": "testpassword",
            "new_password": "newtestpassword",
            "confirm_password": "mismatch",
            "save_password": True,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)

    def test_post_edit_password_invalid_new_password(self):
        url = reverse("edit_password")
        data = {
            "current_password": "testpassword",
            "new_password": "weak",
            "confirm_password": "weak",
            "save_password": True,
        }
        response = self.client.post(url, data=data)
        self.assertEqual(response.status_code, 302)


class AddServiceViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user_model = get_user_model()
        self.user = self.user_model.objects.create_user(
            username="testuser@test.com",
            email="testuser@test.com",
            password="Test@123",
            email_verified=True,
        )

    def test_add_service_view_with_valid_inputs(self):
        self.client.login(username="testuser@test.com", password="Test@123")
        response = self.client.post(
            "/add_service",
            {
                "title": "Test Service",
                "service_type": "Test Type",
                "service_description": "Test Description",
                "rate": "10",
                "contact": "test@test.com",
                "address": "Test Address",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/events")

    def test_add_service_view_with_invalid_inputs(self):
        url = reverse("add_service")
        self.client.login(username="testuser@test.com", password="Test@123")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "doghub_app/add_service.html")

    def test_add_service_view_for_logged_out_user(self):
        response = self.client.get("/add_service")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login?next=/add_service")

    def test_add_service_view_with_incomplete_fields(self):
        url = reverse("add_service")
        self.client.login(username="testuser", password="testpass")
        response = self.client.post(
            url,
            {
                "title": "Test Service",
                "service_type": "Test Type",
                "rate": "10",
                "contact": "test@test.com",
            },
        )
        self.assertEqual(response.status_code, 302)

    # self.assertTemplateUsed(response, 'doghub_app/add_service.html')


class CreateGroupViewTest(TestCase):
    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username="testuser", password="Test@123"
        )
        self.user_profile = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test User",
        )
        self.url = reverse("create_group")

    def test_create_group_with_valid_data(self):
        self.client.login(username="testuser", password="Test@123")
        form_data = {
            "group_title": "Test Group",
            "group_description": "This is a test group.",
        }
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(response, "/my-groups/")
        self.assertTrue(Groups.objects.filter(group_title="Test Group").exists())
        self.assertEqual(
            Groups.objects.filter(group_title="Test Group").first().group_owner,
            self.user,
        )

    def test_create_group_with_invalid_data(self):
        self.client.login(username="testuser", password="Test@123")
        form_data = {}
        response = self.client.post(self.url, form_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        self.assertFalse(Groups.objects.filter(group_title="Test Group").exists())


class JoinLeaveGroupTestCase(TestCase):
    def setUp(self):
        # Create a user
        self.user = CustomUser.objects.create_user(
            username="user1", email="user1@example.com", password="testpassword"
        )
        self.user_profile1 = UserProfile.objects.create(
            user_id=self.user,
            fname="Test",
            lname="User",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )

        # Create some groups
        self.group1 = Groups.objects.create(
            group_title="Group 1",
            group_description="Group 1 description",
            group_owner=self.user,
        )
        self.group2 = Groups.objects.create(
            group_title="Group 2",
            group_description="Group 2 description",
            group_owner=self.user,
        )
        self.group3 = Groups.objects.create(
            group_title="Group 3",
            group_description="Group 3 description",
            group_owner=self.user,
        )
        self.group1.save()
        self.group2.save()
        self.group3.save()

        # user1 owns 3 groups
        # Create another user to join user1 groups
        self.user2 = CustomUser.objects.create_user(
            username="user2", email="user2@example.com", password="testpassword"
        )
        self.user_profile2 = UserProfile.objects.create(
            user_id=self.user2,
            fname="Test",
            lname="User 2",
            dob=date.today() - timedelta(days=365 * 20),
            bio="Test bio",
        )

    def test_join_leave_group_view(self):
        # Login user2
        self.client.login(username="user2", password="testpassword")

        # Access the join_group view
        response = self.client.get(reverse("join_group"))

        # Check that the response is successful and the context is correct
        self.assertEqual(response.status_code, 200)
        self.assertTrue("groups" in response.context)
        self.assertEqual(len(response.context["groups"]), 3)

        # logging.debug("so far so good")
        # Check that the user is not a member of any of the groups
        for group in response.context["groups"]:
            # logging.debug(f"checking member for group {group}")
            self.assertFalse(group.groupmember_set.filter(member=self.user2).exists())

        # Join Group 1 and Group 2
        group_ids = [g.group_id for g in response.context["groups"]]
        gid1, gid2, gid3 = group_ids
        response = self.client.post(
            reverse("join_group"), data={str(gid1): "on", str(gid2): "on"}
        )

        # Check that the user is now a pending member of Group 1 and Group 2 but not group3
        self.assertTrue(
            self.group1.groupmember_set.filter(member=self.user2, pending=True).exists()
        )
        self.assertTrue(
            self.group2.groupmember_set.filter(member=self.user2, pending=True).exists()
        )
        self.assertFalse(
            self.group3.groupmember_set.filter(member=self.user2, pending=True).exists()
        )

        # check that the owner is not a member
        self.assertFalse(self.group1.groupmember_set.filter(member=self.user).exists())
        self.assertFalse(self.group2.groupmember_set.filter(member=self.user).exists())
        self.assertFalse(self.group3.groupmember_set.filter(member=self.user).exists())

        # login the owner and accept incoming requests
        self.client.login(username="user", password="testpassword")

        response = self.client.get(reverse("my_groups"))

        # check that there are 2 pending requests
        self.assertEqual(len(response.context["groups_pending"]), 2)

        # accept one and reject the other
        gid1, gid2 = [g.group_id for g in response.context["groups_pending"]]

        # accept member into group1
        response = self.client.post(
            reverse("my_groups"),
            data={"group_id": gid1, "member_id": self.user2.pk, "status": "accept"},
        )

        # reject member from group2
        response = self.client.post(
            reverse("my_groups"),
            data={"group_id": gid2, "member_id": self.user2.pk, "status": "reject"},
        )

        # login user2 and check that he's no longer pending for group1
        # and was rejected for group2
        self.client.login(username="user2", password="testpassword")
        # Check that the user is now a pending member of Group 1 and Group 2 but not group3

        self.assertTrue(
            self.group1.groupmember_set.filter(
                member=self.user2, pending=False
            ).exists()
        )
        self.assertFalse(self.group2.groupmember_set.filter(member=self.user2).exists())

        # test leave group
        # user2 is currently logged in
        # and is a member of group1 only, test that they can leave group1

        # get a list of groups to leave
        response = self.client.get(reverse("leave_group"))

        # check that the user is part of only one group
        # and that it's group one
        self.assertEqual(len(response.context["groups"]), 1)
        self.assertEqual(response.context["groups"][0].group_id, gid1)

        # logging.debug(f"the response: {response}")
        # logging.debug(f"the context: {response.context}")
        # logging.debug(f"gid1: {gid1} gid2: {gid2}")

        # leave group1
        response = self.client.post(reverse("leave_group"), data={str(gid1): "on"})

        # check that user2 is no longer a member of group1
        self.assertFalse(self.group1.groupmember_set.filter(member=self.user2).exists())
