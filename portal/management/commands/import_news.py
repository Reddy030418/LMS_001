import csv
from django.core.management.base import BaseCommand
from django.utils import timezone
from portal.models import NewsItem

class Command(BaseCommand):
    help = 'Import news items from CSV file'

    def handle(self, *args, **options):
        csv_file_path = 'data/news.csv'
        try:
            with open(csv_file_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    title = row['title'].strip()
                    summary = row['summary'].strip()
                    image = row.get('image', '').strip()
                    published_str = row.get('published_on', '').strip()
                    try:
                        if published_str:
                            published_on = timezone.datetime.strptime(published_str, '%Y-%m-%d').date()
                        else:
                            published_on = timezone.now().date()
                    except ValueError:
                        self.stdout.write(self.style.WARNING(f'Invalid date for {title}, using current date'))
                        published_on = timezone.now().date()

                    news_item, created = NewsItem.objects.get_or_create(
                        title=title,
                        defaults={
                            'summary': summary,
                            'image': image,
                            'published_on': published_on,
                        }
                    )
                    if created:
                        self.stdout.write(self.style.SUCCESS(f'Added news item: {title}'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Skipped existing news item: {title}'))
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file {csv_file_path} not found.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error importing news: {str(e)}'))
