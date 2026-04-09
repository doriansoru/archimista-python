"""
Viste per entità di servizio: Source, Institution, DocumentForm, Project, Editor,
DigitalObject, Heading, Anagraphic.
Tutte hanno CRUD base con ListView + DetailView.
"""

from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.shortcuts import redirect
from archimista_python.archive.models import (
    Source, Institution, DocumentForm, Project, Editor,
    DigitalObject, Heading, Anagraphic,
)
from archimista_python.archive.forms import HeadingForm, AnagraphicForm, AnagIdentifierFormSet


# =============================================================================
# FONTI (Source)
# =============================================================================
class SourceListView(ListView):
    model = Source
    template_name = 'archive/source_list.html'
    context_object_name = 'sources'
    paginate_by = 50


class SourceDetailView(DetailView):
    model = Source
    template_name = 'archive/source_detail.html'
    context_object_name = 'source'


# =============================================================================
# ISTITUZIONI (Institution)
# =============================================================================
class InstitutionListView(ListView):
    model = Institution
    template_name = 'archive/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 50


class InstitutionDetailView(DetailView):
    model = Institution
    template_name = 'archive/institution_detail.html'
    context_object_name = 'institution'


# =============================================================================
# PROFILI DOCUMENTARI (DocumentForm) — Spostati in views/document_forms.py
# =============================================================================
# =============================================================================
# VOCI DI INDICE (Heading)
# =============================================================================
class HeadingListView(ListView):
    model = Heading
    template_name = 'archive/heading_list.html'
    context_object_name = 'headings'
    paginate_by = 50


class HeadingDetailView(DetailView):
    model = Heading
    template_name = 'archive/heading_detail.html'
    context_object_name = 'heading'


class HeadingCreateView(CreateView):
    model = Heading
    form_class = HeadingForm
    template_name = 'archive/heading_form.html'
    success_url = reverse_lazy('archive:heading_list')

    def form_valid(self, form):
        messages.success(self.request, 'Voce di indice creata con successo.')
        return super().form_valid(form)


class HeadingUpdateView(UpdateView):
    model = Heading
    form_class = HeadingForm
    template_name = 'archive/heading_form.html'
    success_url = reverse_lazy('archive:heading_list')

    def form_valid(self, form):
        messages.success(self.request, 'Voce di indice aggiornata con successo.')
        return super().form_valid(form)


class HeadingDeleteView(DeleteView):
    model = Heading
    template_name = 'archive/heading_confirm_delete.html'
    success_url = reverse_lazy('archive:heading_list')
    context_object_name = 'heading'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Voce di indice eliminata con successo.')
        return super().delete(request, *args, **kwargs)


# =============================================================================
# ANAGRAFICHE (Anagraphic)
# =============================================================================
class AnagraphicListView(ListView):
    model = Anagraphic
    template_name = 'archive/anagraphic_list.html'
    context_object_name = 'anagraphics'
    paginate_by = 50


class AnagraphicDetailView(DetailView):
    model = Anagraphic
    template_name = 'archive/anagraphic_detail.html'
    context_object_name = 'anagraphic'


class AnagraphicCreateView(CreateView):
    model = Anagraphic
    form_class = AnagraphicForm
    template_name = 'archive/anagraphic_form.html'
    success_url = reverse_lazy('archive:anagraphic_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['identifier_formset'] = AnagIdentifierFormSet(self.request.POST, instance=self.object)
        else:
            context['identifier_formset'] = AnagIdentifierFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        identifier_formset = context['identifier_formset']
        # Salva prima l'oggetto principale, poi il formset
        self.object = form.save()
        identifier_formset.instance = self.object
        if identifier_formset.is_valid():
            identifier_formset.save()
        messages.success(self.request, 'Scheda anagrafica creata con successo.')
        return super().form_valid(form)


class AnagraphicUpdateView(UpdateView):
    model = Anagraphic
    form_class = AnagraphicForm
    template_name = 'archive/anagraphic_form.html'
    success_url = reverse_lazy('archive:anagraphic_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.POST:
            context['identifier_formset'] = AnagIdentifierFormSet(self.request.POST, instance=self.object)
        else:
            context['identifier_formset'] = AnagIdentifierFormSet(instance=self.object)
        return context

    def form_valid(self, form):
        context = self.get_context_data()
        identifier_formset = context['identifier_formset']
        if identifier_formset.is_valid():
            self.object = form.save()
            identifier_formset.instance = self.object
            identifier_formset.save()
            messages.success(self.request, 'Scheda anagrafica aggiornata con successo.')
            return super().form_valid(form)
        else:
            return self.render_to_response(self.get_context_data(form=form))


class AnagraphicDeleteView(DeleteView):
    model = Anagraphic
    template_name = 'archive/anagraphic_confirm_delete.html'
    success_url = reverse_lazy('archive:anagraphic_list')
    context_object_name = 'anagraphic'

    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Scheda anagrafica eliminata con successo.')
        return super().delete(request, *args, **kwargs)
