from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, DeleteView, View
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from archimista_python.archive.models import Creator, CreatorName, Fond, Institution, Source, CreatorAssociationType, Event, Term
from archimista_python.archive.forms import (
    CreatorForm, CreatorPreferredNameForm, CreatorOtherNameFormSet,
    CreatorLegalStatusFormSet,
    CreatorUrlFormSet, CreatorIdentifierFormSet, CreatorActivityFormSet,
    CreatorEditorFormSet,
    RelCreatorCreatorFormSet, RelCreatorInstitutionFormSet,
    RelCreatorSourceFormSet, RelCreatorFondFormSet,
    EventFormSet,
)

def _get_dropdown_lists():
    """Restituisce le liste per i dropdown dei formset."""
    from archimista_python.archive.models import Term
    return {
        'fonds_list': Fond.objects.all().order_by('name'),
        'institutions_list': Institution.objects.all().order_by('name'),
        'creators_list': Creator.objects.all().order_by('history'),
        'sources_list': Source.objects.all().order_by('title'),
        'association_types_list': CreatorAssociationType.objects.all(),
        'editing_type_terms': Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position'),
        'terms': {
            'creator_names_qualifier': Term.objects.filter(
                vocabulary__name='creator_names.qualifier'
            ).order_by('position'),
        },
    }

class CreatorListView(ListView):
    model = Creator
    template_name = 'archive/creator_list.html'
    context_object_name = 'creators'
    paginate_by = 20

    def get_queryset(self):
        return Creator.objects.all().order_by('history')


class CreatorDetailView(DetailView):
    model = Creator
    template_name = 'archive/creator_detail.html'
    context_object_name = 'creator'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['events'] = Event.objects.filter(
            content_type=ContentType.objects.get_for_model(self.object),
            object_id=self.object.pk
        ).order_by('order_date')
        return context


def _get_preferred_name(creator):
    """Ottiene o crea il nome preferito per un creator."""
    if creator and creator.pk:
        pn = CreatorName.objects.filter(
            creator=creator, qualifier='A', preferred=True
        ).first()
        if pn:
            return pn
    return CreatorName(qualifier='A', preferred=True)


