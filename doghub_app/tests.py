from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from datetime import datetime
from django.contrib.auth import get_user_model
from mock import patch
from doghub_app.models import CustomUser, UserProfile, DogProfile, EventPost, Park
from doghub_app.tokens import verification_token_generator
from .forms import EventPostForm
from . import validators
from django.core import mail
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.messages import get_messages


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

class AddPostViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", email="test@example.com", password="testpass")
        self.park = Park.objects.create(name='Test Fishbridge', latitude='40.709070274158', longitude='-74.0013770043858')
        self.url = reverse('add_post')
        self.url = reverse ('add_post')
        self.valid_data = {
            'event_title': 'Test Event',
            'event_description': 'This is a test event',
            'event_time': '2023-04-08T12:00',
            'location': '40.709070274158', longitude='-74.0013770043858'
        }

    def test_add_post_view_with_valid_data(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(EventPost.objects.count(),1)

    def test_add_post_view_with_invalid_data(self):
        self.client.login(username='testuser', password='testpass')
        invalid_data = self.valid_data.copy()
        invalid_data['event_title'] = ''
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')

    def test_add_post_view_with_unauthenticated_user(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/accounts/login/?next=' + self.url)

    def test_add_post_view_with_unverified_user(self):
        self.user.email_verified = False
        self.user.save()
        self.client.login(username='testuser', password='testpass')
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/events/')
        self.assertEqual(EventPost.objects.count(), 0)

    def test_add_post_view_with_invalid_location(self):
        self.client.login(username='testuser', password='testpass')
        invalid_data = self.valid_data.copy()
        invalid_data['location'] = 'invalid_location'
        response = self.client.post(self.url, invalid_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.assertEqual(EventPost.objects.count(), 0)
        self.assertContains(response, 'No park found for the given info')

    def test_add_post_view_context(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('event_post_form' in response.context)
        self.assertTrue('current_datetime' in response.context)
        self.assertTrue('park_data' in response.context)
        self.assertIsInstance(response.context['event_post_form'].instance, EventPost)
        self.assertIsInstance(response.context['current_datetime'], str)
        self.assertIsInstance(response.context['park_data'], str)
        self.assertContains(response, 'name="event_title"')
        self.assertContains(response, 'name="event_description"')
        self.assertContains(response, 'name="event_time"')
        self.assertContains(response, 'id="id_location"')