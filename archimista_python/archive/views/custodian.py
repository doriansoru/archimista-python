from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, DeleteView, View
from django.db import transaction
from django.db.models import Q
from archimista_python.archive.models import Custodian, CustodianName, Fond, Source, Term
from archimista_python.archive.forms import (
    CustodianForm, CustodianPreferredNameForm,
    CustodianNameFormSet, CustodianIdentifierFormSet, CustodianContactFormSet,
    CustodianBuildingFormSet, CustodianOwnerFormSet, CustodianUrlFormSet,
    CustodianEditorFormSet, RelCustodianSourceFormSet, RelCustodianFondFormSet,
)

# =============================================================================
# VISTE PER CUSTODIAN (ALLINEATE A RUBY)
# =============================================================================

class CustodianListView(ListView):
    model = Custodian
    template_name = 'archive/custodian_list.html'
    context_object_name = 'custodians'
    paginate_by = 20

    def get_queryset(self):
        qs = Custodian.objects.all().order_by('-updated_at')
        search_query = self.request.GET.get('q', '').strip()
        if search_query:
            # Search by preferred name or other names
            qs = qs.filter(
                Q(custodian_names__name__icontains=search_query, custodian_names__preferred=True) |
                Q(custodian_names__name__icontains=search_query)
            ).distinct()
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('q', '').strip()
        return context


class CustodianDetailView(DetailView):
    model = Custodian
    template_name = 'archive/custodian_detail.html'
    context_object_name = 'custodian'


