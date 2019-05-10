from django.test import TestCase
from ..forms import UserRegistrationForm


class SignUpFormTest(TestCase):
    def test_form_has_fields(self):
        form = UserRegistrationForm()
        expected = ['username', 'email', 'password1', 'password2', ]
        actual = list(form.fields)
        self.assertSequenceEqual(expected, actual)
