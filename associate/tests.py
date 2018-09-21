from django.test import TestCase
from django.contrib.auth.models import User
from django.shortcuts import reverse
from rest_framework.test import APITestCase
from rest_framework import status

from .models import Device, Activity


class ApiTestCase(APITestCase):
    def setUp(self):
        self.device = {
            'name': 'Some device'
        }
        valid_user = {
            'username': 'testuser1',
            'password': '1234qwer'
        }
        self.user = User.objects.create_user(**valid_user)
        device = Device.objects.create(name='Some name', user=self.user)
        self.activity = {
            'device': device.id,
            'start': '2018-06-06 10:00:00',
            'end': '2018-06-06 11:00:00',
            'name': 'Some activity'
        }

    def test_post_device(self):
        self.assertEqual(Device.objects.count(), 1)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.post('/api/device/', format='json', data=self.device)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 2)

    def test_post_activities(self):
        self.assertEqual(Activity.objects.count(), 0)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.post('/api/activities/', format='json', data=self.activity)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Activity.objects.count(), 1)


class ApiAccessTestCase(APITestCase):
    def setUp(self):
        valid_user = {
            'username': 'testuser1',
            'password': '1234qwer'
        }
        self.user = User.objects.create_user(**valid_user)

    def test_get_device_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.get('/api/device/')
        self.assertEqual(response.status_code, 405)

    def test_get_activities_auth(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + str(self.user.auth_token))
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, 405)

    def test_get_device(self):
        response = self.client.get('/api/device/')
        self.assertEqual(response.status_code, 401)

    def test_get_activities(self):
        response = self.client.get('/api/activities/')
        self.assertEqual(response.status_code, 401)


class ViewAccessTestCase(TestCase):
    def setUp(self):
        self.valid_credentials = {
            'username': 'testuser1',
            'password': '1234qwer'
        }
        self.invalid_credentials = {
            'username': 'testuser2',
            'password': '1234qwer'
        }
        self.valid_user = User.objects.create_user(**self.valid_credentials)
        self.invalid_user = User.objects.create_user(**self.invalid_credentials, is_staff=True)
        self.device = Device.objects.create(name='some device', user=self.valid_user)

    def test_device_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse('devices'))
        self.assertEqual(response.status_code, 200)

    def test_device_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse('devices'))
        self.assertEqual(response.status_code, 404)

    def test_activities_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse('activity_device', kwargs={'pk': self.device.id}))
        self.assertEqual(response.status_code, 200)

    def test_activities_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse('activity_device', kwargs={'pk': self.device.id}))
        self.assertEqual(response.status_code, 404)
