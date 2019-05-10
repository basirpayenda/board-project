from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.auth import views as auth_views
from django.urls import resolve, reverse
from django.test import TestCase


class PasswordChangeTests(TestCase):
    def setUp(self):
        username = 'john'
        password = 'secret123'
        # Create user
        user = User.objects.create_user(
            username=username, email='john@doe.com', password=password)
        # Login user
        # Now logged in users can change the password
        self.client.login(username=username, password=password)
        self.response = self.client.get(reverse('password_change'))

    def test_status_code(self):
        self.assertEqual(self.response.status_code, 200)

    def test_url_resolves_correct_view(self):
        view = resolve('/settings/change-password/')
        self.assertEqual(view.func.view_class, auth_views.PasswordChangeView)

    def test_csrf(self):
        self.assertContains(self.response, 'csrfmiddlewaretoken')

    def test_contains_form(self):
        form = self.response.context.get('form')
        self.assertIsInstance(form, PasswordChangeForm)

    def test_form_inputs(self):
        '''
        The view must contain four inputs: csrf, old_password, new_password1, new_password2
        '''
        self.assertContains(self.response, '<input', 5)
        self.assertContains(self.response, 'type="password"', 3)
        self.assertContains(self.response, 'type="submit"', 1)


class LoginRequiredPasswordChangeTests(TestCase):
    def test_redirection(self):
        url = reverse('password_change')
        login_url = reverse('signin')
        response = self.client.get(url)
        self.assertRedirects(response, f'{login_url}?next={url}')


class PasswordChangeTestCase(TestCase):
    '''
    Base test case for form processing
    accepts a `data` dict to POST to the view.
    '''

    def setUp(self, data={}):
        # Sign up then sign in
        self.user = User.objects.create_user(
            username='john', email='john@doe.com', password='old_password')
        self.client.login(username='john', password='old_password')

        # Browsing Password Change Page and Posting data in it!
        self.url = reverse('password_change')
        self.response = self.client.post(self.url, data)


class SuccessfulPasswordChangeTests(PasswordChangeTestCase):
    def setUp(self):
        super().setUp({
            'old_password': 'old_password',
            'new_password1': 'new_password',
            'new_password2': 'new_password',
        })

    def test_redirection(self):
        '''
        A valid form submission should redirect the user
        '''
        self.assertRedirects(self.response, reverse('password_change_done'))

    def test_password_changed(self):
        '''
        refresh the user instance from database to get the new password
        hash updated by the change password view.
        '''
        self.user.refresh_from_db()
        # Make
        self.assertTrue(self.user.check_password('new_password'))

    def test_user_authentication(self):
        '''
        Create a new request to an arbitrary page.
        The resulting response should now have an `user` to its context, after a successful sign up.
        '''
        response = self.client.get(reverse('board:home'))
        user = response.context.get('user')
        self.assertTrue(user.is_authenticated)


class InvalidPasswordChangeTests(PasswordChangeTestCase):
    def test_status_code(self):
        '''
        An invalid form submission should return to the same page
        '''
        self.assertEqual(self.response.status_code, 200)

    def test_form_errors(self):
        form = self.response.context.get('form')
        self.assertTrue(form.errors)

    def test_didnt_change_password(self):
        '''
        refresh the user instance from the database to make
        sure we have the latest data.
        '''
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('old_password'))
