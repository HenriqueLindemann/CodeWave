from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from .models import Project, Task, TaskApplication, ProgrammingLanguage
from django.contrib.messages import get_messages

User = get_user_model()

class ProjectModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            category='Web',
            created_by=self.user
        )
        self.language1 = ProgrammingLanguage.objects.create(name='Python')
        self.language2 = ProgrammingLanguage.objects.create(name='JavaScript')
        self.task1 = Task.objects.create(
            project=self.project,
            title='Task 1',
            description='Description 1',
            due_date='2023-12-31',
            initial_value=100.00
        )
        self.task1.programming_languages.add(self.language1)
        self.task2 = Task.objects.create(
            project=self.project,
            title='Task 2',
            description='Description 2',
            due_date='2023-12-31',
            initial_value=200.00
        )
        self.task2.programming_languages.add(self.language2)

    def test_project_creation(self):
        self.assertEqual(self.project.title, 'Test Project')
        self.assertEqual(self.project.created_by, self.user)

    def test_get_unique_languages(self):
        unique_languages = self.project.get_unique_languages()
        self.assertEqual(len(unique_languages), 2)
        self.assertIn(self.language1, unique_languages)
        self.assertIn(self.language2, unique_languages)

class ProjectDetailViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='12345',
            email='testuser@example.com' 
        )
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            category='Web',
            created_by=self.user
        )
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='A test task',
            due_date='2023-12-31',
            initial_value=100.00
        )

    def test_project_detail_view(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('projects:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
        self.assertContains(response, self.task.title)

    def test_project_detail_view_not_logged_in(self):
        response = self.client.get(reverse('projects:project_detail', args=[self.project.id]))
        print(f"Initial redirect URL: {response.url}") 

        response = self.client.get(reverse('projects:project_detail', args=[self.project.id]), follow=True)
        print(f"Redirect chain: {response.redirect_chain}")

        self.assertEqual(response.status_code, 200)  # Deve terminar em uma página renderizada
        
        login_url = reverse('login')
        self.assertTrue(any(login_url in redirect[0] for redirect in response.redirect_chain))
        
        expected_next_param = f'/projects/{self.project.id}/'
        self.assertTrue(any(expected_next_param in redirect[0] for redirect in response.redirect_chain))

    def test_is_project_owner(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.get(reverse('projects:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['is_project_owner'])

        other_user = User.objects.create_user(
            username='otheruser',
            password='12345',
            email='otheruser@example.com'  # Use um email diferente
        )
        self.client.login(username='otheruser', password='12345')
        response = self.client.get(reverse('projects:project_detail', args=[self.project.id]))
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['is_project_owner'])

class ProjectViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='12345', email='testuser@example.com')
        self.project = Project.objects.create(
            title='Test Project',
            description='A test project',
            category='Web',
            created_by=self.user
        )
        self.task = Task.objects.create(
            project=self.project,
            title='Test Task',
            description='A test task',
            due_date='2023-12-31',
            initial_value=100.00,
            status='open',
            application_status='open'
        )
        self.language = ProgrammingLanguage.objects.create(name='Python')
        self.task.programming_languages.add(self.language)

    def test_create_project(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:create_project')
        data = {
            'title': 'New Project',
            'description': 'A new project description',
            'category': 'Mobile',
            'tasks-TOTAL_FORMS': '1',
            'tasks-INITIAL_FORMS': '0',
            'tasks-MIN_NUM_FORMS': '0',
            'tasks-MAX_NUM_FORMS': '1000',
            'tasks-0-title': 'New Task',
            'tasks-0-description': 'A new task description',
            'tasks-0-due_date': '2024-12-31',
            'tasks-0-initial_value': '200.00',
        }
        response = self.client.post(url, data)
        
        print(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            print("Response content:", response.content.decode())
            
            if 'form' in response.context:
                print("Project form errors:", response.context['form'].errors)
            if 'task_formset' in response.context:
                print("Task formset errors:", response.context['task_formset'].errors)
        
        # Verificar se o projeto foi criado
        project_exists = Project.objects.filter(title='New Project').exists()
        print(f"Project exists: {project_exists}")
        
        if project_exists:
            project = Project.objects.get(title='New Project')
            print(f"Project ID: {project.id}")
            print(f"Project tasks count: {project.tasks.count()}")
        
        self.assertTrue(project_exists, "O projeto não foi criado.")
        
        if project_exists:
            project = Project.objects.get(title='New Project')
            self.assertTrue(Task.objects.filter(project=project, title='New Task').exists(), "A tarefa não foi criada.")

    def test_edit_project(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:edit_project', args=[self.project.id])
        data = {
            'title': 'Updated Project',
            'description': 'An updated project description',
            'category': 'Mobile',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after edit
        self.project.refresh_from_db()
        self.assertEqual(self.project.title, 'Updated Project')

    def test_apply_for_task(self):
        other_user = User.objects.create_user(username='otheruser', password='12345', email='other@example.com')
        self.client.login(username='otheruser', password='12345')
        url = reverse('projects:apply_for_task', args=[self.task.id])
        data = {
            'proposed_value': '150.00',
            'comment': 'I would like to work on this task',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after application
        self.assertTrue(TaskApplication.objects.filter(task=self.task, developer=other_user).exists())

    def test_review_application(self):
        other_user = User.objects.create_user(username='otheruser', password='12345', email='other@example.com')
        application = TaskApplication.objects.create(
            task=self.task,
            developer=other_user,
            proposed_value='150.00',
            status='pending'
        )
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:review_application', args=[application.id])
        data = {
            'action': 'accept',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after review
        application.refresh_from_db()
        self.task.refresh_from_db()
        self.assertEqual(application.status, 'accepted')
        self.assertEqual(self.task.status, 'in_progress')
        self.assertEqual(self.task.assigned_to, other_user)

    def test_submit_final_delivery(self):
        self.task.assigned_to = self.user
        self.task.status = 'in_progress'
        self.task.save()
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:submit_final_delivery', args=[self.task.id])
        data = {
            'comments': 'Task completed successfully',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after submission
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'under_review')
        self.assertEqual(self.task.final_delivery_comments, 'Task completed successfully')

    def test_review_task(self):
        self.task.status = 'under_review'
        self.task.save()
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:review_task', args=[self.task.id])
        data = {
            'review_status': 'approved',
            'feedback': 'Great work!',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect after review
        self.task.refresh_from_db()
        self.assertEqual(self.task.status, 'completed')
        self.assertEqual(self.task.feedback, 'Great work!')

    def test_delete_task(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:delete_task', args=[self.task.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)  # JSON response
        data = response.json()
        self.assertTrue(data['success'])
        self.assertFalse(Task.objects.filter(id=self.task.id).exists())

    def test_search_projects(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:search_projects')
        data = {
            'searchInput': 'Test',
            'categorySelect': 'Web',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect to results page
        session = self.client.session
        self.assertEqual(session['search_title'], 'Test')
        self.assertEqual(session['search_category'], 'Web')

    def test_results_search_projects(self):
        self.client.login(username='testuser', password='12345')
        session = self.client.session
        session['search_title'] = 'Test'
        session['search_category'] = 'Web'
        session.save()
        url = reverse('projects:results_search_projects')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Project')

    def test_search_tasks(self):
        self.client.login(username='testuser', password='12345')
        url = reverse('projects:search_tasks')
        data = {
            'searchInput': 'Test',
            'projectSelect': str(self.project.id),
            'languageSelect': str(self.language.id),
            'applicationStatusSelect': 'open',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)  # Redirect to results page
        session = self.client.session
        self.assertEqual(session['search_title'], 'Test')
        self.assertEqual(session['search_project'], str(self.project.id))
        self.assertEqual(session['search_language'], str(self.language.id))
        self.assertEqual(session['search_app_status'], 'open')

    def test_results_search_tasks(self):
        self.client.login(username='testuser', password='12345')
        session = self.client.session
        session['search_title'] = 'Test'
        session['search_project'] = str(self.project.id)
        session['search_language'] = str(self.language.id)
        session['search_app_status'] = 'open'
        session.save()
        url = reverse('projects:results_search_tasks')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Task')   