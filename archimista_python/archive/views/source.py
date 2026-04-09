from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction, models
from django.contrib import messages
import json

from archimista_python.archive.models import Source, SourceType, SourceUrl
from archimista_python.archive.forms.source import (
    SourceForm, SourceUrlFormSet,
)


class SourceListView(ListView):
    model = Source
    template_name = 'archive/source_list.html'
    context_object_name = 'sources'
    paginate_by = 50
    ordering = ['short_title']

    def get_queryset(self):
        queryset = super().get_queryset()
        q = self.request.GET.get('q', '').strip()
        if q:
            queryset = queryset.filter(
                models.Q(short_title__icontains=q) |
                models.Q(title__icontains=q) |
                models.Q(author__icontains=q)
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['q'] = self.request.GET.get('q', '')
        return context


class SourceDetailView(View):
    """Detail view per Source — mostra TUTTI i campi del form Ruby."""

    def get(self, request, pk):
        source = Source.objects.get(pk=pk)
        source_urls = source.source_urls.all()
        rel_fonds = source.rel_fond_sources.select_related('fond').all()
        rel_creators = source.rel_creator_sources.select_related('creator').all()
        rel_custodians = source.rel_custodian_sources.select_related('custodian').all()

        return render(request, 'archive/source_detail.html', {
            'source': source,
            'source_urls': source_urls,
            'rel_fonds': rel_fonds,
            'rel_creators': rel_creators,
            'rel_custodians': rel_custodians,
        })


class SourceCreateView(View):
    template_name = 'archive/source_form.html'

    def get(self, request):
        type_code = request.GET.get('type', 1)
        form = SourceForm(
            initial={'source_type_code': type_code},
            source_types=_get_source_types(),
            source_subtypes=_get_source_subtypes(int(type_code)),
        )
        url_formset = SourceUrlFormSet(prefix='url')

        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'action': 'Nuova fonte',
            'source_type_code': int(type_code),
            'source_subtypes_json': json.dumps(_get_all_subtypes()),
        })

    def post(self, request):
        type_code = request.POST.get('source_type_code', 1)
        form = SourceForm(
            request.POST,
            source_types=_get_source_types(),
            source_subtypes=_get_source_subtypes(int(type_code)),
        )
        url_formset = SourceUrlFormSet(request.POST, prefix='url')

        if form.is_valid() and url_formset.is_valid():
            with transaction.atomic():
                source = form.save()
                url_formset.instance = source
                url_formset.save()
            messages.success(request, 'Scheda creata')
            return redirect('archive:source_edit', pk=source.pk)

        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'action': 'Nuova fonte',
            'source_type_code': int(type_code),
            'source_subtypes_json': json.dumps(_get_all_subtypes()),
        })


class SourceUpdateView(View):
    template_name = 'archive/source_form.html'

    def get(self, request, pk):
        source = Source.objects.get(pk=pk)
        type_code = source.source_type_code or 1
        form = SourceForm(
            instance=source,
            source_types=_get_source_types(),
            source_subtypes=_get_source_subtypes(int(type_code)),
        )
        url_formset = SourceUrlFormSet(instance=source, prefix='url')

        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'action': 'Modifica fonte',
            'source': source,
            'source_type_code': int(type_code),
            'source_subtypes_json': json.dumps(_get_all_subtypes()),
        })

    def post(self, request, pk):
        source = Source.objects.get(pk=pk)
        type_code = request.POST.get('source_type_code', source.source_type_code or 1)
        form = SourceForm(
            request.POST, instance=source,
            source_types=_get_source_types(),
            source_subtypes=_get_source_subtypes(int(type_code)),
        )
        url_formset = SourceUrlFormSet(request.POST, instance=source, prefix='url')

        if form.is_valid() and url_formset.is_valid():
            with transaction.atomic():
                form.save()
                url_formset.save()
            messages.success(request, 'Scheda aggiornata')
            return redirect('archive:source_edit', pk=source.pk)

        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'action': 'Modifica fonte',
            'source': source,
            'source_type_code': int(type_code),
            'source_subtypes_json': json.dumps(_get_all_subtypes()),
        })


class SourceDeleteView(DeleteView):
    model = Source
    template_name = 'archive/source_confirm_delete.html'
    success_url = reverse_lazy('archive:source_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Scheda eliminata')
        return super().delete(request, *args, **kwargs)


# --- Helper ---

def _get_source_types():
    """Restituisce le tipologie root (come SourceType.roots in Ruby)."""
    return list(SourceType.objects.filter(parent_code__isnull=True).order_by('position'))


def _get_source_subtypes(parent_code):
    """Restituisce le sottotipologie per un tipo (come SourceType.subtypes_of in Ruby)."""
    return list(SourceType.objects.filter(parent_code=parent_code).order_by('position'))


def _get_all_subtypes():
    """Restituisce TUTTE le sottotipologie come dict {parent_code: [(code, name), ...]}."""
    all_subtypes = SourceType.objects.filter(parent_code__isnull=False).order_by('position')
    result = {}
    for st in all_subtypes:
        result.setdefault(st.parent_code, []).append((st.code, st.source_type))
    return result
