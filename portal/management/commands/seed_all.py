from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = "Seed the PostgreSQL database with all data: departments, categories, books, users, e-resources, news, and transactions."

    def add_arguments(self, parser):
        parser.add_argument(
            "--skip-transactions",
            action="store_true",
            help="Skip generating synthetic transactions",
        )
        parser.add_argument(
            "--tx-count",
            type=int,
            default=3000,
            help="Number of synthetic transactions to generate (default: 3000)",
        )

    def handle(self, *args, **options):
        self.stdout.write("=" * 60)
        self.stdout.write("  ANU LMS - Full Database Seed")
        self.stdout.write("=" * 60)

        steps = [
            ("import_departments", "Importing departments..."),
            ("import_categories", "Importing book categories..."),
            ("import_books", "Importing books..."),
            ("import_users", "Importing users & profiles..."),
            ("import_eresources", "Importing e-resources..."),
            ("import_news", "Importing news items..."),
        ]

        for cmd_name, msg in steps:
            self.stdout.write("-" * 40)
            self.stdout.write(self.style.HTTP_INFO("[>] %s" % msg))
            try:
                call_command(cmd_name)
                self.stdout.write(self.style.SUCCESS("  [OK] %s completed" % cmd_name))
            except Exception as e:
                self.stderr.write(self.style.ERROR("  [FAIL] %s failed: %s" % (cmd_name, e)))

        # Create superuser admin if not exists
        self.stdout.write("-" * 40)
        self.stdout.write(self.style.HTTP_INFO("[>] Creating admin superuser..."))
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@anu.edu",
                password="admin@123",
            )
            self.stdout.write(self.style.SUCCESS("  [OK] Created superuser: admin / admin@123"))
        else:
            self.stdout.write("  Superuser 'admin' already exists, skipping.")

        # Generate synthetic transactions
        if not options["skip_transactions"]:
            self.stdout.write("-" * 40)
            tx_count = options["tx_count"]
            self.stdout.write(self.style.HTTP_INFO("[>] Generating %d synthetic transactions..." % tx_count))
            try:
                call_command("generate_transactions", count=tx_count)
                self.stdout.write(self.style.SUCCESS("  [OK] Transactions generated"))
            except Exception as e:
                self.stderr.write(self.style.ERROR("  [FAIL] Transaction generation failed: %s" % e))
        else:
            self.stdout.write(self.style.WARNING("  Skipping transaction generation (--skip-transactions)"))

        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS("  DATABASE SEED COMPLETE"))
        self.stdout.write("=" * 60)
        self.stdout.write(self.style.SUCCESS(
            "\nYou can now run: python manage.py runserver\n"
            "  Admin login:   admin / admin@123\n"
            "  Student login:  2022CSE001 / anu@123\n"
            "  Librarian login: LIB001 / lib@123"
        ))
