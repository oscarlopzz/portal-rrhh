from django import forms
from .models import Justification

ALLOWED_CONTENT_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_FILE_MB = 5

class JustificationCreateForm(forms.ModelForm):
    class Meta:
        model = Justification
        fields = ['jtype', 'issue_date', 'description', 'document', 'leave']
        widgets = {
            'issue_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_document(self):
        f = self.cleaned_data.get('document')
        if not f:
            raise forms.ValidationError("Sube un archivo (PDF/JPG/PNG).")
        if f.content_type not in ALLOWED_CONTENT_TYPES:
            raise forms.ValidationError("Formato no permitido. Usa PDF, JPG o PNG.")
        if f.size > MAX_FILE_MB * 1024 * 1024:
            raise forms.ValidationError(f"Archivo demasiado grande (máx. {MAX_FILE_MB} MB).")
        return f

class JustificationReviewForm(forms.ModelForm):
    decision = forms.ChoiceField(choices=[('APPROVED','Aprobar'), ('REJECTED','Rechazar')])

    class Meta:
        model = Justification
        fields = ['decision']

    def save(self, reviewer, instance):
        instance.reviewer = reviewer
        instance.status = self.cleaned_data['decision']
        instance.save()
        return instance
