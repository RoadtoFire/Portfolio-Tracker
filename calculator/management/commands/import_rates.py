import csv
from django.core.management.base import BaseCommand
from calculator.models import Stock, PurificationRate  # Updated Import!
from datetime import datetime

class Command(BaseCommand):
    help = 'Import purification rates from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        self.stdout.write(f"Reading from {csv_file_path}...")

        try:
            with open(csv_file_path, 'r') as file:
                # 1. Strip whitespace from headers just in case
                reader = csv.DictReader(file)
                
                # Normalize headers (remove BOM or spaces)
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

                count = 0
                for row in reader:
                    # --- THE FIX IS HERE ---
                    symbol_raw = row.get('Symbol', '').strip()
                    
                    # Skip comments, empty lines, or lines without a symbol
                    if not symbol_raw or symbol_raw.startswith('#'):
                        continue
                    
                    # Skip lines where CompanyName is missing (prevent the NOT NULL error)
                    company_name = row.get('CompanyName')
                    if not company_name:
                        continue 
                    # -----------------------

                    # 1. Get or Create Stock
                    stock, _ = Stock.objects.get_or_create(
                        symbol=symbol_raw.upper(),
                        defaults={'name': company_name.strip()}
                    )
                    
                    # 2. Parse Date
                    try:
                        eff_date = datetime.strptime(row['EffectiveDate'].strip(), '%Y-%m-%d').date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f"Skipping row with invalid date: {row}"))
                        continue

                    # 3. Update or Create Rate
                    PurificationRate.objects.update_or_create(
                        stock=stock,
                        effective_date=eff_date,
                        defaults={'impurity_percentage': row['ImpurityPercentage'].strip()}
                    )
                    count += 1
            
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {count} rates!'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR('File not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))