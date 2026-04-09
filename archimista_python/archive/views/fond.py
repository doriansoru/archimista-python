from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from archimista_python.archive.models import Fond, Term, Event
from archimista_python.archive.forms import (
    FondForm,
    FondNameFormSet, FondIdentifierFormSet, FondLangFormSet, FondOwnerFormSet,
    FondUrlFormSet, FondEditorFormSet,
    RelFondHeadingFormSet, RelFondSourceFormSet, RelFondDocumentFormFormSet,
    EventFormSet,
)

class FondListView(ListView):
    model = Fond
    template_name = 'archive/fond_list.html'
    context_object_name = 'fonds'
    
    def get_queryset(self):
        # Mostra solo i fondi radice (senza parent/ancestry)
        return Fond.objects.filter(ancestry__isnull=True).order_by('position')

class FondDetailView(DetailView):
    model = Fond
    template_name = 'archive/fond_detail.html'
    context_object_name = 'fond'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self.object),
            object_id=self.object.pk
        ).order_by('order_date')
        return context

class FondCreateView(CreateView):
    model = Fond
    form_class = FondForm
    template_name = 'archive/fond_form.html'
    success_url = reverse_lazy('archive:fond_list')

    def get_initial(self):
        """Se ?parent_id=X è nell'URL, pre-compila il fondo padre."""
        initial = super().get_initial()
        parent_id = self.request.GET.get('parent_id')
        if parent_id:
            initial['parent'] = parent_id
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Aggiungi le scelte dai vocabolari per i campi standardizzati
        context['fond_type_choices'] = Term.objects.filter(
            vocabulary__name='fonds.fond_type'
        ).order_by('position')
        context['access_condition_choices'] = Term.objects.filter(
            vocabulary__name='fonds.access_condition'
        ).order_by('position')
        context['use_condition_choices'] = Term.objects.filter(
            vocabulary__name='fonds.use_condition'
        ).order_by('position')
        context['preservation_choices'] = Term.objects.filter(
            vocabulary__name='fonds.preservation'
        ).order_by('position')
        context['description_type_choices'] = Term.objects.filter(
            vocabulary__name='fonds.description_type'
        ).order_by('position')
        return context

