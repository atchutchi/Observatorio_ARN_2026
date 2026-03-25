from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()


class AuthAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123',
            email='test@arn.gw', role='admin_arn',
            first_name='Test', last_name='User',
        )

    def test_obtain_token(self):
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_obtain_token_wrong_password(self):
        response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser', 'password': 'wrongpass',
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token(self):
        token_response = self.client.post('/api/v1/auth/token/', {
            'username': 'testuser', 'password': 'testpass123',
        })
        refresh = token_response.data['refresh']

        response = self.client.post('/api/v1/auth/token/refresh/', {
            'refresh': refresh,
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)


class ProfileAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='profileuser', password='testpass123',
            email='profile@arn.gw', role='analyst_arn',
            first_name='Profile', last_name='User',
            phone='+245955111111', position='Analista',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'profileuser')
        self.assertEqual(response.data['email'], 'profile@arn.gw')
        self.assertEqual(response.data['role'], 'analyst_arn')

    def test_update_profile(self):
        response = self.client.patch('/api/v1/auth/profile/', {
            'first_name': 'Updated',
            'phone': '+245955222222',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], 'Updated')
        self.assertEqual(response.data['phone'], '+245955222222')

    def test_cannot_change_role_via_profile(self):
        response = self.client.patch('/api/v1/auth/profile/', {
            'role': 'admin_arn',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, 'analyst_arn')

    def test_unauthenticated_profile(self):
        self.client.force_authenticate(user=None)
        response = self.client.get('/api/v1/auth/profile/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class UserManagementAPITest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_user(
            username='admin', password='testpass123', role='admin_arn',
        )
        self.analyst = User.objects.create_user(
            username='analyst', password='testpass123', role='analyst_arn',
        )
        self.client.force_authenticate(user=self.admin)

    def test_list_users_as_admin(self):
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_users_as_non_admin(self):
        self.client.force_authenticate(user=self.analyst)
        response = self.client.get('/api/v1/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_user(self):
        response = self.client.post('/api/v1/users/', {
            'username': 'newuser',
            'password': 'securepass123',
            'role': 'viewer',
            'email': 'new@arn.gw',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_update_user(self):
        response = self.client.patch(f'/api/v1/users/{self.analyst.id}/', {
            'first_name': 'Updated',
        })
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.analyst.refresh_from_db()
        self.assertEqual(self.analyst.first_name, 'Updated')

    def test_delete_user(self):
        response = self.client.delete(f'/api/v1/users/{self.analyst.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(User.objects.filter(id=self.analyst.id).exists())
