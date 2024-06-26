import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from dashboard.models import Report, Publisher

class Command(BaseCommand):
    help = 'Imports reports from a CSV file into the Report model'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'reports.csv')  # Caminho fixo para o arquivo CSV, mudar na pasta data
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                publisher_name = row['PUBLISHER (EXTERNAL KEY)']
                try:
                    publisher = Publisher.objects.get(name=publisher_name)
                except Publisher.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Publisher not found: {publisher_name}'))
                    continue  

                _, created = Report.objects.update_or_create(
                    name=row['REPORT'],
                    defaults={
                        'link': row['LINK'],
                        'publisher': publisher,
                        'year': int(row['ANO']),
                        'periodicity': int(row['PERIOCIDADE']) if row['PERIOCIDADE'] else None,
                        'coverage': int(row['COBERTURA']) if row['COBERTURA'] else None,
                        'scope': int(row['ESCOPO']) if row['ESCOPO'] else None,
                        'attack_range': int(row['ABRANGÊNCIA DE ATAQUES']) if row['ABRANGÊNCIA DE ATAQUES'] else None,
                        'research_methodology': int(row['METODOLOGIA DE PESQUISA']) if row['METODOLOGIA DE PESQUISA'] else None,
                        'final_score': self.map_score(row['SCORE FINAL'])
                    }
                )
                action = 'created' if created else 'updated'
                self.stdout.write(self.style.SUCCESS(f'Successfully {action} report: {row["REPORT"]}'))

    def map_score(self, score):
        score_mapping = {
            'Muito Relevante': 'MR',
            'Relevante': 'R',
            'Pouco Relevante': 'PR'
        }
        return score_mapping.get(score, 'R')  # Retorna 'R' como default se não encontrar correspondência