from django import forms
from django.core.exceptions import ValidationError

from tracker.models import Task


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ('description', 'jira_id')

    def clean(self):
        description = self.cleaned_data['description']
        if description.find('[') != -1 or description.find(']') != -1:
            raise ValidationError('В заголовке не должно быть jira_id')