class FondUpdateView(View):
    """Vista per modificare fondi con tutte le estensioni"""
    template_name = 'archive/fond_form.html'

    def get(self, request, pk, *args, **kwargs):
        fond = get_object_or_404(Fond, pk=pk)
        fond_form = FondForm(instance=fond)

        # Formset per estensioni Fond
        fond_name_formset = FondNameFormSet(instance=fond)
        fond_identifier_formset = FondIdentifierFormSet(instance=fond)
        fond_lang_formset = FondLangFormSet(instance=fond)
        fond_owner_formset = FondOwnerFormSet(instance=fond)
        fond_url_formset = FondUrlFormSet(instance=fond)
        fond_editor_formset = FondEditorFormSet(instance=fond)
        rel_fond_heading_formset = RelFondHeadingFormSet(instance=fond, prefix='rel_fond_heading')
        rel_fond_source_formset = RelFondSourceFormSet(instance=fond, prefix='rel_fond_source')
        rel_fond_document_formset = RelFondDocumentFormFormSet(instance=fond, prefix='rel_fond_document')

        # Estremi cronologici
        event_formset = EventFormSet(instance=fond, prefix='fond_events')

        context = {
            'fond_form': fond_form,
            'fond_name_formset': fond_name_formset,
            'fond_identifier_formset': fond_identifier_formset,
            'fond_lang_formset': fond_lang_formset,
            'fond_owner_formset': fond_owner_formset,
            'fond_url_formset': fond_url_formset,
            'fond_editor_formset': fond_editor_formset,
            'rel_fond_heading_formset': rel_fond_heading_formset,
            'rel_fond_source_formset': rel_fond_source_formset,
            'rel_fond_document_formset': rel_fond_document_formset,
            'event_formset': event_formset,
            'fond': fond,
            # Scelte dai vocabolari per i campi standardizzati
            'fond_type_choices': Term.objects.filter(vocabulary__name='fonds.fond_type').order_by('position'),
            'access_condition_choices': Term.objects.filter(vocabulary__name='fonds.access_condition').order_by('position'),
            'use_condition_choices': Term.objects.filter(vocabulary__name='fonds.use_condition').order_by('position'),
            'preservation_choices': Term.objects.filter(vocabulary__name='fonds.preservation').order_by('position'),
            'description_type_choices': Term.objects.filter(vocabulary__name='fonds.description_type').order_by('position'),
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        fond = get_object_or_404(Fond, pk=pk)
        fond_form = FondForm(request.POST, instance=fond)

        # Formset per estensioni Fond
        fond_name_formset = FondNameFormSet(request.POST, instance=fond)
        fond_identifier_formset = FondIdentifierFormSet(request.POST, instance=fond)
        fond_lang_formset = FondLangFormSet(request.POST, instance=fond)
        fond_owner_formset = FondOwnerFormSet(request.POST, instance=fond)
        fond_url_formset = FondUrlFormSet(request.POST, instance=fond)
        fond_editor_formset = FondEditorFormSet(request.POST, instance=fond)
        rel_fond_heading_formset = RelFondHeadingFormSet(request.POST, instance=fond, prefix='rel_fond_heading')
        rel_fond_source_formset = RelFondSourceFormSet(request.POST, instance=fond, prefix='rel_fond_source')
        rel_fond_document_formset = RelFondDocumentFormFormSet(request.POST, instance=fond, prefix='rel_fond_document')

        # Estremi cronologici
        event_formset = EventFormSet(request.POST, instance=fond, prefix='fond_events')

        if fond_form.is_valid():
            fond = fond_form.save()

            # Salva tutti i formset (prima is_valid, poi save)
            fond_name_formset.is_valid()
            fond_name_formset.save()
            fond_identifier_formset.is_valid()
            fond_identifier_formset.save()
            fond_lang_formset.is_valid()
            fond_lang_formset.save()
            fond_owner_formset.is_valid()
            fond_owner_formset.save()
            fond_url_formset.is_valid()
            fond_url_formset.save()
            fond_editor_formset.is_valid()
            fond_editor_formset.save()
            rel_fond_heading_formset.is_valid()
            rel_fond_heading_formset.save()
            rel_fond_source_formset.is_valid()
            rel_fond_source_formset.save()
            rel_fond_document_formset.is_valid()
            rel_fond_document_formset.save()

            # Salva estremi cronologici (Event)
            event_formset.is_valid()
            for form in event_formset.forms:
                if not form.cleaned_data:
                    continue
                if form.cleaned_data.get('DELETE', False):
                    if form.instance.pk:
                        form.instance.delete()
                    continue

                has_data = any(form.cleaned_data.get(f) for f in [
                    'start_date_from_year', 'start_date_from_month', 'start_date_from_day',
                    'end_date_from_year', 'end_date_from_month', 'end_date_from_day',
                    'start_date_spec', 'end_date_spec', 'start_date_place', 'end_date_place', 'note'
                ])
                if not has_data and not form.instance.pk:
                    continue

                if form.instance.pk:
                    event = form.instance
                else:
                    event = Event(
                        content_type=ContentType.objects.get_for_model(Fond),
                        object_id=fond.pk
                    )

                for field_name in ['preferred', 'is_valid', 'event_type',
                                   'start_date_spec', 'start_date_valid', 'start_date_format', 'start_date_place',
                                   'end_date_spec', 'end_date_valid', 'end_date_format', 'end_date_place', 'note']:
                    if field_name in form.cleaned_data:
                        setattr(event, field_name, form.cleaned_data[field_name])

                year = form.cleaned_data.get('start_date_from_year', '').strip() if form.cleaned_data.get('start_date_from_year') else ''
                month = form.cleaned_data.get('start_date_from_month', '')
                day = form.cleaned_data.get('start_date_from_day', '')
                if year:
                    from datetime import date
                    try:
                        event.start_date_from = date(int(year), int(month or 1), int(day or 1))
                        event.start_date_to = date(int(year), int(month or 12), int(day or 31))
                        event.start_date_display = event.start_date_from.strftime('%Y-%m-%d')
                    except (ValueError, TypeError):
                        pass

                if not form.cleaned_data.get('equal_bounds'):
                    year = form.cleaned_data.get('end_date_from_year', '').strip() if form.cleaned_data.get('end_date_from_year') else ''
                    month = form.cleaned_data.get('end_date_from_month', '')
                    day = form.cleaned_data.get('end_date_from_day', '')
                    if year:
                        from datetime import date
                        try:
                            event.end_date_from = date(int(year), int(month or 1), int(day or 1))
                            event.end_date_to = date(int(year), int(month or 12), int(day or 31))
                            event.end_date_display = event.end_date_from.strftime('%Y-%m-%d')
                        except (ValueError, TypeError):
                            pass
                else:
                    event.end_date_from = event.start_date_from
                    event.end_date_to = event.start_date_to
                    event.end_date_display = event.start_date_display

                if event.start_date_from:
                    event.order_date = event.start_date_from.isoformat()

                event.save()

            return redirect('archive:fond_detail', pk=fond.pk)

        # Se ci sono errori, ripresenta il form
        context = {
            'fond_form': fond_form,
            'fond_name_formset': fond_name_formset,
            'fond_identifier_formset': fond_identifier_formset,
            'fond_lang_formset': fond_lang_formset,
            'fond_owner_formset': fond_owner_formset,
            'fond_url_formset': fond_url_formset,
            'fond_editor_formset': fond_editor_formset,
            'rel_fond_heading_formset': rel_fond_heading_formset,
            'rel_fond_source_formset': rel_fond_source_formset,
            'rel_fond_document_formset': rel_fond_document_formset,
            'event_formset': event_formset,
            'fond': fond,
            # Scelte dai vocabolari per i campi standardizzati
            'fond_type_choices': Term.objects.filter(vocabulary__name='fonds.fond_type').order_by('position'),
            'access_condition_choices': Term.objects.filter(vocabulary__name='fonds.access_condition').order_by('position'),
            'use_condition_choices': Term.objects.filter(vocabulary__name='fonds.use_condition').order_by('position'),
            'preservation_choices': Term.objects.filter(vocabulary__name='fonds.preservation').order_by('position'),
            'description_type_choices': Term.objects.filter(vocabulary__name='fonds.description_type').order_by('position'),
        }
        return render(request, self.template_name, context)

class FondDeleteView(DeleteView):
    model = Fond
    template_name = 'archive/fond_confirm_delete.html'
    success_url = reverse_lazy('archive:fond_list')

