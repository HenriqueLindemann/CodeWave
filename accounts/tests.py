from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Skill

User = get_user_model()

class UserModelTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.skill1 = Skill.objects.create(name='Python', description='Python programming language')
        self.skill2 = Skill.objects.create(name='Django', description='Django web framework')

        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
            name='Test User',
            is_developer=True,
            is_client=False,
            bio='This is a test bio.',
            balance=100.00,
            rank=5,
            rating=8.5,
            wave_balance=50.00
        )
        self.user.skills.add(self.skill1, self.skill2)

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'testuser@example.com')
        self.assertTrue(self.user.is_developer)
        self.assertFalse(self.user.is_client)
        self.assertEqual(self.user.bio, 'This is a test bio.')
        self.assertEqual(self.user.balance, 100.00)
        self.assertEqual(self.user.rank, 5)
        self.assertEqual(self.user.rating, 8.5)
        self.assertEqual(self.user.wave_balance, 50.00)
        self.assertIn(self.skill1, self.user.skills.all())
        self.assertIn(self.skill2, self.user.skills.all())

    def test_user_string_representation(self):
        self.assertEqual(str(self.user), 'testuser')

    def test_user_full_name(self):
        self.assertEqual(self.user.get_full_name(), 'Test User')

    def test_user_short_name(self):
        self.assertEqual(self.user.get_short_name(), 'Test')

    def test_user_without_name(self):
        user_without_name = User.objects.create_user(
            username='nonameuser',
            password='testpassword',
            email='nonameuser@example.com'
        )
        self.assertEqual(user_without_name.get_full_name(), 'nonameuser')
        self.assertEqual(user_without_name.get_short_name(), 'nonameuser')