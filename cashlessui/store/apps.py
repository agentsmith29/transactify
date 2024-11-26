from django.apps import AppConfig
from django.apps import AppConfig

hwcontroller = None

class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    def ready(self):
        from .controller.HardwareController import HardwareController
        global hwcontroller
        hwcontroller = HardwareController()

    #def create_roles(self):
    #    from django.contrib.auth.models import Group
    # 
    #    roles = ['Admin', 'Owner', 'Manager', 'Customer', 'None']
    #    for role in roles:
    #        Group.objects.get_or_create(name=role)
