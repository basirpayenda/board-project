from django.test import TestCase
from django.urls import reverse, resolve
from ..views import signup_view
from django.contrib.auth.models import User
from ..forms import UserRegistrationForm


class SignupTest(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.get(url)

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_signup_url_resolve(self):
        view = resolve('/signup/')
        self.assertEqual(view.func, signup_view)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, UserRegistrationForm)

    def test_form_inputs(self):
        self.assertContains(self.response, '<input', 6)
        self.assertContains(self.response, 'type="text"', 2)
        self.assertContains(self.response, 'type="submit"', 1)
        self.assertContains(self.response, 'type="password"', 2)


class SuccessfulSignupTest(TestCase):
    def setUp(self):
        signup_url = reverse('signup')
        data = {
            'username': 'dr.johndoe',
            'email': 'johndoe@gmail.com',
            'password1': 'password123.com',
            'password2': 'password123.com'
        }

        self.response = self.client.post(signup_url, data)
        self.home = reverse('board:home')

    def test_signup_redirection(self):
        self.assertRedirects(self.response, self.home)

    def test_user_registration_form(self):
        self.assertTrue(User.objects.exists())

    def test_user_authentication(self):
        homepage = self.client.get(self.home)
        user = homepage.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidSignUpTests(TestCase):
    def setUp(self):
        url = reverse('signup')
        self.response = self.client.post(url, {})

    def test_signup_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    # def test_form_errors(self):
    #     form = self.response.context.get('form')
    #     self.assertTrue(form.errors)
    # TODO: solve it!

    def test_dont_create_user(self):
        self.assertFalse(User.objects.exists())
