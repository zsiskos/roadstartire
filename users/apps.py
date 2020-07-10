from django.apps import AppConfig

class UsersConfig(AppConfig):
    name = 'users'
    verbose_name = '👤 Users'

    def ready(self):
        import users.signals # NOTE: If just using the @receiver() decorator, just import the signals module