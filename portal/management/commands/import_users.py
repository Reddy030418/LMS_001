import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password
from portal.models import Profile, Department


class Command(BaseCommand):
    help = "Import users and profiles from data/users.csv"

    def add_arguments(self, parser):
        parser.add_argument(
            "--csv",
            type=str,
            default="data/users.csv",
            help="Path to the users CSV file (default: data/users.csv)",
        )

    def handle(self, *args, **options):
        csv_path = options["csv"]
        created_count = 0
        skipped_count = 0

        try:
            with open(csv_path, newline="", encoding="utf-8") as file:
                reader = csv.DictReader(file)

                for row in reader:
                    username = row["username"].strip()
                    role = row.get("role", "student").strip()

                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            "first_name": row.get("first_name", "").strip(),
                            "last_name": row.get("last_name", "").strip(),
                            "email": row.get("email", "").strip(),
                            "password": make_password(row.get("password", "anu@123")),
                            "is_active": row.get("is_active", "TRUE").upper() == "TRUE",
                            "is_staff": role in ("librarian", "admin"),
                            "is_superuser": role == "admin",
                        },
                    )

                    if created:
                        dept_code = row.get("department_code", "").strip()
                        dept = None
                        if dept_code:
                            try:
                                dept = Department.objects.get(code=dept_code)
                            except Department.DoesNotExist:
                                self.stderr.write(
                                    self.style.WARNING(f"Department '{dept_code}' not found for user '{username}'")
                                )

                        year_str = row.get("year", "").strip()
                        year_val = int(year_str) if year_str and year_str.isdigit() else None

                        Profile.objects.update_or_create(
                            user=user,
                            defaults={
                                "role": role,
                                "department": dept,
                                "roll_number": row.get("roll_number", "").strip(),
                                "course": row.get("course", "").strip(),
                                "year": year_val,
                                "phone": row.get("phone", "").strip(),
                            },
                        )
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f"Created user: {username} (role: {role})"))
                    else:
                        skipped_count += 1
                        self.stdout.write(f"Skipped existing user: {username}")

        except FileNotFoundError:
            self.stderr.write(self.style.ERROR(f"CSV file not found: {csv_path}"))
            return
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing users: {e}"))
            return

        self.stdout.write(
            self.style.SUCCESS(f"\nDone! Created: {created_count}, Skipped: {skipped_count}")
        )
