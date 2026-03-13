from django.db import models


class BaseModel(models.Model):
    """Abstract base model that adds created_at and updated_at to every model."""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Priority(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Priority"
        verbose_name_plural = "Priorities"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Category(BaseModel):
    name = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(BaseModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    deadline = models.DateTimeField(blank=True, null=True)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Pending",
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )
    priority = models.ForeignKey(
        Priority,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
    )

    class Meta:
        verbose_name = "Task"
        verbose_name_plural = "Tasks"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Note(BaseModel):
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="notes",
    )
    content = models.TextField()

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Note for: {self.task.title[:50]}"


class SubTask(BaseModel):
    STATUS_CHOICES = [
        ("Pending", "Pending"),
        ("In Progress", "In Progress"),
        ("Completed", "Completed"),
    ]

    parent_task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        related_name="subtasks",
    )
    title = models.CharField(max_length=255)
    status = models.CharField(
        max_length=50,
        choices=STATUS_CHOICES,
        default="Pending",
    )

    class Meta:
        verbose_name = "Sub Task"
        verbose_name_plural = "Sub Tasks"
        ordering = ["parent_task", "title"]

    def __str__(self):
        return self.title