class CreatorCreateView(View):
    template_name = 'archive/creator_form.html'

    def get(self, request, *args, **kwargs):
        creator_form = CreatorForm()
        preferred_name_form = CreatorPreferredNameForm()
        creator_names_formset = CreatorOtherNameFormSet()
        creator_urls_formset = CreatorUrlFormSet()
        creator_identifiers_formset = CreatorIdentifierFormSet()
        creator_activities_formset = CreatorActivityFormSet()
        creator_legal_statuses_formset = CreatorLegalStatusFormSet()
        creator_editors_formset = CreatorEditorFormSet()
        rel_creator_creators_formset = RelCreatorCreatorFormSet(prefix='rel_creator_creators')
        relcreatorinstitution_set_formset = RelCreatorInstitutionFormSet(prefix='relcreatorinstitution_set')
        relcreatorsource_set_formset = RelCreatorSourceFormSet(prefix='relcreatorsource_set')
        relcreatorfond_set_formset = RelCreatorFondFormSet(prefix='relcreatorfond_set')

        # Estremi cronologici
        event_formset = EventFormSet(prefix='creator_events')

        context = {
            'creator_form': creator_form,
            'preferred_name_form': preferred_name_form,
            'creator_names_formset': creator_names_formset,
            'creator_urls_formset': creator_urls_formset,
            'creator_identifiers_formset': creator_identifiers_formset,
            'creator_activities_formset': creator_activities_formset,
            'creator_legal_statuses_formset': creator_legal_statuses_formset,
            'creator_editors_formset': creator_editors_formset,
            'rel_creator_creators_formset': rel_creator_creators_formset,
            'relcreatorinstitution_set_formset': relcreatorinstitution_set_formset,
            'relcreatorsource_set_formset': relcreatorsource_set_formset,
            'relcreatorfond_set_formset': relcreatorfond_set_formset,
            'event_formset': event_formset,
            **_get_dropdown_lists(),
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        creator_form = CreatorForm(request.POST)
        preferred_name_form = CreatorPreferredNameForm(request.POST, prefix='preferred_name')
        creator_names_formset = CreatorOtherNameFormSet(request.POST)
        creator_urls_formset = CreatorUrlFormSet(request.POST)
        creator_identifiers_formset = CreatorIdentifierFormSet(request.POST)
        creator_activities_formset = CreatorActivityFormSet(request.POST)
        creator_legal_statuses_formset = CreatorLegalStatusFormSet(request.POST)
        creator_editors_formset = CreatorEditorFormSet(request.POST)
        rel_creator_creators_formset = RelCreatorCreatorFormSet(request.POST, prefix='rel_creator_creators')
        relcreatorinstitution_set_formset = RelCreatorInstitutionFormSet(request.POST, prefix='relcreatorinstitution_set')
        relcreatorsource_set_formset = RelCreatorSourceFormSet(request.POST, prefix='relcreatorsource_set')
        relcreatorfond_set_formset = RelCreatorFondFormSet(request.POST, prefix='relcreatorfond_set')

        # Estremi cronologici
        event_formset = EventFormSet(request.POST, prefix='creator_events')

        if creator_form.is_valid() and all([
            preferred_name_form.is_valid(),
            creator_names_formset.is_valid(),
            creator_urls_formset.is_valid(),
            creator_identifiers_formset.is_valid(),
            creator_activities_formset.is_valid(),
            creator_legal_statuses_formset.is_valid(),
            creator_editors_formset.is_valid(),
            rel_creator_creators_formset.is_valid(),
            relcreatorinstitution_set_formset.is_valid(),
            relcreatorsource_set_formset.is_valid(),
            relcreatorfond_set_formset.is_valid(),
        ]):
            creator = creator_form.save()

            # Salva nome preferito
            pn = preferred_name_form.save(commit=False)
            pn.creator = creator
            pn.qualifier = 'A'
            pn.preferred = True
            pn.save()

            # Salva formset
            for fs in [creator_names_formset, creator_urls_formset,
                       creator_identifiers_formset, creator_activities_formset,
                       creator_legal_statuses_formset,
                       creator_editors_formset, rel_creator_creators_formset,
                       relcreatorinstitution_set_formset, relcreatorsource_set_formset,
                       relcreatorfond_set_formset]:
                fs.instance = creator
                if fs.is_valid():
                    fs.save(commit=False)
                    for form in fs.forms:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                            if any(v for k, v in form.cleaned_data.items() if k not in ('id', 'DELETE') and v):
                                form.save()
                        elif form.cleaned_data and form.cleaned_data.get('DELETE', False) and form.instance.pk:
                            form.instance.delete()

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
                        content_type=ContentType.objects.get_for_model(Creator),
                        object_id=creator.pk
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

            return redirect('archive:creator_detail', pk=creator.pk)

        context = {
            'creator_form': creator_form,
            'preferred_name_form': preferred_name_form,
            'creator_names_formset': creator_names_formset,
            'creator_urls_formset': creator_urls_formset,
            'creator_identifiers_formset': creator_identifiers_formset,
            'creator_activities_formset': creator_activities_formset,
            'creator_legal_statuses_formset': creator_legal_statuses_formset,
            'creator_editors_formset': creator_editors_formset,
            'rel_creator_creators_formset': rel_creator_creators_formset,
            'relcreatorinstitution_set_formset': relcreatorinstitution_set_formset,
            'relcreatorsource_set_formset': relcreatorsource_set_formset,
            'relcreatorfond_set_formset': relcreatorfond_set_formset,
            'event_formset': event_formset,
            **_get_dropdown_lists(),
        }
        return render(request, self.template_name, context)


class CreatorUpdateView(View):
    template_name = 'archive/creator_form.html'

    def get(self, request, pk, *args, **kwargs):
        creator = get_object_or_404(Creator, pk=pk)
        creator_form = CreatorForm(instance=creator)
        preferred_name = _get_preferred_name(creator)
        preferred_name_form = CreatorPreferredNameForm(instance=preferred_name)
        creator_names_formset = CreatorOtherNameFormSet(instance=creator)
        creator_urls_formset = CreatorUrlFormSet(instance=creator)
        creator_identifiers_formset = CreatorIdentifierFormSet(instance=creator)
        creator_activities_formset = CreatorActivityFormSet(instance=creator)
        creator_legal_statuses_formset = CreatorLegalStatusFormSet(instance=creator)
        creator_editors_formset = CreatorEditorFormSet(instance=creator)
        rel_creator_creators_formset = RelCreatorCreatorFormSet(instance=creator, prefix='rel_creator_creators')
        relcreatorinstitution_set_formset = RelCreatorInstitutionFormSet(instance=creator, prefix='relcreatorinstitution_set')
        relcreatorsource_set_formset = RelCreatorSourceFormSet(instance=creator, prefix='relcreatorsource_set')
        relcreatorfond_set_formset = RelCreatorFondFormSet(instance=creator, prefix='relcreatorfond_set')

        # Estremi cronologici
        event_formset = EventFormSet(instance=creator, prefix='creator_events')

        context = {
            'creator_form': creator_form,
            'preferred_name_form': preferred_name_form,
            'creator_names_formset': creator_names_formset,
            'creator_urls_formset': creator_urls_formset,
            'creator_identifiers_formset': creator_identifiers_formset,
            'creator_activities_formset': creator_activities_formset,
            'creator_legal_statuses_formset': creator_legal_statuses_formset,
            'creator_editors_formset': creator_editors_formset,
            'rel_creator_creators_formset': rel_creator_creators_formset,
            'relcreatorinstitution_set_formset': relcreatorinstitution_set_formset,
            'relcreatorsource_set_formset': relcreatorsource_set_formset,
            'relcreatorfond_set_formset': relcreatorfond_set_formset,
            'event_formset': event_formset,
            'creator': creator,
            **_get_dropdown_lists(),
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        creator = get_object_or_404(Creator, pk=pk)
        creator_form = CreatorForm(request.POST, instance=creator)
        preferred_name = _get_preferred_name(creator)
        preferred_name_form = CreatorPreferredNameForm(request.POST, instance=preferred_name, prefix='preferred_name')
        creator_names_formset = CreatorOtherNameFormSet(request.POST, instance=creator)
        creator_urls_formset = CreatorUrlFormSet(request.POST, instance=creator)
        creator_identifiers_formset = CreatorIdentifierFormSet(request.POST, instance=creator)
        creator_activities_formset = CreatorActivityFormSet(request.POST, instance=creator)
        creator_legal_statuses_formset = CreatorLegalStatusFormSet(request.POST, instance=creator)
        creator_editors_formset = CreatorEditorFormSet(request.POST, instance=creator)
        rel_creator_creators_formset = RelCreatorCreatorFormSet(request.POST, instance=creator, prefix='rel_creator_creators')
        relcreatorinstitution_set_formset = RelCreatorInstitutionFormSet(request.POST, instance=creator, prefix='relcreatorinstitution_set')
        relcreatorsource_set_formset = RelCreatorSourceFormSet(request.POST, instance=creator, prefix='relcreatorsource_set')
        relcreatorfond_set_formset = RelCreatorFondFormSet(request.POST, instance=creator, prefix='relcreatorfond_set')

        # Estremi cronologici
        event_formset = EventFormSet(request.POST, instance=creator, prefix='creator_events')

        if creator_form.is_valid() and all([
            preferred_name_form.is_valid(),
            creator_names_formset.is_valid(),
            creator_urls_formset.is_valid(),
            creator_identifiers_formset.is_valid(),
            creator_activities_formset.is_valid(),
            creator_legal_statuses_formset.is_valid(),
            creator_editors_formset.is_valid(),
            rel_creator_creators_formset.is_valid(),
            relcreatorinstitution_set_formset.is_valid(),
            relcreatorsource_set_formset.is_valid(),
            relcreatorfond_set_formset.is_valid(),
        ]):
            creator = creator_form.save()

            # Salva nome preferito
            pn = preferred_name_form.save(commit=False)
            pn.creator = creator
            pn.qualifier = 'A'
            pn.preferred = True
            pn.save()

            # Salva formset
            for fs in [creator_names_formset, creator_urls_formset,
                       creator_identifiers_formset, creator_activities_formset,
                       creator_legal_statuses_formset,
                       creator_editors_formset, rel_creator_creators_formset,
                       relcreatorinstitution_set_formset, relcreatorsource_set_formset,
                       relcreatorfond_set_formset]:
                if fs.is_valid():
                    fs.save(commit=False)
                    for form in fs.forms:
                        if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                            if any(v for k, v in form.cleaned_data.items() if k not in ('id', 'DELETE') and v):
                                form.save()
                        elif form.cleaned_data and form.cleaned_data.get('DELETE', False) and form.instance.pk:
                            form.instance.delete()

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
                        content_type=ContentType.objects.get_for_model(Creator),
                        object_id=creator.pk
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

            return redirect('archive:creator_detail', pk=creator.pk)

        context = {
            'creator_form': creator_form,
            'preferred_name_form': preferred_name_form,
            'creator_names_formset': creator_names_formset,
            'creator_urls_formset': creator_urls_formset,
            'creator_identifiers_formset': creator_identifiers_formset,
            'creator_activities_formset': creator_activities_formset,
            'creator_legal_statuses_formset': creator_legal_statuses_formset,
            'creator_editors_formset': creator_editors_formset,
            'rel_creator_creators_formset': rel_creator_creators_formset,
            'relcreatorinstitution_set_formset': relcreatorinstitution_set_formset,
            'relcreatorsource_set_formset': relcreatorsource_set_formset,
            'relcreatorfond_set_formset': relcreatorfond_set_formset,
            'event_formset': event_formset,
            'creator': creator,
            **_get_dropdown_lists(),
        }
        return render(request, self.template_name, context)


class CreatorDeleteView(DeleteView):
    model = Creator
    template_name = 'archive/creator_confirm_delete.html'
    success_url = reverse_lazy('archive:creator_list')
