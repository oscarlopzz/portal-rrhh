from django import forms
from .models import Evaluation

class EvaluationCreateForm(forms.ModelForm):
    class Meta:
        model = Evaluation
        fields = ['employee', 'period_start', 'period_end', 'score', 'comments', 'status']
        widgets = {
            'period_start': forms.DateInput(attrs={'type': 'date'}),
            'period_end': forms.DateInput(attrs={'type': 'date'}),
        }

class EvaluationReviewForm(forms.ModelForm):
    decision = forms.ChoiceField(choices=[('COMPLETED', 'Completar')], initial='COMPLETED')

    class Meta:
        model = Evaluation
        fields = ['score', 'comments']

    def save(self, *, reviewer, instance: Evaluation, commit=True):
        instance.score = self.cleaned_data['score']
        instance.comments = self.cleaned_data.get('comments', instance.comments)
        instance.status = 'COMPLETED'
        instance.reviewer = reviewer
        from django.utils import timezone
        instance.reviewed_at = timezone.now()
        if commit:
            instance.save()
        return instance
