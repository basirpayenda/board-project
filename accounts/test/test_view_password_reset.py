from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.models import User
from django.core import mail
from django.urls import resolve, reverse
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator


# TODO: class for password reset test
# TODO: check the status of password_reset url
# TODO: check the function of the url
# TODO: check if it is the proper form submitted at password_reset.html
# TODO: check the number of inputs there

class PasswordResetTest(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.get(url)

    def test_password_reset_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_password_reset_view_function(self):
        url = resolve('/password_reset/')
        self.assertEqual(url.func.view_class, auth_views.PasswordResetView)

    def test_check_form_at_password_reset(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordResetForm)

    def test_check_input_numbers(self):
        self.assertContains(self.response, '<input', 3)
        self.assertContains(self.response, 'type="email"', 1)


# TODO: Class for successful password reset
# TODO: check the redirection
# TODO: check if the email is sent

class SuccessfulPasswordResetTest(TestCase):
    def setUp(self):
        email = 'basirrpayenda@gmail.com'
        User.objects.create_user(
            username='JohnDoe', email=email, password='tester123')

        url = reverse('password_reset')
        self.response = self.client.post(url, {'email': email})

    def test_redirection(self):
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_sent_email(self):
        self.assertEqual(1, len(mail.outbox))

# TODO: - class for invalid email at password reset page
# TODO: test redirection back to password_reset_done
# TODO: test if the email is sent


class UnsuccessfulPasswordResetTest(TestCase):
    def setUp(self):
        url = reverse('password_reset')
        self.response = self.client.post(
            url, {'email': 'doesntexistemail@email.com'})

    def test_redirection(self):
        url = reverse('password_reset_done')
        self.assertRedirects(self.response, url)

    def test_email_numbers_sent(self):
        self.assertEqual(0, len(mail.outbox))


class PasswordResetDoneTest(TestCase):
    def setUp(self):
        url = reverse('password_reset_done')
        self.response = self.client.get(url)

    def test_password_reset_done_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve('/password_reset/done/')
        self.assertEqual(view.func.view_class,
                         auth_views.PasswordResetDoneView)


class PasswordResetConfirmTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='john', email='john@doe.com', password='123abcdef')

        self.uid = urlsafe_base64_encode(force_bytes(user.pk))
        self.token = default_token_generator.make_token(user)

        self.response = self.client.get(reverse('password_reset_confirm', kwargs={
                                        'uidb64': self.uid, 'token': self.token}), follow=True)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_view_function(self):
        view = resolve("/password_reset_confirm/<uidb64>/<token>/")
        self.assertEqual(view.func.view_class,
                         auth_views.PasswordResetConfirmView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_forms(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, SetPasswordForm)

    def test_forms_inputs(self):
        self.assertContains(self.response, '<input', 4)
        self.assertContains(self.response, 'type="password"', 2)
        self.assertContains(self.response, 'type="submit"', 1)


class InvalidPasswordResetConfirmTest(TestCase):
    def setUp(self):
        user = User.objects.create_user(
            username='john', email='john@doe.com', password='testing123')

        uid = urlsafe_base64_encode(force_bytes(user))
        token = default_token_generator.make_token(user)

        user.set_password = 'john'
        user.save()

        self.response = self.client.get(
            reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token}))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_html(self):
        password_reset_url = reverse('password_reset')
        self.assertContains(
            self.response, 'href="{0}"'.format(password_reset_url))


class PasswordResetCompleteTest(TestCase):
    def setUp(self):
        url = reverse('password_reset_complete')
        self.response = self.client.get(url)

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolve(self):
        url = resolve('/password_reset_complete/')
        self.assertEqual(url.func.view_class,
                         auth_views.PasswordResetCompleteView)