class CustodianCreateView(View):
    template_name = 'archive/custodian_form.html'

    def get(self, request, *args, **kwargs):
        custodian_form = CustodianForm()
        preferred_name_form = CustodianPreferredNameForm()
        custodian_name_formset = CustodianNameFormSet()
        custodian_identifier_formset = CustodianIdentifierFormSet()
        custodian_contact_formset = CustodianContactFormSet()
        custodian_building_formset = CustodianBuildingFormSet()
        custodian_owner_formset = CustodianOwnerFormSet()
        custodian_url_formset = CustodianUrlFormSet()
        custodian_editor_formset = CustodianEditorFormSet()
        rel_custodian_source_formset = RelCustodianSourceFormSet(prefix='rel_custodian_sources')
        rel_custodian_fond_formset = RelCustodianFondFormSet(prefix='rel_custodian_fonds')

        # Prefill preferred name form
        preferred_name_form = CustodianPreferredNameForm(
            instance=CustodianName(preferred=True)
        )

        context = {
            'custodian_form': custodian_form,
            'preferred_name_form': preferred_name_form,
            'custodian_name_formset': custodian_name_formset,
            'custodian_identifier_formset': custodian_identifier_formset,
            'custodian_contact_formset': custodian_contact_formset,
            'custodian_building_formset': custodian_building_formset,
            'custodian_owner_formset': custodian_owner_formset,
            'custodian_url_formset': custodian_url_formset,
            'custodian_editor_formset': custodian_editor_formset,
            'rel_custodian_source_formset': rel_custodian_source_formset,
            'rel_custodian_fond_formset': rel_custodian_fond_formset,
            'fonds_list': Fond.objects.all().order_by('name'),
            'sources_list': Source.objects.all().order_by('title'),
            'terms': {
                'custodian_names_qualifier': Term.objects.filter(
                    vocabulary__name='custodian_names.qualifier'
                ).order_by('position'),
            },
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        custodian_form = CustodianForm(request.POST)
        preferred_name_form = CustodianPreferredNameForm(request.POST)
        custodian_name_formset = CustodianNameFormSet(request.POST)
        custodian_identifier_formset = CustodianIdentifierFormSet(request.POST)
        custodian_contact_formset = CustodianContactFormSet(request.POST)
        custodian_building_formset = CustodianBuildingFormSet(request.POST)
        custodian_owner_formset = CustodianOwnerFormSet(request.POST)
        custodian_url_formset = CustodianUrlFormSet(request.POST)
        custodian_editor_formset = CustodianEditorFormSet(request.POST)
        rel_custodian_source_formset = RelCustodianSourceFormSet(request.POST, prefix='rel_custodian_sources')
        rel_custodian_fond_formset = RelCustodianFondFormSet(request.POST, prefix='rel_custodian_fonds')

        if (custodian_form.is_valid() and
            preferred_name_form.is_valid() and
            custodian_name_formset.is_valid() and
            custodian_identifier_formset.is_valid() and
            custodian_contact_formset.is_valid() and
            custodian_building_formset.is_valid() and
            custodian_owner_formset.is_valid() and
            custodian_url_formset.is_valid() and
            custodian_editor_formset.is_valid() and
            rel_custodian_source_formset.is_valid() and
            rel_custodian_fond_formset.is_valid()):

            custodian = custodian_form.save()

            # Save preferred name
            pref_name = preferred_name_form.save(commit=False)
            pref_name.custodian = custodian
            pref_name.preferred = True
            pref_name.save()

            # Save formsets
            for formset in [
                custodian_name_formset,
                custodian_identifier_formset,
                custodian_contact_formset,
                custodian_building_formset,
                custodian_owner_formset,
                custodian_url_formset,
                custodian_editor_formset,
                rel_custodian_source_formset,
                rel_custodian_fond_formset,
            ]:
                formset.instance = custodian
                formset.is_valid()
                formset.save()

            return redirect('archive:custodian_detail', pk=custodian.pk)

        context = {
            'custodian_form': custodian_form,
            'preferred_name_form': preferred_name_form,
            'custodian_name_formset': custodian_name_formset,
            'custodian_identifier_formset': custodian_identifier_formset,
            'custodian_contact_formset': custodian_contact_formset,
            'custodian_building_formset': custodian_building_formset,
            'custodian_owner_formset': custodian_owner_formset,
            'custodian_url_formset': custodian_url_formset,
            'custodian_editor_formset': custodian_editor_formset,
            'rel_custodian_source_formset': rel_custodian_source_formset,
            'rel_custodian_fond_formset': rel_custodian_fond_formset,
            'fonds_list': Fond.objects.all().order_by('name'),
            'sources_list': Source.objects.all().order_by('title'),
            'terms': {
                'custodian_names_qualifier': Term.objects.filter(
                    vocabulary__name='custodian_names.qualifier'
                ).order_by('position'),
            },
        }
        return render(request, self.template_name, context)


class CustodianUpdateView(View):
    template_name = 'archive/custodian_form.html'

    def get(self, request, pk, *args, **kwargs):
        custodian = get_object_or_404(Custodian, pk=pk)

        # Get or create preferred name
        preferred_name, created = CustodianName.objects.get_or_create(
            custodian=custodian,
            preferred=True,
            defaults={'name': '', 'note': ''}
        )

        custodian_form = CustodianForm(instance=custodian)
        preferred_name_form = CustodianPreferredNameForm(instance=preferred_name)
        custodian_name_formset = CustodianNameFormSet(instance=custodian)
        custodian_identifier_formset = CustodianIdentifierFormSet(instance=custodian)
        custodian_contact_formset = CustodianContactFormSet(instance=custodian)
        custodian_building_formset = CustodianBuildingFormSet(instance=custodian)
        custodian_owner_formset = CustodianOwnerFormSet(instance=custodian)
        custodian_url_formset = CustodianUrlFormSet(instance=custodian)
        custodian_editor_formset = CustodianEditorFormSet(instance=custodian)
        rel_custodian_source_formset = RelCustodianSourceFormSet(instance=custodian, prefix='rel_custodian_sources')
        rel_custodian_fond_formset = RelCustodianFondFormSet(instance=custodian, prefix='rel_custodian_fonds')

        context = {
            'custodian_form': custodian_form,
            'preferred_name_form': preferred_name_form,
            'custodian_name_formset': custodian_name_formset,
            'custodian_identifier_formset': custodian_identifier_formset,
            'custodian_contact_formset': custodian_contact_formset,
            'custodian_building_formset': custodian_building_formset,
            'custodian_owner_formset': custodian_owner_formset,
            'custodian_url_formset': custodian_url_formset,
            'custodian_editor_formset': custodian_editor_formset,
            'rel_custodian_source_formset': rel_custodian_source_formset,
            'rel_custodian_fond_formset': rel_custodian_fond_formset,
            'fonds_list': Fond.objects.all().order_by('name'),
            'sources_list': Source.objects.all().order_by('title'),
            'custodian': custodian,
            'terms': {
                'custodian_names_qualifier': Term.objects.filter(
                    vocabulary__name='custodian_names.qualifier'
                ).order_by('position'),
            },
        }
        return render(request, self.template_name, context)

    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        custodian = get_object_or_404(Custodian, pk=pk)

        # Get or create preferred name
        preferred_name, created = CustodianName.objects.get_or_create(
            custodian=custodian,
            preferred=True,
            defaults={'name': '', 'note': ''}
        )

        custodian_form = CustodianForm(request.POST, instance=custodian)
        preferred_name_form = CustodianPreferredNameForm(request.POST, instance=preferred_name)
        custodian_name_formset = CustodianNameFormSet(request.POST, instance=custodian)
        custodian_identifier_formset = CustodianIdentifierFormSet(request.POST, instance=custodian)
        custodian_contact_formset = CustodianContactFormSet(request.POST, instance=custodian)
        custodian_building_formset = CustodianBuildingFormSet(request.POST, instance=custodian)
        custodian_owner_formset = CustodianOwnerFormSet(request.POST, instance=custodian)
        custodian_url_formset = CustodianUrlFormSet(request.POST, instance=custodian)
        custodian_editor_formset = CustodianEditorFormSet(request.POST, instance=custodian)
        rel_custodian_source_formset = RelCustodianSourceFormSet(request.POST, instance=custodian, prefix='rel_custodian_sources')
        rel_custodian_fond_formset = RelCustodianFondFormSet(request.POST, instance=custodian, prefix='rel_custodian_fonds')

        if (custodian_form.is_valid() and
            preferred_name_form.is_valid() and
            custodian_name_formset.is_valid() and
            custodian_identifier_formset.is_valid() and
            custodian_contact_formset.is_valid() and
            custodian_building_formset.is_valid() and
            custodian_owner_formset.is_valid() and
            custodian_url_formset.is_valid() and
            custodian_editor_formset.is_valid() and
            rel_custodian_source_formset.is_valid() and
            rel_custodian_fond_formset.is_valid()):

            custodian = custodian_form.save()

            # Save preferred name
            pref_name = preferred_name_form.save(commit=False)
            pref_name.custodian = custodian
            pref_name.preferred = True
            pref_name.save()

            # Save formsets
            for formset in [
                custodian_name_formset,
                custodian_identifier_formset,
                custodian_contact_formset,
                custodian_building_formset,
                custodian_owner_formset,
                custodian_url_formset,
                custodian_editor_formset,
                rel_custodian_source_formset,
                rel_custodian_fond_formset,
            ]:
                formset.is_valid()
                formset.save()

            return redirect('archive:custodian_detail', pk=custodian.pk)

        context = {
            'custodian_form': custodian_form,
            'preferred_name_form': preferred_name_form,
            'custodian_name_formset': custodian_name_formset,
            'custodian_identifier_formset': custodian_identifier_formset,
            'custodian_contact_formset': custodian_contact_formset,
            'custodian_building_formset': custodian_building_formset,
            'custodian_owner_formset': custodian_owner_formset,
            'custodian_url_formset': custodian_url_formset,
            'custodian_editor_formset': custodian_editor_formset,
            'rel_custodian_source_formset': rel_custodian_source_formset,
            'rel_custodian_fond_formset': rel_custodian_fond_formset,
            'fonds_list': Fond.objects.all().order_by('name'),
            'sources_list': Source.objects.all().order_by('title'),
            'custodian': custodian,
            'terms': {
                'custodian_names_qualifier': Term.objects.filter(
                    vocabulary__name='custodian_names.qualifier'
                ).order_by('position'),
            },
        }
        return render(request, self.template_name, context)


class CustodianDeleteView(DeleteView):
    model = Custodian
    template_name = 'archive/custodian_confirm_delete.html'
    success_url = '/archive/custodians/'
