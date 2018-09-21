from datetime import datetime, timedelta

from django.test import TestCase
from django.shortcuts import reverse

from .models import User, Company
from .utils.person_info import average_duration_activity
from associate.models import Device, Activity


class ManagerViewAccessTestCase(TestCase):
    def setUp(self):
        self.valid_credentials = {
            'username': 'testuser1',
            'password': '1234qwer'
        }
        self.valid_credentials_company = {
            'username': 'testuser2',
            'password': '1234qwer'
        }
        self.invalid_credentials = {
            'username': 'testuser3',
            'password': '1234qwer'
        }
        self.company = Company.objects.create(title='some company')
        self.valid_user = User.objects.create_user(**self.valid_credentials, is_staff=True)
        self.valid_user_with_company = User.objects.create_user(
            **self.valid_credentials_company,
            is_staff=True
        )
        self.valid_user_with_company.profile.company = self.company
        self.valid_user_with_company.profile.save()
        self.invalid_user = User.objects.create_user(**self.invalid_credentials)
        self.invalid_user.profile.company = self.company
        self.invalid_user.profile.save()

    def test_invite_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse('invite'))
        self.assertRedirects(response, reverse('create_company'), 302)

    def test_invite_view_with_company_positive(self):
        self.client.login(**self.valid_credentials_company)
        response = self.client.get(reverse('invite'))
        self.assertEqual(response.status_code, 200)

    def test_invite_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse('invite'))
        self.assertEqual(response.status_code, 404)

    def test_register_company_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse('create_company'))
        self.assertEqual(response.status_code, 200)

    def test_register_with_company_view_positive(self):
        self.client.login(**self.valid_credentials_company)
        response = self.client.get(reverse('create_company'))
        self.assertRedirects(
            response,
            reverse('company_info', kwargs={
                'pk': self.valid_user_with_company.profile.company.id
            }),
            302
        )

    def test_register_company_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse('create_company'))
        self.assertEqual(response.status_code, 404)

    def test_person_activity_view_with_company_positive(self):
        self.client.login(**self.valid_credentials_company)
        response = self.client.get(reverse('person_activity', kwargs={'pk': self.invalid_user.id}))
        self.assertEqual(response.status_code, 200)

    def test_person_activity_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse('person_activity', kwargs={'pk': self.invalid_user.id}))
        self.assertEqual(response.status_code, 404)

    def test_person_activity_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse('person_activity', kwargs={'pk': self.invalid_user.id}))
        self.assertEqual(response.status_code, 404)

    def test_info_company_view_positive(self):
        self.client.login(**self.valid_credentials)
        response = self.client.get(reverse(
            'company_info',
            kwargs={
                'pk': self.valid_user_with_company.profile.company.id
            }
        ))
        self.assertEqual(response.status_code, 404)

    def test_info_with_company_view_positive(self):
        self.client.login(**self.valid_credentials_company)
        response = self.client.get(reverse(
            'company_info',
            kwargs={
                'pk': self.valid_user_with_company.profile.company.id
            }
        ))
        self.assertEqual(response.status_code, 200)

    def test_info_company_view_negative(self):
        self.client.login(**self.invalid_credentials)
        response = self.client.get(reverse(
            'company_info',
            kwargs={
                'pk': self.valid_user_with_company.profile.company.id
            }
        ))
        self.assertEqual(response.status_code, 404)


class UtilsTestCase(TestCase):
    def setUp(self):
        self.valid_credentials = {
            'username': 'testuser1',
            'password': '1234qwer'
        }
        self.user = User.objects.create_user(**self.valid_credentials)
        device = Device.objects.create(name='some device', user=self.user)
        activities_data = [
            {
                'device': device,
                'start': '2018-06-21T10:00:00Z',
                'end': '2018-06-21T11:00:00Z',
                'name': 'Some activity 1',
                'user': self.user
            },
            {
                'device': device,
                'start': '2018-06-21T12:00:00Z',
                'end': '2018-06-21T14:00:00Z',
                'name': 'Some activity 2',
                'user': self.user
            },
            {
                'device': device,
                'start': '2018-06-21T06:30:00Z',
                'end': '2018-06-21T07:48:00Z',
                'name': 'Some activity 3',
                'user': self.user
            },
        ]
        activities = [
            Activity(**active)
            for active in activities_data
        ]
        Activity.objects.bulk_create(activities)

    def test_average_duration_activity(self):
        t = datetime.strptime('1:26:00', '%H:%M:%S').time()
        self.assertEqual(average_duration_activity(self.user), timedelta(hours=t.hour, minutes=t.minute, seconds=t.second))
        self.assertIsInstance(average_duration_activity(self.user), timedelta)
