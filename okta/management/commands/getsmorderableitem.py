from django.core.management.base import BaseCommand
from resourceaccommodator import views

class Command(BaseCommand):
    help = "get information for Self Managed Orderable Items"
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Get self managed orderable items: "%s"' % views.get_sm_orderable_item()))
