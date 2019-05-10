from django.contrib.auth.models import User
from django.test import TestCase
from django.core import mail
from django.urls import reverse, resolve
from django.contrib.auth import views as auth_view


# TODO: test email subject
# TODO: test email body
# TODO: test email to


class TestMailPasswordReset(TestCase):
    def setUp(self):
        User.objects.create_user(
            username='john', email='john@doe.com', password='123')
        self.response = self.client.post(reverse('password_reset'), {
                                         'email': 'john@doe.com'})
        self.email = mail.outbox[0]

    def test_email_subject(self):
        self.assertEqual(
            '[Django boards] Please reset your password', self.email.subject)

    def test_email_body(self):
        context = self.response.context
        uid = context.get('uid')
        token = context.get('token')
        password_reset_confirm_token = reverse('password_reset_confirm', kwargs={
            'uidb64': uid, 'token': token})

        self.assertIn(password_reset_confirm_token, self.email.body)
        self.assertIn('john@doe.com', self.email.body)
        self.assertIn('john', self.email.body)

    def test_email_to(self):
        self.assertEqual(['john@doe.com', ], self.email.to)
