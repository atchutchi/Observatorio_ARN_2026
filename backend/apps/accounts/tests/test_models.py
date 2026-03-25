from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):

    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin_test', password='testpass123', role='admin_arn',
        )
        self.analyst = User.objects.create_user(
            username='analyst_test', password='testpass123', role='analyst_arn',
        )
        self.operator = User.objects.create_user(
            username='op_test', password='testpass123', role='operator_telecel',
        )
        self.viewer = User.objects.create_user(
            username='viewer_test', password='testpass123', role='viewer',
        )

    def test_is_arn_admin(self):
        self.assertTrue(self.admin.is_arn_admin)
        self.assertFalse(self.analyst.is_arn_admin)
        self.assertFalse(self.operator.is_arn_admin)
        self.assertFalse(self.viewer.is_arn_admin)

    def test_is_arn_staff(self):
        self.assertTrue(self.admin.is_arn_staff)
        self.assertTrue(self.analyst.is_arn_staff)
        self.assertFalse(self.operator.is_arn_staff)
        self.assertFalse(self.viewer.is_arn_staff)

    def test_is_operator_user(self):
        self.assertFalse(self.admin.is_operator_user)
        self.assertTrue(self.operator.is_operator_user)
        self.assertFalse(self.viewer.is_operator_user)

    def test_str_representation(self):
        self.admin.first_name = 'Admin'
        self.admin.last_name = 'Test'
        self.admin.save()
        self.assertIn('Admin Test', str(self.admin))
        self.assertIn('Administrador ARN', str(self.admin))

    def test_default_role_is_viewer(self):
        user = User.objects.create_user(username='default_role', password='testpass123')
        self.assertEqual(user.role, 'viewer')

    def test_user_fields(self):
        self.admin.phone = '+245955000000'
        self.admin.position = 'Director'
        self.admin.save()
        self.admin.refresh_from_db()
        self.assertEqual(self.admin.phone, '+245955000000')
        self.assertEqual(self.admin.position, 'Director')
