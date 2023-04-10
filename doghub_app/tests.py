from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from unittest.mock import patch
from doghub_app.models import CustomUser, UserProfile, DogProfile, Tag, Park
from doghub_app.tokens import verification_token_generator
from . import validators
from django.core import mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import get_messages
from doghub.settings import BASE_DIR
import pathlib
import yaml
from datetime import date, timedelta

# import logging


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
            "http://127.0.0.1:8000/reset_password/confirm", mail.outbox[0].body
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
