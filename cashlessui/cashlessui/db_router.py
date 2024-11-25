class MultiDatabaseRouter:
    """
    A database router to direct queries and migrations to the appropriate database.
    """

    # Define apps and models that should route to the USER database
    route_app_labels = {'auth', 'sessions', 'contenttypes', 'admin', 'cashlessui'}

    def db_for_read(self, model, **hints):
        """
        Direct read operations to the appropriate database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'USER'
        return 'default'

    def db_for_write(self, model, **hints):
        """
        Direct write operations to the appropriate database.
        """
        if model._meta.app_label in self.route_app_labels:
            return 'USER'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if models are in the same database or across both databases.
        """
        db_set = {'USER', 'default'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Direct migrations to the appropriate database.
        """
        if app_label in self.route_app_labels:
            return db == 'USER'
        return db == 'default'
