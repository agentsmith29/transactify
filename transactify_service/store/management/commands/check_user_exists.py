from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Check if a user exists"

    def add_arguments(self, parser):
        parser.add_argument("username", type=str, help="Username to check")

    def handle(self, *args, **options):
        username = options["username"]
        User = get_user_model()
        exists = User.objects.filter(username=username).exists()
        self.stdout.write("true" if exists else "false")
