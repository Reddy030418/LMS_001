import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from portal.models import Profile, Department

class Command(BaseCommand):
    help = "Import users from CSV"

    def handle(self, *args, **options):
        with open("data/users.csv", newline="", encoding="utf-8") as file:
            reader = csv.DictReader(file)

            for row in reader:
                is_active_str = row.get("is_active", "true")
                is_active = is_active_str.lower() == "true" if is_active_str else True

                user, created = User.objects.get_or_create(
                    username=row["username"],
                    defaults={
                        "email": row["email"],
                        "first_name": row["first_name"],
                        "last_name": row["last_name"],
                        "is_active": is_active
                    }
                )

                if created:
                    user.set_password(row["password"])
                    user.save()

                    department = Department.objects.get(code=row["department_code"])

                    year_str = row.get("year")
                    year = int(year_str) if year_str and year_str.strip() else None

                    Profile.objects.get_or_create(
                        user=user,
                        defaults={
                            "role": row["role"],
                            "department": department,
                            "roll_number": row["roll_number"],
                            "course": row["course"],
                            "year": year,
                            "phone": row["phone"]
                        }
                    )

                    self.stdout.write(self.style.SUCCESS(f"Created {user.username}"))
                else:
                    self.stdout.write(f"Skipped {user.username}")
