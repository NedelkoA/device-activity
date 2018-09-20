from uuid import uuid4

from django.test import TestCase
from django.shortcuts import reverse
from django.contrib.auth.models import User

from .utils.tokens import UserToken
from company_manager.models import Invite


class RegisterTestCase(TestCase):
    def setUp(self):
        self.valid_user = {
            'username': 'testuser1',
            'password1': '12345678910add',
            'password2': '12345678910add',
            'email': 'some@some.com',
        }

        self.invalid_user = {
            'username': 'testuser2',
            'password1': 'qwer1234',
            'password2': 'qwer1234',
            'email': 'somemail.com',
        }
        invite_token = uuid4()
        token = str(invite_token).replace('-', '')
        self.invite = Invite.objects.create(
            email='dasdasd@mail.ru',
            invite_token=token
        )

    def test_register_page(self):
        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code, 200)

    def test_register_positive(self):
        response = self.client.post(reverse('registration'), self.valid_user, follow=True)
        self.assertTrue(response.context['user'].is_staff)
        self.assertTrue(response.context['user'].profile)
        self.assertRedirects(response, reverse('profile'), 302)

    def test_register_negative(self):
        response = self.client.post(reverse('registration'), self.invalid_user, follow=True)
        self.assertFalse(response.context['user'].is_active)

    def test_register_with_token(self):
        response = self.client.post(
            '{}?token={}'.format(
                reverse('registration'),
                self.invite.invite_token
            ),
            self.valid_user,
            follow=True
        )
        self.assertTrue(response.context['user'].is_active)
        self.assertFalse(response.context['user'].is_staff)
        self.assertTrue(response.context['user'].profile)
        self.assertTrue(response.context['user'].auth_token)
        self.assertRedirects(response, reverse('profile'), 302)


class LoginTestCase(TestCase):
    def setUp(self):
        self.valid_user = {
            'username': 'testuser1',
            'password': '1234qwer'}
        self.invalid_user = {
            'username': 'testuser2',
            'password': '1234'}

        User.objects.create_user(**self.valid_user)

    def test_login_positive(self):
        response = self.client.post(reverse('login'), self.valid_user, follow=True)
        self.assertTrue(response.context['user'].is_active)
        self.assertRedirects(response, reverse('profile'), 302)

    def test_login_negative(self):
        response = self.client.post(reverse('login'), self.invalid_user, follow=True)
        self.assertTrue(response.context['user'].is_anonymous)

    def test_logout(self):
        response = self.client.get(reverse('logout'), follow=True)
        self.assertTrue(response.context['user'].is_anonymous)
        self.assertRedirects(response, reverse('login'), 302)


class TokenTestCase(TestCase):
    def setUp(self):
        invite_token = uuid4()
        token = str(invite_token).replace('-', '')
        self.invite = Invite.objects.create(
            email='dasdasd@mail.ru',
            invite_token=token
        )
        valid_user = {
            'username': 'testuser1',
            'password': '1234qwer'}
        User.objects.create_user(**valid_user)

    def test_token_exist(self):
        response = self.client.get(
            reverse('registration'),
            data={'token': self.invite.invite_token}
        )
        self.assertTrue(UserToken.check_instance(response.context['request']))

    def test_token_is_alive(self):
        response = self.client.get(
            reverse('registration'),
            data={'token': self.invite.invite_token}
        )
        user_token = UserToken.check_instance(response.context['request'])
        self.assertTrue(user_token.is_alive())

    def test_token_is_used(self):
        response = self.client.get(
            reverse('registration'),
            data={'token': self.invite.invite_token}
        )
        user_token = UserToken.check_instance(response.context['request'])
        user_token.token.invited = User.objects.get(username='testuser1')
        user_token.token.save()
        self.assertTrue(user_token.is_used())
