from django import forms
from django.contrib.contenttypes.forms import generic_inlineformset_factory
from archimista_python.archive.models import Event

# =============================================================================
# FORM PER ESTREMI CRONOLOGICI (EVENT / ARCHIDATE)
# Allineato a Ruby: 2 radio (data puntuale / data secolare), combo specifiche diverse
# =============================================================================

class EventForm(forms.ModelForm):
    """Form per estremi cronologici (Archidate) — allineato a Ruby."""

    # Start date fields (separati come in Ruby: year, month, day)
    start_date_from_year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'size': '7', 'placeholder': 'Anno'})
    )
    start_date_from_month = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(i, str(i)) for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_date_from_day = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(i, str(i)) for i in range(1, 32)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Century fields (per data secolare)
    start_century = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(str(i), f'sec. {["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"][i-1]}') for i in range(1, 22)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    start_century_interval = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'parte...'),
            ('beginning', 'inizio'), ('end', 'fine'), ('middle', 'metà'),
            ('first_half', 'prima metà'), ('second_half', 'seconda metà'),
            ('first_quarter', 'primo quarto'), ('second_quarter', 'secondo quarto'),
            ('third_quarter', 'terzo quarto'), ('last_quarter', 'ultimo quarto'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # End date fields
    end_date_from_year = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'size': '7', 'placeholder': 'Anno'})
    )
    end_date_from_month = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(i, str(i)) for i in range(1, 13)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    end_date_from_day = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(i, str(i)) for i in range(1, 32)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    # Century fields (per data secolare)
    end_century = forms.ChoiceField(
        required=False,
        choices=[('', '---')] + [(str(i), f'sec. {["I","II","III","IV","V","VI","VII","VIII","IX","X","XI","XII","XIII","XIV","XV","XVI","XVII","XVIII","XIX","XX","XXI"][i-1]}') for i in range(1, 22)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    end_century_interval = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'parte...'),
            ('beginning', 'inizio'), ('end', 'fine'), ('middle', 'metà'),
            ('first_half', 'prima metà'), ('second_half', 'seconda metà'),
            ('first_quarter', 'primo quarto'), ('second_quarter', 'secondo quarto'),
            ('third_quarter', 'terzo quarto'), ('last_quarter', 'ultimo quarto'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Event
        fields = [
            'preferred', 'is_valid', 'event_type',
            'start_date_spec', 'start_date_valid', 'start_date_format', 'start_date_place',
            'end_date_spec', 'end_date_valid', 'end_date_format', 'end_date_place',
            'note',
        ]
        widgets = {
            'preferred': forms.CheckboxInput(attrs={'class': 'form-check-input preferred-event'}),
            'is_valid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'event_type': forms.TextInput(attrs={'class': 'form-control'}),
            'start_date_spec': forms.Select(attrs={'class': 'form-select archidate-field'}),
            'start_date_valid': forms.Select(attrs={'class': 'form-select archidate-field'}),
            'start_date_format': forms.RadioSelect(attrs={'class': 'format-toggler start'}),
            'start_date_place': forms.TextInput(attrs={'class': 'form-control'}),
            'end_date_spec': forms.Select(attrs={'class': 'form-select archidate-field'}),
            'end_date_valid': forms.Select(attrs={'class': 'form-select archidate-field'}),
            'end_date_format': forms.RadioSelect(attrs={'class': 'format-toggler end'}),
            'end_date_place': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.TextInput(attrs={'class': 'form-control'}),
        }

    # Sovrascrivo i campi CharField come ChoiceField per far funzionare RadioSelect
    start_date_format = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'format-toggler start'}),
    )
    end_date_format = forms.ChoiceField(
        required=False,
        widget=forms.RadioSelect(attrs={'class': 'format-toggler end'}),
    )
    start_date_spec = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select archidate-field'}),
    )
    end_date_spec = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select archidate-field'}),
    )
    start_date_valid = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select archidate-field'}),
    )
    end_date_valid = forms.ChoiceField(
        required=False,
        widget=forms.Select(attrs={'class': 'form-select archidate-field'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # FORMAT RADIO: solo 2 opzioni come Ruby (data puntuale, data secolare)
        self.fields['start_date_format'].choices = [
            ('Y', 'data puntuale'), ('C', 'data secolare'),
        ]
        self.fields['end_date_format'].choices = [
            ('Y', 'data puntuale'), ('C', 'data secolare'),
        ]

        # START DATE SPEC: combo con = ante circa (come Ruby)
        self.fields['start_date_spec'].choices = [
            ('', '---'), ('idem', '='), ('ante', 'ante'), ('circa', 'circa'),
        ]

        # END DATE SPEC: combo con ante = circa (come Ruby)
        self.fields['end_date_spec'].choices = [
            ('', '---'), ('ante', 'ante'), ('idem', '='), ('circa', 'circa'),
        ]

        # START/END DATE VALID: combo con certa, incerta, attribuita, incerta e attribuita
        self.fields['start_date_valid'].choices = [
            ('', '---'), ('C', 'certa'), ('U', 'incerta'), ('Q', 'attribuita'), ('UQ', 'incerta e attribuita'),
        ]
        self.fields['end_date_valid'].choices = [
            ('', '---'), ('C', 'certa'), ('U', 'incerta'), ('Q', 'attribuita'), ('UQ', 'incerta e attribuita'),
        ]

        # Imposta default SOLO per eventi esistenti (non per il form vuoto extra)
        is_existing = self.instance and self.instance.pk
        if is_existing:
            if not self.instance.start_date_spec:
                self.fields['start_date_spec'].initial = 'idem'
            if not self.instance.start_date_valid:
                self.fields['start_date_valid'].initial = 'C'
            if not self.instance.start_date_format:
                self.fields['start_date_format'].initial = 'Y'
            if not self.instance.end_date_spec:
                self.fields['end_date_spec'].initial = 'idem'
            if not self.instance.end_date_valid:
                self.fields['end_date_valid'].initial = 'C'
            if not self.instance.end_date_format:
                self.fields['end_date_format'].initial = 'O'
        # Per il form vuoto extra: nessun default, campi vuoti

        # Popola i campi year/month/day da start_date_from se esiste
        if self.instance and self.instance.pk and self.instance.start_date_from:
            self.fields['start_date_from_year'].initial = self.instance.start_date_from.year
            # Mostra mese/giorno solo se il formato non è 'Y' (anno solo)
            fmt = self.instance.start_date_format
            if fmt != 'Y':
                self.fields['start_date_from_month'].initial = self.instance.start_date_from.month
                if fmt == 'YMD':
                    self.fields['start_date_from_day'].initial = self.instance.start_date_from.day

        # Popola i campi year/month/day da end_date_from se esiste
        if self.instance and self.instance.pk and self.instance.end_date_from:
            self.fields['end_date_from_year'].initial = self.instance.end_date_from.year
            fmt = self.instance.end_date_format
            if fmt != 'Y':
                self.fields['end_date_from_month'].initial = self.instance.end_date_from.month
                if fmt == 'YMD':
                    self.fields['end_date_from_day'].initial = self.instance.end_date_from.day

        # Equal bounds checkbox
        self.fields['equal_bounds'] = forms.BooleanField(
            required=False,
            widget=forms.CheckboxInput(attrs={'class': 'form-check-input equal-bounds-command'}),
            label="Uguale all'estremo iniziale"
        )
        if is_existing and self.instance.start_date_from and self.instance.end_date_from:
            if self.instance.start_date_from == self.instance.end_date_from:
                self.fields['equal_bounds'].initial = True

    def save(self, commit=True):
        """Costruisce le date da year/month/day e salva."""
        instance = super().save(commit=False)

        # Costruisci start_date_from
        year = self.cleaned_data.get('start_date_from_year', '').strip()
        month = self.cleaned_data.get('start_date_from_month', '')
        day = self.cleaned_data.get('start_date_from_day', '')
        if year:
            from datetime import date
            try:
                instance.start_date_from = date(int(year), int(month or 1), int(day or 1))
                instance.start_date_to = date(int(year), int(month or 12), int(day or 31))
            except (ValueError, TypeError):
                pass

        # Costruisci end_date_from (se equal_bounds, copia da start)
        if self.cleaned_data.get('equal_bounds'):
            instance.end_date_from = instance.start_date_from
            instance.end_date_to = instance.start_date_to
        else:
            year = self.cleaned_data.get('end_date_from_year', '').strip()
            month = self.cleaned_data.get('end_date_from_month', '')
            day = self.cleaned_data.get('end_date_from_day', '')
            if year:
                from datetime import date
                try:
                    instance.end_date_from = date(int(year), int(month or 1), int(day or 1))
                    instance.end_date_to = date(int(year), int(month or 12), int(day or 31))
                except (ValueError, TypeError):
                    pass

        # Imposta order_date per ordinamento (come Ruby)
        if instance.start_date_from:
            instance.order_date = instance.start_date_from.isoformat()

        # Imposta display dates
        if instance.start_date_from:
            instance.start_date_display = instance.start_date_from.strftime('%Y-%m-%d')
        if instance.end_date_from:
            instance.end_date_display = instance.end_date_from.strftime('%Y-%m-%d')

        if commit:
            instance.save()
        return instance


# Formset generico per Event (usa GenericInlineFormSet)
# extra=0: mostra solo gli eventi esistenti, come Ruby (nessun form vuoto extra)
EventFormSet = generic_inlineformset_factory(
    Event,
    form=EventForm,
    extra=0,
    can_delete=True,
    ct_field='content_type',
    fk_field='object_id',
)
