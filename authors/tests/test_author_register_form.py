from django.test import TestCase
from django.urls import reverse
from authors.forms import RegisterForm
from parameterized import parameterized

class AuthorRegisterFormUnitTest(TestCase):
    @parameterized.expand([
        ('username', 'Your username'),
        ('email', 'Your email'),
        ('first_name', 'Your first name'),
        ('last_name', 'Your last name'),
        ('password', 'Your password'),
        ('password2', 'Repeat your password'),
    ])
    def test_fields_placeholder(self, field, placeholder):
        form = RegisterForm()
        current_placeholder = form[field].field.widget.attrs['placeholder']
        self.assertEqual(current_placeholder, placeholder)


    @parameterized.expand([
        ('password', 'Password must have at least one uppercase letter, one lowercase letter and one number. The length should be at least 8 characters'),
        ('email', 'The email must be valid'),
        ('username', 'Username must have letters, numbers or one of those @.+-_ and the length between 4 and 150 characters')
    ])
    def test_fields_help_text(self, field, needed):
        form = RegisterForm()
        current = form[field].field.help_text
        self.assertEqual(current, needed)


    @parameterized.expand([
        ('username', 'Username'),
        ('email', 'Email'),
        ('first_name', 'First name'),
        ('last_name', 'Last name'),
        ('password', 'Password'),
        ('password2', 'Password2')
    ])
    def test_fields_placeholder(self, field, needed):
        form = RegisterForm()
        current = form[field].field.label
        self.assertEqual(current, needed)


class AuthorRegisterFormIntegrationTest(TestCase):
    def setUp(self, *args, **kwargs):
        self.form_data = {
            'username': 'user',
            'first_name': 'first',
            'last_name': 'last',
            'email': 'email@anyemail.com',
            'password': 'Str0ngP@ssword1',
            'password2': 'Str0ngP@ssword1',
        }

        return super().setUp(*args, **kwargs)


    @parameterized.expand([
        ('username', 'This field must not be empty'),
        ('first_name', 'Write your first name'),
        ('last_name', 'Write your last name'),
        ('password', 'Password must not be empty'),
        ('password2', 'Password confirmation must not be empty'),
        ('email', 'Write your email'),
    ])
    def test_fields_cannot_be_empty(self, field, msg):
        self.form_data[field] = ''
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get(field))

    
    def test_username_field_min_length_should_be_4(self):
        self.form_data['username'] = 'Joa'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Username minimum length is 4 characters'
        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))


    def test_username_field_max_length_should_be_150(self):
        self.form_data['username'] = 'A' * 151
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Username maximum length is 150 characters'
        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('username'))

    
    def test_password_field_have_lower_upper_case_letters_and_numbers(self):
        self.form_data['password'] = 'bc123ABC_'
        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Password and password confirmation must be equal'
        # self.assertIn(msg, response.content.decode('utf-8'))
        self.assertIn(msg, response.context['form'].errors.get('password'))


    def test_password_and_password_confirmation_are_equal(self):
        self.form_data['password'] = '123456Aa_'
        self.form_data['password2'] = '123456Aa_'

        url = reverse('authors:register_create')
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'Password and password confirmation must be equal'
        self.assertNotIn(msg, response.content.decode('utf-8'))
        #self.assertNotIn(msg, response.context['form'].errors.get('password'))


    def test_send_get_request_to_registration_create_view_returns_404(self):
        url = reverse('authors:register_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
        

    def test_email_is_unique(self):
        self.form_data['email'] = 'email@email.com'

        url = reverse('authors:register_create')
        self.client.post(url, data=self.form_data, follow=True)
        response = self.client.post(url, data=self.form_data, follow=True)

        msg = 'User email is already in use'
        self.assertIn(msg, response.context['form'].errors.get('email'))
        self.assertIn(msg, response.content.decode('utf-8'))


    def test_author_created_and_login(self):
        url = reverse('authors:register_create')
        self.form_data.update({
            'username': 'testuser',
            'password': '123456Aa',
            'password2': '123456Aa'
        })

        self.client.post(url, data=self.form_data, follow=True)
        
        is_authenticated = self.client.login(
            username='testuser',
            password='123456Aa'
        )

        self.assertTrue(is_authenticated)
