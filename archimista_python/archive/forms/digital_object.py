from django import forms
from archimista_python.archive.models import DigitalObject


class DigitalObjectForm(forms.ModelForm):
    """Form per Oggetti Digitali — allineato a Ruby con upload file."""

    asset_file = forms.FileField(
        required=False,
        label='File',
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/jpeg,image/jpg,image/png,image/webp,application/pdf,video/mp4',
        }),
        help_text='Formati accettati: JPEG, PNG, PDF, MP4. Dimensione massima: 8 MB.',
    )

    class Meta:
        model = DigitalObject
        fields = ['title', 'description', 'position', 'published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'position': forms.NumberInput(attrs={'class': 'form-control'}),
            'published': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'title': 'Titolo',
            'description': 'Descrizione',
            'position': 'Posizione',
            'published': 'Pubblicato',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].required = False
        self.fields['published'].initial = True

    def clean_asset_file(self):
        """Valida dimensione e tipo del file (allineato a Ruby Paperclip)."""
        f = self.cleaned_data.get('asset_file')
        if f:
            # Max 8 MB (come Ruby)
            if f.size > 8 * 1024 * 1024:
                raise forms.ValidationError('Il file non può superare 8 MB.')
            # Content type validation (come Ruby)
            allowed = [
                'image/jpeg', 'image/jpg', 'image/pjpeg', 'image/png', 'image/webp', 'image/gif',
                'application/pdf',
                'video/mp4', 'application/mp4', 'video/mpeg4', 'video/webm',
            ]
            if f.content_type not in allowed:
                raise forms.ValidationError(
                    f'Tipo file non supportato ({f.content_type}). '
                    'Formati accettati: JPEG, PNG, PDF, MP4.'
                )
        return f

    def save(self, commit=True):
        """Salva il file uploadato nel campo asset."""
        instance = super().save(commit=False)
        f = self.cleaned_data.get('asset_file')
        if f and not instance.asset:
            instance.asset = f
        if commit:
            instance.save()
            # Genera thumbnail dopo il salvataggio
            if instance.asset and instance.is_image():
                instance.generate_thumbnails()
        return instance
