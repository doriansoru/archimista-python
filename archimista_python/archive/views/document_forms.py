"""
Viste CRUD per DocumentForm (Profili documentari).
Allineate a Ruby: document_forms_controller.rb
"""

from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from archimista_python.archive.models import DocumentForm, DocumentFormEditor, Term
from archimista_python.archive.forms.document_form import (
    DocumentFormForm, DocumentFormEditorFormSet,
)


# =============================================================================
# LISTA E DETTAGLIO
# =============================================================================

class DocumentFormListView(ListView):
    model = DocumentForm
    template_name = 'archive/document_form_list.html'
    context_object_name = 'document_forms'
    paginate_by = 50
    ordering = ['name']


class DocumentFormDetailView(DetailView):
    model = DocumentForm
    template_name = 'archive/document_form_detail.html'
    context_object_name = 'document_form'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['document_form_editors'] = self.object.document_form_editors.all()
        return context


# =============================================================================
# CREATE
# =============================================================================

class DocumentFormCreateView(View):
    template_name = 'archive/document_form_form.html'

    def get(self, request):
        form = DocumentFormForm()
        editor_formset = DocumentFormEditorFormSet(prefix='editor')
        editing_type_terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Nuovo profilo documentario',
            'editing_type_terms': editing_type_terms,
        })

    def post(self, request):
        form = DocumentFormForm(request.POST)
        editor_formset = DocumentFormEditorFormSet(request.POST, prefix='editor')

        if form.is_valid() and editor_formset.is_valid():
            with transaction.atomic():
                document_form = form.save()
                editor_formset.instance = document_form
                editor_formset.save()
            messages.success(request, 'Profilo documentario creato con successo.')
            return redirect('archive:document_form_edit', pk=document_form.pk)

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Nuovo profilo documentario',
        })


# =============================================================================
# UPDATE
# =============================================================================

class DocumentFormUpdateView(View):
    template_name = 'archive/document_form_form.html'

    def get(self, request, pk):
        document_form = DocumentForm.objects.get(pk=pk)
        form = DocumentFormForm(instance=document_form)
        editor_formset = DocumentFormEditorFormSet(instance=document_form, prefix='editor')
        editing_type_terms = Term.objects.filter(
            vocabulary__name='editors.editing_type'
        ).order_by('position')

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Modifica profilo documentario',
            'document_form': document_form,
            'editing_type_terms': editing_type_terms,
        })

    def post(self, request, pk):
        document_form = DocumentForm.objects.get(pk=pk)
        form = DocumentFormForm(request.POST, instance=document_form)
        editor_formset = DocumentFormEditorFormSet(request.POST, instance=document_form, prefix='editor')

        if form.is_valid() and editor_formset.is_valid():
            with transaction.atomic():
                form.save()
                editor_formset.save()
            messages.success(request, 'Profilo documentario aggiornato con successo.')
            return redirect('archive:document_form_edit', pk=document_form.pk)

        return render(request, self.template_name, {
            'form': form,
            'editor_formset': editor_formset,
            'action': 'Modifica profilo documentario',
            'document_form': document_form,
        })


# =============================================================================
# DELETE
# =============================================================================

class DocumentFormDeleteView(DeleteView):
    model = DocumentForm
    template_name = 'archive/document_form_confirm_delete.html'
    success_url = reverse_lazy('archive:document_form_list')
    context_object_name = 'document_form'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Profilo documentario eliminato con successo.')
        return super().delete(request, *args, **kwargs)
