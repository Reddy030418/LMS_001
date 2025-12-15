import csv
from django.core.management.base import BaseCommand
from portal.models import Eresource

class Command(BaseCommand):
    help = 'Import e-resources from CSV file'

    def handle(self, *args, **options):
        csv_file_path = 'data/eresources.csv'
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    name = row['name'].strip()
                    description = row['description'].strip()
                    url = row['url'].strip()
                    letter = row.get('letter', '').strip()

                    eresource, created = Eresource.objects.get_or_create(
                        name=name,
                        defaults={
                            'description': description,
                            'url': url,
                            'letter': letter,
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Added e-resource: {name}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipped existing e-resource: {name}'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file {csv_file_path} not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing e-resources: {str(e)}'))
