from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db import transaction
from archimista_python.archive.models import Editor
from archimista_python.archive.forms.editor import EditorForm


class EditorListView(ListView):
    """Lista compilatori — allineata a Ruby."""
    model = Editor
    template_name = 'archive/editor_list.html'
    context_object_name = 'editors'
    paginate_by = 50

    def get_queryset(self):
        return Editor.objects.order_by('last_name', 'first_name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Compilatori'
        return context


class EditorDetailView(DetailView):
    """Dettaglio compilatore — allineato a Ruby."""
    model = Editor
    template_name = 'archive/editor_detail.html'
    context_object_name = 'editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Dettaglio compilatore: {self.object}"
        return context


class EditorCreateView(CreateView):
    """Creazione compilatore — allineata a Ruby."""
    model = Editor
    form_class = EditorForm
    template_name = 'archive/editor_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuovo compilatore'
        context['action'] = 'create'
        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.created_by = 1
        form.instance.updated_by = 1
        messages.success(self.request, 'Scheda creata')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('archive:editor_list')


class EditorUpdateView(UpdateView):
    """Modifica compilatore — allineata a Ruby."""
    model = Editor
    form_class = EditorForm
    template_name = 'archive/editor_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Modifica compilatore: {self.object}"
        context['action'] = 'update'
        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.updated_by = 1
        messages.success(self.request, 'Scheda aggiornata')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('archive:editor_list')


class EditorDeleteView(DeleteView):
    """Eliminazione compilatore — allineata a Ruby."""
    model = Editor
    template_name = 'archive/editor_confirm_delete.html'
    context_object_name = 'editor'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = f"Elimina compilatore: {self.object}"
        return context

    def get_success_url(self):
        return reverse_lazy('archive:editor_list')
