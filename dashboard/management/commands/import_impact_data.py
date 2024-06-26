import csv
from django.core.management.base import BaseCommand
from django.conf import settings
import os
from decimal import Decimal, InvalidOperation
from dashboard.models import ImpactData, Report

def safe_convert_to_decimal(value):
    try:
        # Remove pontos e substitui vírgulas por pontos
        cleaned_value = value.replace('.', '').replace(',', '.')
        return Decimal(cleaned_value)
    except InvalidOperation:
        return None

class Command(BaseCommand):
    help = 'Imports impact data from a CSV file into the ImpactData model'

    def handle(self, *args, **options):
        file_path = os.path.join(settings.BASE_DIR, 'data', 'impact_data.csv')  # Caminho fixo para o arquivo CSV
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                report_name = row['REPORT FONTE (EXTERNAL KEY)']
                try:
                    report = Report.objects.get(name=report_name)
                except Report.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f'Report not found: {report_name}'))
                    continue  # Skip to next row
                
                impact_data, created = ImpactData.objects.update_or_create(
                    year=int(row['ANO']),
                    impact=row['IMPACTO'],
                    condition_or_attack=row['CONDIÇÃO/ATAQUE'],  
                    company_size=row['TAMANHO EMPRESA'],       
                    region=row['REGIÃO'],                       
                    country=row['PAÍS'],                       
                    sector=row['SETOR'],                        
                    report=report,                              
                    defaults={
                        'probability': safe_convert_to_decimal(row['PROBABILIDADE']),
                        'cost': safe_convert_to_decimal(row['CUSTO']),
                        'cost_metric': row['MÉTRICA (custo)']
                    }
                )

                # Loga se foi criado ou atualizado
                action = 'created' if created else 'updated'
                self.stdout.write(self.style.SUCCESS(f'Successfully {action} impact data for report: {report_name}'))

            self.stdout.write(self.style.SUCCESS('Successfully imported impact data'))
