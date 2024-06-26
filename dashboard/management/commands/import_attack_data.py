import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from decimal import Decimal, InvalidOperation
from dashboard.models import AttackData, Report

def safe_convert_to_decimal(value):
    try:
        # Remove pontos e substitui vírgulas por pontos
        cleaned_value = value.replace('.', '').replace(',', '.')
        return Decimal(cleaned_value)
    except InvalidOperation:
        return None

class Command(BaseCommand):
    help = 'Imports attack data from a CSV file into the AttackData model'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'attack_data.csv')  # Caminho fixo para o arquivo CSV
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                report_name = row['REPORT FONTE (EXTERNAL KEY)']
                try:
                    report = Report.objects.get(name=report_name)
                except Report.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Report not found: {report_name}'))
                    continue  # Skip to next row

                attack_data, created = AttackData.objects.update_or_create(
                    year=int(row['ANO']),
                    attack_type=row['ATAQUE'],
                    condition=row['CONDIÇÃO'], 
                    company_size=row['TAMANHO EMPRESA'], 
                    region=row['REGIÃO'],  
                    country=row['PAÍS'],  
                    sector=row['SETOR'],  
                    cost_metric=row['MÉTRICA (custo)'],
                    report=report, 
                    defaults={
                        'probability': safe_convert_to_decimal(row['PROBABILIDADE']) if row['PROBABILIDADE'] else None,
                        'cost': safe_convert_to_decimal(row['CUSTO']) if row['CUSTO'] else None,
                    }
                )

                # Loga se foi criado ou atualizado
                if created:
                    self.stdout.write(self.style.SUCCESS(f'Created new attack data for report: {report_name}'))
                else:
                    self.stdout.write(self.style.SUCCESS(f'Updated existing attack data for report: {report_name}'))

            self.stdout.write(self.style.SUCCESS('Successfully imported attack data'))
