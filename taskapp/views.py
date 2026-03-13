from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.utils import timezone
from .models import Task, SubTask, Category, Priority, Note
from .forms import TaskForm, SubTaskForm, NoteForm, CategoryForm, PriorityForm



class HomePageView(TemplateView):
    template_name = "taskapp/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        now = timezone.now()
        ctx["total_tasks"] = Task.objects.count()
        ctx["pending"] = Task.objects.filter(status="Pending").count()
        ctx["in_progress"] = Task.objects.filter(status="In Progress").count()
        ctx["completed"] = Task.objects.filter(status="Completed").count()
        ctx["total_subtasks"] = SubTask.objects.count()
        ctx["total_notes"] = Note.objects.count()
        ctx["tasks_this_month"] = Task.objects.filter(
            created_at__year=now.year, created_at__month=now.month).count()
        ctx["overdue"] = Task.objects.filter(
            deadline__lt=now).exclude(status="Completed").count()
        ctx["status_data"] = list(Task.objects.values("status").annotate(count=Count("id")))
        ctx["category_data"] = list(Task.objects.values("category__name").annotate(count=Count("id")).order_by("-count")[:5])
        ctx["priority_data"] = list(Task.objects.values("priority__name").annotate(count=Count("id")).order_by("-count"))
        ctx["recent_tasks"] = Task.objects.select_related("priority", "category").order_by("-created_at")[:5]
        return ctx



class TaskListView(ListView):
    model = Task
    template_name = "taskapp/task_list.html"
    context_object_name = "tasks"
    paginate_by = 10

    def get_queryset(self):
        qs = Task.objects.select_related("priority", "category").all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        priority = self.request.GET.get("priority", "")
        category = self.request.GET.get("category", "")
        sort = self.request.GET.get("sort", "-created_at")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(description__icontains=q))
        if status:
            qs = qs.filter(status=status)
        if priority:
            qs = qs.filter(priority__id=priority)
        if category:
            qs = qs.filter(category__id=category)
        allowed = ["title", "-title", "deadline", "-deadline", "status", "-status", "created_at", "-created_at"]
        if sort in allowed:
            qs = qs.order_by(sort)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["current_status"] = self.request.GET.get("status", "")
        ctx["current_priority"] = self.request.GET.get("priority", "")
        ctx["current_category"] = self.request.GET.get("category", "")
        ctx["current_sort"] = self.request.GET.get("sort", "-created_at")
        ctx["priorities"] = Priority.objects.all()
        ctx["categories"] = Category.objects.all()
        ctx["status_choices"] = Task.STATUS_CHOICES
        return ctx


