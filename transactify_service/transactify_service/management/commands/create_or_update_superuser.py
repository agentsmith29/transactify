import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = "Create or update a superuser with environment variables"

    def handle(self, *args, **kwargs):
        # Fetch environment variables
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL")

        # Ensure all required environment variables are set
        if not username or not password or not email:
            self.stderr.write("Error: All required environment variables are not set.")
            self.stderr.write("Required: DJANGO_SUPERUSER_USERNAME, DJANGO_SUPERUSER_PASSWORD, DJANGO_SUPERUSER_EMAIL")
            return

        # Get the user model
        User = get_user_model()

        # Also create the groups admin, owner, manager, customer
        grp_admin, _ = Group.objects.get_or_create(name='admin')
        grp_owner, _ = Group.objects.get_or_create(name='owner')
        grp_manager, _ = Group.objects.get_or_create(name='manager')
        grp_customer, _ =Group.objects.get_or_create(name='customer')

        # Check if the superuser already exists
        try:
            user = User.objects.get(username=username)
            user.groups.add(grp_admin)
            # Update the user's password and email
            user.set_password(password)
            user.email = email
            user.save()
            self.stdout.write(f"Updated password and email for existing superuser '{username}'.")
        except User.DoesNotExist:
            # Create a new superuser
            User.objects.create_superuser(username=username, password=password, email=email)
            self.stdout.write(f"Created new superuser '{username}'.")

        

        # add the superuser to the admin group
       
        

