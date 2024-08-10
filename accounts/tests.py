from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Skill
from decimal import Decimal


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
        
class UserViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='testuser@example.com',
            name='Test User',
            is_developer=True
        )
        self.skill = Skill.objects.create(name='Python')
        self.user.skills.add(self.skill)

    def test_user_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:user_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/Templates/user_profile.html')
        self.assertEqual(response.context['user'], self.user)

    def test_edit_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:edit_profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/Templates/edit_profile.html')

        # Test profile update
        new_data = {
            'name': 'Updated Name',
            'bio': 'Updated bio',
            'is_developer': False,
            'is_client': True,
            'email': 'testuser@example.com',  # Include the email field
            'username': 'testuser',  # Include the username field
        }
        response = self.client.post(reverse('accounts:edit_profile'), new_data)
        
        if response.status_code != 302:
            print("Form errors:", response.context['form'].errors)
        
        self.assertRedirects(response, reverse('accounts:user_profile'))
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, 'Updated Name')
        self.assertEqual(self.user.bio, 'Updated bio')
        self.assertFalse(self.user.is_developer)
        self.assertTrue(self.user.is_client)

    def test_search_developer_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:search_developer'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search_developer.html')
        self.assertIn('skills', response.context)

    def test_results_search_devs_view(self):
        self.client.login(username='testuser', password='testpassword')
        session = self.client.session
        session['search_name'] = 'Test'
        session['search_skill'] = str(self.skill.id)
        session.save()

        response = self.client.get(reverse('accounts:results_search_devs'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'results_search_devs.html')
        self.assertIn('developers', response.context)
        self.assertIn(self.user, response.context['developers'])

    def test_view_profile_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:view_profile', args=[self.user.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'view_profile.html')
        self.assertEqual(response.context['profile_user'], self.user)
        self.assertTrue(response.context['can_view_sensitive_info'])

    def test_add_wave_view(self):
        self.client.login(username='testuser', password='testpassword')
        response = self.client.get(reverse('accounts:add_wave'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'add_wave.html')

        # Test adding wave balance
        initial_balance = self.user.wave_balance
        response = self.client.post(reverse('accounts:add_wave'), {'amount': 50.00})
        self.assertRedirects(response, reverse('accounts:user_profile'))
        self.user.refresh_from_db()
        
        # Convert initial_balance to Decimal before addition
        expected_balance = Decimal(str(initial_balance)) + Decimal('50.00')
        self.assertEqual(self.user.wave_balance, expected_balance)

class SkillModelTests(TestCase):
    def test_skill_creation(self):
        skill = Skill.objects.create(name='JavaScript', description='Programming language')
        self.assertEqual(str(skill), 'JavaScript')
        self.assertEqual(skill.description, 'Programming language')