class TaskCreateView(CreateView):
    model = Task
    form_class = TaskForm
    template_name = "taskapp/task_form.html"
    success_url = reverse_lazy("task-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Add New Task"
        ctx["cancel_url"] = reverse_lazy("task-list")
        return ctx


class TaskUpdateView(UpdateView):
    model = Task
    form_class = TaskForm
    template_name = "taskapp/task_form.html"
    success_url = reverse_lazy("task-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = f"Edit Task: {self.object.title}"
        ctx["cancel_url"] = reverse_lazy("task-list")
        return ctx


class TaskDeleteView(DeleteView):
    model = Task
    template_name = "taskapp/task_del.html"
    success_url = reverse_lazy("task-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("task-list")
        ctx["entity_name"] = "Task"
        return ctx



class SubTaskListView(ListView):
    model = SubTask
    template_name = "taskapp/subtask_list.html"
    context_object_name = "subtasks"
    paginate_by = 10
    def get_queryset(self):
        qs = SubTask.objects.select_related("parent_task").all()
        q = self.request.GET.get("q", "").strip()
        status = self.request.GET.get("status", "")
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(parent_task__title__icontains=q))
        if status:
            qs = qs.filter(status=status)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        ctx["current_status"] = self.request.GET.get("status", "")
        ctx["status_choices"] = SubTask.STATUS_CHOICES
        return ctx

class SubTaskCreateView(CreateView):
    model = SubTask
    form_class = SubTaskForm
    template_name = "taskapp/subtask_form.html"
    success_url = reverse_lazy("subtask-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Add Sub Task"
        ctx["cancel_url"] = reverse_lazy("subtask-list")
        return ctx

class SubTaskUpdateView(UpdateView):
    model = SubTask
    form_class = SubTaskForm
    template_name = "taskapp/subtask_form.html"
    success_url = reverse_lazy("subtask-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = f"Edit Sub Task: {self.object.title}"
        ctx["cancel_url"] = reverse_lazy("subtask-list")
        return ctx

class SubTaskDeleteView(DeleteView):
    model = SubTask
    template_name = "taskapp/task_del.html"
    success_url = reverse_lazy("subtask-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("subtask-list")
        ctx["entity_name"] = "Sub Task"
        return ctx



class NoteListView(ListView):
    model = Note
    template_name = "taskapp/note_list.html"
    context_object_name = "notes"
    paginate_by = 10
    def get_queryset(self):
        qs = Note.objects.select_related("task").all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(Q(content__icontains=q) | Q(task__title__icontains=q))
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx

class NoteCreateView(CreateView):
    model = Note
    form_class = NoteForm
    template_name = "taskapp/note_form.html"
    success_url = reverse_lazy("note-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Add Note"
        ctx["cancel_url"] = reverse_lazy("note-list")
        return ctx

class NoteUpdateView(UpdateView):
    model = Note
    form_class = NoteForm
    template_name = "taskapp/note_form.html"
    success_url = reverse_lazy("note-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Edit Note"
        ctx["cancel_url"] = reverse_lazy("note-list")
        return ctx

class NoteDeleteView(DeleteView):
    model = Note
    template_name = "taskapp/task_del.html"
    success_url = reverse_lazy("note-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("note-list")
        ctx["entity_name"] = "Note"
        return ctx



class CategoryListView(ListView):
    model = Category
    template_name = "taskapp/category_list.html"
    context_object_name = "categories"
    paginate_by = 10
    def get_queryset(self):
        qs = Category.objects.annotate(task_count=Count("tasks")).all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx

class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "taskapp/category_form.html"
    success_url = reverse_lazy("category-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Add Category"
        ctx["cancel_url"] = reverse_lazy("category-list")
        return ctx

class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "taskapp/category_form.html"
    success_url = reverse_lazy("category-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = f"Edit Category: {self.object.name}"
        ctx["cancel_url"] = reverse_lazy("category-list")
        return ctx

class CategoryDeleteView(DeleteView):
    model = Category
    template_name = "taskapp/task_del.html"
    success_url = reverse_lazy("category-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("category-list")
        ctx["entity_name"] = "Category"
        return ctx



class PriorityListView(ListView):
    model = Priority
    template_name = "taskapp/priority_list.html"
    context_object_name = "priorities"
    paginate_by = 10
    def get_queryset(self):
        qs = Priority.objects.annotate(task_count=Count("tasks")).all()
        q = self.request.GET.get("q", "").strip()
        if q:
            qs = qs.filter(name__icontains=q)
        return qs
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx

class PriorityCreateView(CreateView):
    model = Priority
    form_class = PriorityForm
    template_name = "taskapp/priority_form.html"
    success_url = reverse_lazy("priority-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = "Add Priority"
        ctx["cancel_url"] = reverse_lazy("priority-list")
        return ctx

class PriorityUpdateView(UpdateView):
    model = Priority
    form_class = PriorityForm
    template_name = "taskapp/priority_form.html"
    success_url = reverse_lazy("priority-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["form_title"] = f"Edit Priority: {self.object.name}"
        ctx["cancel_url"] = reverse_lazy("priority-list")
        return ctx

class PriorityDeleteView(DeleteView):
    model = Priority
    template_name = "taskapp/task_del.html"
    success_url = reverse_lazy("priority-list")
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cancel_url"] = reverse_lazy("priority-list")
        ctx["entity_name"] = "Priority"
        return ctx