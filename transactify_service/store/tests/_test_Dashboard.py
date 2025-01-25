from django.test import TestCase, Client
from django.contrib.auth.models import User, Group
from django.urls import reverse
from django.conf import settings


class DashboardViewTests(TestCase):
    def setUp(self):
        # Create groups
        self.admin_group = Group.objects.create(name="Admins")
        self.owner_group = Group.objects.create(name="Owner")
        self.manager_group = Group.objects.create(name="Manager")
        self.customer_group = Group.objects.create(name="Customer")
        
        # Create users
        self.admin_user = User.objects.create_user(username="admin", password="adminpassword")
        self.owner_user = User.objects.create_user(username="owner", password="ownerpassword")
        self.manager_user = User.objects.create_user(username="manager", password="managerpassword")
        self.customer_user = User.objects.create_user(username="customer", password="customerpassword")
        
        # Assign groups
        self.admin_user.groups.add(self.admin_group)
        self.owner_user.groups.add(self.owner_group)
        self.manager_user.groups.add(self.manager_group)
        self.customer_user.groups.add(self.customer_group)
        
        # Create test client
        self.client = Client()

    def test_dashboard_redirects_admin(self):
        self.client.login(username="admin", password="adminpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, "/admin/")

    def test_dashboard_renders_for_owner(self):
        self.client.login(username="owner", password="ownerpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Don Knabberello")

    def test_dashboard_renders_for_manager(self):
        self.client.login(username="manager", password="managerpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Don Knabberello")

    def test_dashboard_renders_for_customer(self):
        self.client.login(username="customer", password="customerpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Don Knabberello")

    def test_dashboard_redirects_unauthenticated(self):
        response = self.client.get(reverse("dashboard"))
        self.assertRedirects(response, f"{settings.LOGIN_URL}?next={reverse('dashboard')}")

    def test_dashboard_handles_empty_entries(self):
        self.client.login(username="customer", password="customerpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No entries available.")  # Update the template to handle empty entries

    def test_dashboard_entry_links(self):
        self.client.login(username="customer", password="customerpassword")
        response = self.client.get(reverse("dashboard"))
        self.assertContains(response, f"/{settings.STORE_NAME}/customers/")
