from django import forms

from tracker.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('description', )
