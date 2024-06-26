import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from dashboard.models import Publisher  

class Command(BaseCommand):
    help = 'Imports publishers from a CSV file into the Publisher model'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'publishers.csv')
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                publisher_name = row['PUBLISHER']
                reputation = row['REPUTAÇÃO']

                publisher, created = Publisher.objects.update_or_create(
                    name=publisher_name,
                    defaults={'reputation': int(reputation) if reputation.isdigit() else 0}
                )

                # Loga se foi criado ou atualizado
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new publisher: {publisher_name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated existing publisher: {publisher_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully imported publishers'))
