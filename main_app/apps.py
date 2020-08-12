from django.apps import AppConfig


class MainAppConfig(AppConfig):
    name = 'main_app'
    verbose_name='Roadstar Main App'

    def ready(self):
        import main_app.signals # NOTE: If just using the @receiver() decorator, just import the signals module
