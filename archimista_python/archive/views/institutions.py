"""
Viste CRUD per Institution (Profili istituzionali).
Allineate a Ruby: institutions_controller.rb
"""

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from archimista_python.archive.models import Institution, InstitutionEditor, Term
from archimista_python.archive.forms.institution import (
    InstitutionForm, InstitutionEditorFormSet,
)


# =============================================================================
# LISTA E DETTAGLIO (sostituiscono quelle in entities.py)
# =============================================================================

class InstitutionListView(ListView):
    model = Institution
    template_name = 'archive/institution_list.html'
    context_object_name = 'institutions'
    paginate_by = 50
    ordering = ['name']


class InstitutionDetailView(DetailView):
    model = Institution
    template_name = 'archive/institution_detail.html'
    context_object_name = 'institution'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['institution_editors'] = self.object.institution_editors.all()
        return context


# =============================================================================
# CREATE
# =============================================================================

class InstitutionCreateView(View):
    template_name = 'archive/institution_form.html'

    def get(self, request):
        form = InstitutionForm()
        editor_formset = InstitutionEditorFormSet(prefix='editor')
        editing_type_terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Nuovo profilo istituzionale',
            'editing_type_terms': editing_type_terms,
        })

    def post(self, request):
        form = InstitutionForm(request.POST)
        editor_formset = InstitutionEditorFormSet(request.POST, prefix='editor')

        if form.is_valid() and editor_formset.is_valid():
            with transaction.atomic():
                institution = form.save()
                editor_formset.instance = institution
                editor_formset.save()
            messages.success(request, 'Scheda creata')
            return redirect('archive:institution_edit', pk=institution.pk)

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Nuovo profilo istituzionale',
        })


# =============================================================================
# UPDATE
# =============================================================================

class InstitutionUpdateView(View):
    template_name = 'archive/institution_form.html'

    def get(self, request, pk):
        institution = Institution.objects.get(pk=pk)
        form = InstitutionForm(instance=institution)
        editor_formset = InstitutionEditorFormSet(instance=institution, prefix='editor')
        editing_type_terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Modifica profilo istituzionale',
            'institution': institution,
            'editing_type_terms': editing_type_terms,
        })

    def post(self, request, pk):
        institution = Institution.objects.get(pk=pk)
        form = InstitutionForm(request.POST, instance=institution)
        editor_formset = InstitutionEditorFormSet(request.POST, instance=institution, prefix='editor')

        if form.is_valid() and editor_formset.is_valid():
            with transaction.atomic():
                form.save()
                editor_formset.save()
            messages.success(request, 'Scheda aggiornata')
            return redirect('archive:institution_edit', pk=institution.pk)

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Modifica profilo istituzionale',
            'institution': institution,
        })


# =============================================================================
# DELETE
# =============================================================================

class InstitutionDeleteView(DeleteView):
    model = Institution
    template_name = 'archive/institution_confirm_delete.html'
    success_url = reverse_lazy('archive:institution_list')

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Scheda eliminata')
        return super().delete(request, *args, **kwargs)
