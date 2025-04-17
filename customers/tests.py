from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Customer, CustomerCategory

class CustomerModelTest(TestCase):
    def setUp(self):
        self.category = CustomerCategory.objects.create(name='VIP')
        self.customer = Customer.objects.create(
            name='عميل تجريبي',
            code='CUST001',
            phone='01000000000',
            email='test@example.com',
            customer_type='retail',
            status='active',
            category=self.category
        )

    def test_customer_str(self):
        self.assertEqual(str(self.customer), 'عميل تجريبي')

    def test_customer_code_unique(self):
        with self.assertRaises(Exception):
            Customer.objects.create(
                name='عميل آخر',
                code='CUST001',
                phone='01111111111',
                email='other@example.com',
                customer_type='retail',
                status='active',
                category=self.category
            )

class CustomerViewsTest(TestCase):
    def setUp(self):
        self.User = get_user_model()
        self.user = self.User.objects.create_user(username='testuser', password='testpass123')
        self.client = Client()
        self.category = CustomerCategory.objects.create(name='VIP')
        self.customer = Customer.objects.create(
            name='عميل تجريبي',
            code='CUST002',
            phone='01000000001',
            email='test2@example.com',
            customer_type='retail',
            status='active',
            category=self.category
        )
        self.client.login(username='testuser', password='testpass123')

    def test_customer_list_view(self):
        response = self.client.get(reverse('customers:customer_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'عميل تجريبي')

    def test_customer_create_view(self):
        response = self.client.post(reverse('customers:customer_create'), {
            'name': 'عميل جديد',
            'code': 'CUST003',
            'phone': '01234567890',
            'email': 'new@example.com',
            'customer_type': 'retail',
            'status': 'active',
            'category': self.category.id
        })
        self.assertEqual(response.status_code, 302)  # Redirect after create
        self.assertTrue(Customer.objects.filter(code='CUST003').exists())

    def test_customer_delete_view(self):
        response = self.client.post(reverse('customers:customer_delete', args=[self.customer.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Customer.objects.filter(id=self.customer.id).exists())
