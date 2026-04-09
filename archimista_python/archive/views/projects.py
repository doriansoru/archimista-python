from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.views.generic import ListView, DetailView, DeleteView
from django.urls import reverse_lazy
from django.db import transaction
from django.contrib import messages

from archimista_python.archive.models import Project
from archimista_python.archive.forms.project import (
    ProjectForm, ProjectUrlFormSet, ProjectManagerFormSet, 
    ProjectStakeholderFormSet, RelProjectFondFormSet
)

class ProjectListView(ListView):
    model = Project
    template_name = 'archive/project_list.html'
    context_object_name = 'projects'
    paginate_by = 50
    ordering = ['name']

class ProjectDetailView(DetailView):
    model = Project
    template_name = 'archive/project_detail.html'
    context_object_name = 'project'

class ProjectCreateView(View):
    template_name = 'archive/project_form.html'

    def get(self, request):
        form = ProjectForm()
        url_formset = ProjectUrlFormSet(prefix='url')
        manager_formset = ProjectManagerFormSet(prefix='manager')
        stakeholder_formset = ProjectStakeholderFormSet(prefix='stakeholder')
        fond_formset = RelProjectFondFormSet(prefix='fond')
        
        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'manager_formset': manager_formset,
            'stakeholder_formset': stakeholder_formset,
            'fond_formset': fond_formset,
            'action': 'Nuovo progetto'
        })

    def post(self, request):
        form = ProjectForm(request.POST)
        url_formset = ProjectUrlFormSet(request.POST, prefix='url')
        manager_formset = ProjectManagerFormSet(request.POST, prefix='manager')
        stakeholder_formset = ProjectStakeholderFormSet(request.POST, prefix='stakeholder')
        fond_formset = RelProjectFondFormSet(request.POST, prefix='fond')

        if form.is_valid() and url_formset.is_valid() and manager_formset.is_valid() and stakeholder_formset.is_valid() and fond_formset.is_valid():
            with transaction.atomic():
                project = form.save()
                url_formset.instance = project
                url_formset.save()
                manager_formset.instance = project
                manager_formset.save()
                stakeholder_formset.instance = project
                stakeholder_formset.save()
                fond_formset.instance = project
                fond_formset.save()
                
            messages.success(request, 'Progetto creato con successo.')
            return redirect('archive:project_detail', pk=project.pk)
            
        return render(request, self.template_name, {
            'form': form,
            'url_formset': url_formset,
            'manager_formset': manager_formset,
            'stakeholder_formset': stakeholder_formset,
            'fond_formset': fond_formset,
            'action': 'Nuovo progetto'
        })

class ProjectUpdateView(View):
    template_name = 'archive/project_form.html'

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(instance=project)
        url_formset = ProjectUrlFormSet(instance=project, prefix='url')
        manager_formset = ProjectManagerFormSet(instance=project, prefix='manager')
        stakeholder_formset = ProjectStakeholderFormSet(instance=project, prefix='stakeholder')
        fond_formset = RelProjectFondFormSet(instance=project, prefix='fond')
        
        return render(request, self.template_name, {
            'form': form,
            'project': project,
            'url_formset': url_formset,
            'manager_formset': manager_formset,
            'stakeholder_formset': stakeholder_formset,
            'fond_formset': fond_formset,
            'action': 'Modifica progetto'
        })

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ProjectForm(request.POST, instance=project)
        url_formset = ProjectUrlFormSet(request.POST, instance=project, prefix='url')
        manager_formset = ProjectManagerFormSet(request.POST, instance=project, prefix='manager')
        stakeholder_formset = ProjectStakeholderFormSet(request.POST, instance=project, prefix='stakeholder')
        fond_formset = RelProjectFondFormSet(request.POST, instance=project, prefix='fond')

        if form.is_valid() and url_formset.is_valid() and manager_formset.is_valid() and stakeholder_formset.is_valid() and fond_formset.is_valid():
            with transaction.atomic():
                project = form.save()
                url_formset.save()
                manager_formset.save()
                stakeholder_formset.save()
                fond_formset.save()
                
            messages.success(request, 'Progetto aggiornato con successo.')
            return redirect('archive:project_detail', pk=project.pk)
            
        return render(request, self.template_name, {
            'form': form,
            'project': project,
            'url_formset': url_formset,
            'manager_formset': manager_formset,
            'stakeholder_formset': stakeholder_formset,
            'fond_formset': fond_formset,
            'action': 'Modifica progetto'
        })

class ProjectDeleteView(DeleteView):
    model = Project
    template_name = 'archive/project_confirm_delete.html'
    success_url = reverse_lazy('archive:project_list')
    
    def delete(self, request, *args, **kwargs):
        messages.success(self.request, 'Progetto eliminato con successo.')
        return super().delete(request, *args, **kwargs)
