import sys

def is_running_migration():
    """
    Check if a migration is being executed.
    """
    migrate_keywords = ['migrate', 'makemigrations', 'createsuperuser', 'create_or_update_superuser',
                        'collectstatic']
    # Check if 'migrate' or 'makemigrations' is in the command-line arguments
    for keyword in migrate_keywords:
        if keyword in sys.argv:
            return True
    
    return False
        