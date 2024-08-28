from django.core.management.base import BaseCommand
from resourceaccommodator import views

class Command(BaseCommand):
    help = "get information for Orderable Items in Confluence"
    
    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Get orderable items: "%s"' % views.get_orderable_item()))
