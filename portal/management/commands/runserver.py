from django.core.management.commands.runserver import Command as BaseRunserverCommand

class Command(BaseRunserverCommand):
    default_port = '5500'
