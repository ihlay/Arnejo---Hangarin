from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker
from taskapp.models import Priority, Category, Task, Note, SubTask

fake = Faker()


class Command(BaseCommand):
    help = "Populate database with Priority/Category data and fake Tasks, Notes, SubTasks."

    def handle(self, *args, **options):
        self.stdout.write("=" * 50)
        self.stdout.write("Hangarin — Populating Database")
        self.stdout.write("=" * 50)

        priority_names = ["High", "Medium", "Low", "Critical", "Optional"]
        priorities = []
        for name in priority_names:
            obj, created = Priority.objects.get_or_create(name=name)
            priorities.append(obj)
            status = "created" if created else "already exists"
            self.stdout.write(f"  Priority '{name}' — {status}")
        self.stdout.write(self.style.SUCCESS(f"Priorities ready\n"))

        category_names = ["Work", "School", "Personal", "Finance", "Projects"]
        categories = []
        for name in category_names:
            obj, created = Category.objects.get_or_create(name=name)
            categories.append(obj)
            status = "created" if created else "already exists"
            self.stdout.write(f"  Category '{name}' — {status}")
        self.stdout.write(self.style.SUCCESS(f"Categories ready\n"))

        self.stdout.write("Generating 20 fake Tasks...")
        for _ in range(20):
            Task.objects.create(
                title=fake.sentence(nb_words=5),
                description=fake.paragraph(nb_sentences=3),
                deadline=timezone.make_aware(fake.date_time_this_month()),
                status=fake.random_element(elements=["Pending", "In Progress", "Completed"]),
                category=fake.random_element(elements=categories),
                priority=fake.random_element(elements=priorities),
            )
        self.stdout.write(self.style.SUCCESS("20 Tasks created\n"))

        all_tasks = list(Task.objects.all())
        self.stdout.write("Generating 30 fake Notes...")
        for _ in range(30):
            Note.objects.create(
                task=fake.random_element(elements=all_tasks),
                content=fake.paragraph(nb_sentences=3),
            )
        self.stdout.write(self.style.SUCCESS("30 Notes created\n"))

        self.stdout.write("Generating 40 fake SubTasks...")
        for _ in range(40):
            SubTask.objects.create(
                parent_task=fake.random_element(elements=all_tasks),
                title=fake.sentence(nb_words=5),
                status=fake.random_element(elements=["Pending", "In Progress", "Completed"]),
            )
        self.stdout.write(self.style.SUCCESS("40 SubTasks created\n"))

        self.stdout.write("=" * 50)
        self.stdout.write(self.style.SUCCESS("Done!"))
        self.stdout.write(f"  Priorities : {Priority.objects.count()}")
        self.stdout.write(f"  Categories : {Category.objects.count()}")
        self.stdout.write(f"  Tasks      : {Task.objects.count()}")
        self.stdout.write(f"  Notes      : {Note.objects.count()}")
        self.stdout.write(f"  SubTasks   : {SubTask.objects.count()}")