from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db import transaction
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import get_object_or_404, redirect
from archimista_python.archive.models import DigitalObject, Fond, Unit, Creator, Custodian, Source
from archimista_python.archive.forms.digital_object import DigitalObjectForm

# Mappatura entità → modello
ATTACHABLE_MODELS = {
    'fond': Fond,
    'unit': Unit,
    'creator': Creator,
    'custodian': Custodian,
    'source': Source,
}

# Mappatura entità → nome URL base
ATTACHABLE_URL_NAMES = {
    'fond': 'fond_detail',
    'unit': 'unit_detail',
    'creator': 'creator_detail',
    'custodian': 'custodian_detail',
    'source': 'source_detail',
}


def resolve_attachable_from_kwargs(**kwargs):
    """Risolve l'entità padre dai parametri URL (es. fond_id, unit_id, ecc.)."""
    for key, model_class in ATTACHABLE_MODELS.items():
        pk = kwargs.get(f'{key}_id')
        if pk:
            return get_object_or_404(model_class, pk=pk), key
    return None, None


def build_attachable_context(attachable, attachable_type):
    """Costruisce il contesto per le viste nested."""
    url_name = ATTACHABLE_URL_NAMES.get(attachable_type, '')
    return {
        'attachable': attachable,
        'attachable_type': attachable_type,
        'attachable_detail_url': reverse(f'archive:{url_name}', kwargs={'pk': attachable.pk}) if url_name else '',
    }


class DigitalObjectListView(ListView):
    """Lista oggetti digitali — supporta sia contesto nested che globale."""
    model = DigitalObject
    template_name = 'archive/digital_object_list.html'
    context_object_name = 'digital_objects'
    paginate_by = 50

    def dispatch(self, request, *args, **kwargs):
        self.attachable, self.attachable_type = resolve_attachable_from_kwargs(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        qs = DigitalObject.objects.select_related('content_type').order_by('position', '-updated_at')
        if self.attachable:
            ct = ContentType.objects.get_for_model(self.attachable)
            qs = qs.filter(content_type=ct, object_id=self.attachable.pk)
        else:
            # Lista globale (come Ruby all action)
            q = self.request.GET.get('q', '').strip()
            if q:
                from django.db.models import Q
                qs = qs.filter(
                    Q(title__icontains=q) | Q(description__icontains=q) |
                    Q(asset_file_name__icontains=q)
                )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.attachable:
            context.update(build_attachable_context(self.attachable, self.attachable_type))
            context['title'] = f"Oggetti digitali — {self.attachable}"
            context['nested'] = True
        else:
            context['title'] = 'Oggetti digitali'
            context['nested'] = False
            context['q'] = self.request.GET.get('q', '')
        return context

    def get_template_names(self):
        if self.attachable:
            return ['archive/digital_object_nested_list.html']
        return ['archive/digital_object_list.html']


class DigitalObjectDetailView(DetailView):
    """Dettaglio oggetto digitale."""
    model = DigitalObject
    template_name = 'archive/digital_object_detail.html'
    context_object_name = 'digital_object'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['title'] = f"Oggetto digitale: {obj.title or obj.asset_file_name or str(obj.id)}"
        context['attachable'] = obj.attachable
        return context


class DigitalObjectCreateView(CreateView):
    """Creazione oggetto digitale — supporta contesto nested."""
    model = DigitalObject
    form_class = DigitalObjectForm
    template_name = 'archive/digital_object_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.attachable, self.attachable_type = resolve_attachable_from_kwargs(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Nuovo oggetto digitale'
        context['action'] = 'create'
        if self.attachable:
            context.update(build_attachable_context(self.attachable, self.attachable_type))
            context['nested'] = True
        else:
            context['nested'] = False
        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.created_by = 1
        form.instance.updated_by = 1
        if self.attachable:
            form.instance.content_type = ContentType.objects.get_for_model(self.attachable)
            form.instance.object_id = self.attachable.pk
        messages.success(self.request, 'Oggetto digitale creato')
        result = super().form_valid(form)
        # Genera thumbnail dopo il salvataggio
        if self.object.asset and self.object.is_image():
            self.object.generate_thumbnails()
        return result

    def get_success_url(self):
        if self.attachable:
            url_name = ATTACHABLE_URL_NAMES.get(self.attachable_type, '')
            if url_name:
                return reverse(f'archive:{self.attachable_type}_digital_object_list',
                               kwargs={f'{self.attachable_type}_id': self.attachable.pk})
        return reverse_lazy('archive:digital_object_list')

    def get_template_names(self):
        if self.attachable:
            return ['archive/digital_object_nested_form.html']
        return ['archive/digital_object_form.html']


class DigitalObjectUpdateView(UpdateView):
    """Modifica oggetto digitale — supporta contesto nested."""
    model = DigitalObject
    form_class = DigitalObjectForm
    template_name = 'archive/digital_object_form.html'

    def dispatch(self, request, *args, **kwargs):
        self.attachable, self.attachable_type = resolve_attachable_from_kwargs(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['title'] = f"Modifica oggetto digitale: {obj.title or obj.asset_file_name or str(obj.id)}"
        context['action'] = 'update'
        if self.attachable:
            context.update(build_attachable_context(self.attachable, self.attachable_type))
            context['nested'] = True
        else:
            context['nested'] = False
        return context

    @transaction.atomic
    def form_valid(self, form):
        form.instance.updated_by = 1
        messages.success(self.request, 'Oggetto digitale aggiornato')
        return super().form_valid(form)

    def get_success_url(self):
        if self.attachable:
            return reverse(f'archive:{self.attachable_type}_digital_object_list',
                           kwargs={f'{self.attachable_type}_id': self.attachable.pk})
        return reverse_lazy('archive:digital_object_list')

    def get_template_names(self):
        if self.attachable:
            return ['archive/digital_object_nested_form.html']
        return ['archive/digital_object_form.html']


class DigitalObjectDeleteView(DeleteView):
    """Eliminazione oggetto digitale — supporta contesto nested."""
    model = DigitalObject
    template_name = 'archive/digital_object_confirm_delete.html'
    context_object_name = 'digital_object'

    def dispatch(self, request, *args, **kwargs):
        self.attachable, self.attachable_type = resolve_attachable_from_kwargs(**kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        obj = self.object
        context['title'] = f"Elimina oggetto digitale: {obj.title or obj.asset_file_name or str(obj.id)}"
        if self.attachable:
            context.update(build_attachable_context(self.attachable, self.attachable_type))
            context['nested'] = True
        else:
            context['nested'] = False
        return context

    def get_success_url(self):
        if self.attachable:
            return reverse(f'archive:{self.attachable_type}_digital_object_list',
                           kwargs={f'{self.attachable_type}_id': self.attachable.pk})
        return reverse_lazy('archive:digital_object_list')

    def get_template_names(self):
        if self.attachable:
            return ['archive/digital_object_nested_confirm_delete.html']
        return ['archive/digital_object_confirm_delete.html']
