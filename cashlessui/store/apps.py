from django.apps import AppConfig
from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    #def ready(self):
    #    # Ensure roles (groups) are created
    #    self.create_roles()

    #def create_roles(self):
    #    from django.contrib.auth.models import Group
    # 
    #    roles = ['Admin', 'Owner', 'Manager', 'Customer', 'None']
    #    for role in roles:
    #        Group.objects.get_or_create(name=role)
