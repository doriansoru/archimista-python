#!/usr/bin/env python
"""
Script per popolare i vocabolari controllati di Archimista.
Questo script inserisce i termini standardizzati nei vocabolari
per standardizzare l'inserimento dati.

Utilizzo:
    python seed_vocabularies.py
"""

import os
import django

# Configura Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()

from archimista_python.archive.models import Vocabulary, Term

def create_vocabulary(name, description=None):
    """Crea o recupera un vocabolario."""
    vocab, created = Vocabulary.objects.get_or_create(
        name=name,
        defaults={'description': description} if description else {}
    )
    if created:
        print(f"✓ Creato vocabolario: {name}")
    else:
        print(f"  Vocabolario esistente: {name}")
    return vocab

def create_term(vocab, term_key, term_value, position=1):
    """Crea un termine in un vocabolario."""
    term, created = Term.objects.update_or_create(
        vocabulary=vocab,
        term_key=term_key,
        defaults={
            'term': term_value,
            'term_value': term_value,
            'position': position
        }
    )
    if created:
        print(f"    ✓ Aggiunto termine: {term_key} = {term_value}")
    return term

def sync_terms(vocab, terms_list):
    """Sincronizza i termini di un vocabolario: aggiunge/aggiorna quelli in lista e rimuove gli altri."""
    print(f"  Sincronizzazione termini per: {vocab.name}")
    
    # 1. Identifica le chiavi e i valori validi
    valid_keys = [t[0] for t in terms_list]
    valid_values = [t[1] for t in terms_list]
    
    # 2. Rimuovi termini non più validi
    deleted_count = Term.objects.filter(vocabulary=vocab).exclude(term_key__in=valid_keys).delete()[0]
    if deleted_count > 0:
        print(f"    × Rimossi {deleted_count} termini obsoleti")
    
    # 3. Aggiorna o crea i termini validi
    for i, (key, value) in enumerate(terms_list, 1):
        term, created = Term.objects.update_or_create(
            vocabulary=vocab,
            term_key=key,
            defaults={
                'term': value,
                'term_value': value,
                'position': i
            }
        )
        if created:
            print(f"    ✓ Creato: {key} = {value}")
        # else:
        #    print(f"    ~ Aggiornato: {key} = {value}")

def seed_vocabularies():
    print("=" * 60)
    print("POPOLAMENTO VOCABOLARI ARCHIMISTA")
    print("=" * 60)
    
    # =============================================================================
    # VOCABOLARI PER FOND
    # =============================================================================
    print("\n--- VOCABOLARI PER FONDI ---")
    
    # fonds.fond_type - Tipologia del fondo
    vocab_fond_type = create_vocabulary("fonds.fond_type", "Tipologia del fondo archivistico")
    fond_types = [
        ("fonds.fond_type.collection", "Collezione"),
        ("fonds.fond_type.fonds", "Fondo"),
        ("fonds.fond_type.fonds_group", "Gruppo di fondi"),
        ("fonds.fond_type.subfonds", "Subfondo"),
        ("fonds.fond_type.series", "Serie"),
        ("fonds.fond_type.subseries", "Sottoserie"),
        ("fonds.fond_type.file", "Fascicolo"),
        ("fonds.fond_type.subfile", "Sottofascicolo"),
        ("fonds.fond_type.item", "Unità"),
        ("fonds.fond_type.section", "Sezione"),
        ("fonds.fond_type.other", "Altro"),
    ]
    for i, (key, value) in enumerate(fond_types, 1):
        create_term(vocab_fond_type, key, value, i)
    
    # fonds.access_condition - Condizione di accesso (da Ruby - vocabulary_id: 17)
    vocab_access = create_vocabulary("fonds.access_condition", "Condizione di accesso al fondo")
    access_conditions = [
        ("fonds.access_condition.liberamente_accessibile", "liberamente accessibile"),
        ("fonds.access_condition.accessibile_previa_autorizzazione", "accessibile previa autorizzazione"),
        ("fonds.access_condition.non_consultabile", "non consultabile"),
        ("fonds.access_condition.parzialmente_accessibile", "parzialmente accessibile"),
    ]
    for i, (key, value) in enumerate(access_conditions, 1):
        create_term(vocab_access, key, value, i)

    # fonds.use_condition - Condizione d'uso (da Ruby - vocabulary_id: 18)
    vocab_use = create_vocabulary("fonds.use_condition", "Condizione d'uso del fondo")
    use_conditions = [
        ("fonds.use_condition.libera", "libera"),
        ("fonds.use_condition.consentita_per_uso_studio", "consentita per uso studio"),
        ("fonds.use_condition.a_pagamento", "a pagamento"),
        ("fonds.use_condition.negata", "negata"),
    ]
    for i, (key, value) in enumerate(use_conditions, 1):
        create_term(vocab_use, key, value, i)
    
    # fonds.preservation - Stato di conservazione (da Ruby - vocabulary_id: 10)
    vocab_preservation = create_vocabulary("fonds.preservation", "Stato di conservazione fondo")
    preservation_states = [
        ("fonds.preservation.excellent", "ottimo"),
        ("fonds.preservation.good", "buono"),
        ("fonds.preservation.discreet", "discreto"),
        ("fonds.preservation.mediocre", "mediocre"),
        ("fonds.preservation.bad", "cattivo"),
        ("fonds.preservation.very_bad", "pessimo"),
    ]
    for i, (key, value) in enumerate(preservation_states, 1):
        create_term(vocab_preservation, key, value, i)
    
    # fonds.description_type - Tipo di descrizione
    vocab_desc_type = create_vocabulary("fonds.description_type", "Tipo di descrizione archivistica")
    description_types = [
        ("fonds.description_type.analytic", "Analitica"),
        ("fonds.description_type.summary", "Sintetica"),
        ("fonds.description_type.intermediate", "Intermedia"),
        ("fonds.description_type.detailed", "Dettagliata"),
    ]
    for i, (key, value) in enumerate(description_types, 1):
        create_term(vocab_desc_type, key, value, i)
    
    # =============================================================================
    # VOCABOLARI PER UNIT
    # =============================================================================
    print("\n--- VOCABOLARI PER UNITÀ ---")
    
    # units.unit_type - Tipo di unità archivistica (da Ruby - vocabulary_id: 13)
    vocab_unit_type = create_vocabulary("units.unit_type", "Tipo di unità archivistica")
    unit_types = [
        ("units.unit_type.list", "registro o altra unità rilegata"),
        ("units.unit_type.file", "fascicolo o altra unità complessa"),
        ("units.unit_type.item", "unità documentaria"),
    ]
    for i, (key, value) in enumerate(unit_types, 1):
        create_term(vocab_unit_type, key, value, i)
    
    # units.access_condition - Condizione di accesso (da Ruby - vocabulary_id: 19)
    vocab_unit_access = create_vocabulary("units.access_condition", "Condizione di accesso all'unità")
    for i, (key, value) in enumerate(access_conditions, 1):
        create_term(vocab_unit_access, key.replace('fonds.', 'units.'), value, i)

    # units.use_condition - Condizione d'uso (da Ruby - vocabulary_id: 20)
    vocab_unit_use = create_vocabulary("units.use_condition", "Condizione d'uso dell'unità")
    for i, (key, value) in enumerate(use_conditions, 1):
        create_term(vocab_unit_use, key.replace('fonds.', 'units.'), value, i)
    
    # units.preservation - Stato di conservazione (da Ruby - vocabulary_id: 12)
    vocab_unit_preservation = create_vocabulary("units.preservation", "Stato di conservazione unità")
    preservation_states_unit = [
        ("units.preservation.excellent", "ottimo"),
        ("units.preservation.good", "buono"),
        ("units.preservation.discreet", "discreto"),
        ("units.preservation.mediocre", "mediocre"),
        ("units.preservation.bad", "cattivo"),
        ("units.preservation.very_bad", "pessimo"),
    ]
    for i, (key, value) in enumerate(preservation_states_unit, 1):
        create_term(vocab_unit_preservation, key, value, i)

    # units.physical_type - Tipo fisico dell'unità (da Ruby - vocabulary_id: 22)
    vocab_physical_type = create_vocabulary("units.physical_type", "Tipo fisico dell'unità archivistica")
    physical_types = [
        ("units.physical_type.album", "album"),
        ("units.physical_type.busta", "busta"),
        ("units.physical_type.cartella", "cartella"),
        ("units.physical_type.faldone", "faldone"),
        ("units.physical_type.fascicolo", "fascicolo"),
        ("units.physical_type.filza", "filza"),
        ("units.physical_type.foglio", "foglio"),
        ("units.physical_type.manifesto", "manifesto"),
        ("units.physical_type.mappa", "mappa"),
        ("units.physical_type.mazzo", "mazzo"),
        ("units.physical_type.opuscolo", "opuscolo"),
        ("units.physical_type.pacco", "pacco"),
        ("units.physical_type.plico", "plico"),
        ("units.physical_type.quaderno", "quaderno"),
        ("units.physical_type.registro", "registro"),
        ("units.physical_type.rivista", "rivista"),
        ("units.physical_type.rotolo", "rotolo"),
        ("units.physical_type.scatola", "scatola"),
        ("units.physical_type.scheda", "scheda"),
        ("units.physical_type.taccuino", "taccuino"),
        ("units.physical_type.volume", "volume"),
    ]
    for i, (key, value) in enumerate(physical_types, 1):
        create_term(vocab_physical_type, key, value, i)

    # units.medium - Supporto (da Ruby - vocabulary_id: 23)
    vocab_medium = create_vocabulary("units.medium", "Supporto materiale")
    medium_types = [
        ("units.medium.paper", "carta"),
        ("units.medium.parchment", "pergamena"),
        ("units.medium.linen_paper", "carta telata"),
        ("units.medium.cardboard", "cartoncino"),
        ("units.medium.film", "pellicola"),
        ("units.medium.other", "altro"),
    ]
    for i, (key, value) in enumerate(medium_types, 1):
        create_term(vocab_medium, key, value, i)

    # units.level_type - Tipo di livello
    vocab_level_type = create_vocabulary("units.level_type", "Tipo di livello archivistico")
    level_types = [
        ("units.level_type.collection", "Collezione"),
        ("units.level_type.fonds", "Fondo"),
        ("units.level_type.series", "Serie"),
        ("units.level_type.subseries", "Sottoserie"),
        ("units.level_type.file", "Fascicolo"),
        ("units.level_type.item", "Unità"),
    ]
    for i, (key, value) in enumerate(level_types, 1):
        create_term(vocab_level_type, key, value, i)

    # unit_damages.code - Tipi di danno (da Ruby Archimista - vocabulary_id: 14)
    vocab_damages = create_vocabulary("unit_damages.code", "Tipologia danni")
    damages = [
        ("unit_damages.code.humidity", "danni da umidità"),
        ("unit_damages.code.flood", "danni da alluvione"),
        ("unit_damages.code.rodents", "danni da roditori"),
        ("unit_damages.code.insects", "danni da insetti"),
        ("unit_damages.code.fire", "danni da incendio"),
        ("unit_damages.code.laceration", "lacerazione"),
        ("unit_damages.code.stain", "macchia"),
        ("unit_damages.code.mutilation", "mutilazione"),
        ("unit_damages.code.perforation", "perforazione"),
        ("unit_damages.code.folds", "piegature"),
        ("unit_damages.code.discoloration", "scoloritura"),
        ("unit_damages.code.crease", "sgualcitura"),
        ("unit_damages.code.fragile", "fragilità del supporto"),
        ("unit_damages.code.funghi_e_batteri", "funghi e batteri"),
        ("unit_damages.code.strappi", "strappi"),
        ("unit_damages.code.fogli_staccati", "fogli staccati"),
        ("unit_damages.code.ingiallimento", "ingiallimento della carta"),
        ("unit_damages.code.lacune", "lacune"),
        ("unit_damages.code.sbiadimento", "sbiadimento"),
        ("unit_damages.code.dispersione", "dispersione"),
        ("unit_damages.code.acidita", "acidità"),
        ("unit_damages.code.usura", "usura"),
        ("unit_damages.code.rottura_cuciture", "rottura delle cuciture"),
    ]
    for i, (key, value) in enumerate(damages, 1):
        create_term(vocab_damages, key, value, i)

    # =============================================================================
    # VOCABOLARI PER CREATOR
    # =============================================================================
    print("\n--- VOCABOLARI PER CREATORE ---")

    # creator.creator_type - Tipo di creatore
    vocab_creator_type = create_vocabulary("creators.creator_type", "Tipo di creatore")
    creator_types = [
        ("creators.creator_type.person", "Persona"),
        ("creators.creator_type.family", "Famiglia"),
        ("creators.creator_type.organization", "Ente/Organizzazione"),
    ]
    for i, (key, value) in enumerate(creator_types, 1):
        create_term(vocab_creator_type, key, value, i)

    # creator_names.qualifier - Qualificatore nomi creatore
    vocab_creator_qualifier = create_vocabulary("creator_names.qualifier", "Qualificatore per nomi di creatore")
    creator_qualifiers = [
        ("creator_names.qualifier.birth_name", "Nome di nascita"),
        ("creator_names.qualifier.pseudonym", "Pseudonimo"),
        ("creator_names.qualifier.variant", "Variante"),
        ("creator_names.qualifier.alternative", "Alternativo"),
    ]
    for i, (key, value) in enumerate(creator_qualifiers, 1):
        create_term(vocab_creator_qualifier, key, value, i)

    # creator_legal_statuses.legal_status - Stato giuridico
    vocab_legal_status = create_vocabulary("creator_legal_statuses.legal_status", "Stato giuridico del creatore")
    legal_statuses = [
        ("creator_legal_statuses.legal_status.public", "Pubblico"),
        ("creator_legal_statuses.legal_status.private", "Privato"),
        ("creator_legal_statuses.legal_status.mixed", "Misto"),
    ]
    for i, (key, value) in enumerate(legal_statuses, 1):
        create_term(vocab_legal_status, key, value, i)

    # =============================================================================
    # VOCABOLARI PER CUSTODIAN
    # =============================================================================
    print("\n--- VOCABOLARI PER CUSTODE ---")

    # custodians.custodian_type - Tipo di custode
    vocab_custodian_type = create_vocabulary("custodians.custodian_type", "Tipo di custode")
    custodian_types = [
        ("custodians.custodian_type.archive", "Archivio"),
        ("custodians.custodian_type.library", "Biblioteca"),
        ("custodians.custodian_type.museum", "Museo"),
        ("custodians.custodian_type.institution", "Istituzione"),
        ("custodians.custodian_type.private", "Privato"),
        ("custodians.custodian_type.other", "Altro"),
    ]
    for i, (key, value) in enumerate(custodian_types, 1):
        create_term(vocab_custodian_type, key, value, i)

    # custodians.legal_status - Stato giuridico custode
    vocab_custodian_legal = create_vocabulary("custodians.legal_status", "Stato giuridico del custode")
    custodian_legal = [
        ("custodians.legal_status.public", "Pubblico"),
        ("custodians.legal_status.private", "Privato"),
    ]
    for i, (key, value) in enumerate(custodian_legal, 1):
        create_term(vocab_custodian_legal, key, value, i)

    # custodian_names.qualifier - Qualificatore nomi custode
    vocab_custodian_qualifier = create_vocabulary("custodian_names.qualifier", "Qualificatore per nomi di custode")
    custodian_qualifiers = [
        ("custodian_names.qualifier.official", "Ufficiale"),
        ("custodian_names.qualifier.variant", "Variante"),
        ("custodian_names.qualifier.alternative", "Alternativo"),
    ]
    for i, (key, value) in enumerate(custodian_qualifiers, 1):
        create_term(vocab_custodian_qualifier, key, value, i)

    # custodian_buildings.custodian_building_type - Tipo edificio
    vocab_custodian_building = create_vocabulary("custodian_buildings.custodian_building_type", "Tipo di edificio del custode")
    custodian_buildings = [
        ("custodian_buildings.custodian_building_type.main", "Edificio principale"),
        ("custodian_buildings.custodian_building_type.annex", "Annesso"),
        ("custodian_buildings.custodian_building_type.depot", "Deposito"),
        ("custodian_buildings.custodian_building_type.other", "Altro"),
    ]
    for i, (key, value) in enumerate(custodian_buildings, 1):
        create_term(vocab_custodian_building, key, value, i)

    # custodian_contacts.contact_type - Tipo contatto
    vocab_contact_type = create_vocabulary("custodian_contacts.contact_type", "Tipo di contatto")
    contact_types = [
        ("custodian_contacts.contact_type.phone", "Telefono"),
        ("custodian_contacts.contact_type.fax", "Fax"),
        ("custodian_contacts.contact_type.email", "Email"),
        ("custodian_contacts.contact_type.website", "Sito web"),
        ("custodian_contacts.contact_type.address", "Indirizzo"),
    ]
    for i, (key, value) in enumerate(contact_types, 1):
        create_term(vocab_contact_type, key, value, i)

    # =============================================================================
    # ALTRI VOCABOLARI
    # =============================================================================
    print("\n--- ALTRI VOCABOLARI ---")

    # projects.project_type - Tipologia d'intervento
    vocab_project_type = create_vocabulary("projects.project_type", "Tipologia d'intervento")
    project_types = [
        ("censimento", "Censimento/guida"),
        ("riordino", "Riordino e inventariazione"),
        ("recupero", "Recupero e rielaborazione di corredo pregresso"),
        ("elenchi", "Elenchi"),
    ]
    sync_terms(vocab_project_type, project_types)

    # projects.status - Status progetto
    vocab_project_status = create_vocabulary("projects.status", "Status del progetto")
    project_statuses = [
        ("in_corso", "In corso"),
        ("concluso", "Concluso/consegnato"),
        ("revisione", "Revisione"),
        ("pubblicato", "Pubblicato/da pubblicare"),
    ]
    sync_terms(vocab_project_status, project_statuses)

    # project_managers.qualifier - Qualificatore responsabile progetto
    vocab_pm_qualifier = create_vocabulary("project_managers.qualifier", "Qualificatore responsabile progetto")
    pm_qualifiers = [
        ("responsabile_scientifico", "Responsabile scientifico"),
        ("responsabile_operativo", "Responsabile operativo"),
        ("schedatore", "Schedatore"),
        ("coordinatore", "Coordinatore"),
    ]
    sync_terms(vocab_pm_qualifier, pm_qualifiers)

    # project_stakeholders.qualifier - Qualificatore stakeholder
    vocab_stakeholder = create_vocabulary("project_stakeholders.qualifier", "Qualificatore stakeholder")
    stakeholder_types = [
        ("finanziamento", "Finanziamento"),
        ("realizzazione", "Realizzazione"),
        ("promozione", "Promozione"),
        ("coordinamento_operativo", "Coordinamento operativo"),
    ]
    sync_terms(vocab_stakeholder, stakeholder_types)

    # headings.heading_type - Tipo di voce di indice (allineato a Ruby - vocabulary_id: 24)
    vocab_heading_type = create_vocabulary("headings.heading_type", "Tipo di voce di indice")
    heading_types = [
        ("headings.heading_type.corporate_body", "Ente"),
        ("headings.heading_type.person", "Persona"),
        ("headings.heading_type.family", "Famiglia"),
        ("headings.heading_type.geographic", "Toponimo"),
        ("headings.heading_type.other", "Altro"),
    ]
    for i, (key, value) in enumerate(heading_types, 1):
        create_term(vocab_heading_type, key, value, i)

    # editors.editing_type - Tipo di compilazione (da Ruby - vocabulary_id: 25)
    vocab_editing_type = create_vocabulary("editors.editing_type", "Tipo di compilazione")
    editing_types = [
        ("editors.editing_type.aggiornamento_scheda", "aggiornamento scheda"),
        ("editors.editing_type.inserimento_dati", "inserimento dati"),
        ("editors.editing_type.integrazione_successiva", "integrazione successiva"),
        ("editors.editing_type.prima_redazione", "prima redazione"),
        ("editors.editing_type.revisione", "revisione"),
        ("editors.editing_type.rielaborazione", "rielaborazione"),
        ("editors.editing_type.schedatura", "schedatura"),
    ]
    for i, (key, value) in enumerate(editing_types, 1):
        create_term(vocab_editing_type, key, value, i)

    # digital_objects.digital_object_type - Tipo oggetto digitale
    vocab_do_type = create_vocabulary("digital_objects.digital_object_type", "Tipo di oggetto digitale")
    do_types = [
        ("digital_objects.digital_object_type.image", "Immagine"),
        ("digital_objects.digital_object_type.text", "Testo"),
        ("digital_objects.digital_object_type.audio", "Audio"),
        ("digital_objects.digital_object_type.video", "Video"),
        ("digital_objects.digital_object_type.dataset", "Dataset"),
        ("digital_objects.digital_object_type.other", "Altro"),
    ]
    for i, (key, value) in enumerate(do_types, 1):
        create_term(vocab_do_type, key, value, i)

    # units.file_type - Tipo file (per FSC)
    vocab_file_type = create_vocabulary("units.file_type", "Tipo file")
    file_types = [
        ("units.file_type.personal", "Personale"),
        ("units.file_type.family", "Famiglia"),
        ("units.file_type.corporate", "Aziendale"),
    ]
    for i, (key, value) in enumerate(file_types, 1):
        create_term(vocab_file_type, key, value, i)

    # anagraphics.anagraphic_type - Tipo anagrafica
    vocab_anagraphic_type = create_vocabulary("anagraphics.anagraphic_type", "Tipo anagrafica")
    anagraphic_types = [
        ("anagraphics.anagraphic_type.person", "Persona"),
        ("anagraphics.anagraphic_type.family", "Famiglia"),
    ]
    for i, (key, value) in enumerate(anagraphic_types, 1):
        create_term(vocab_anagraphic_type, key, value, i)

    # fe_operas.status - Stato opera FE
    vocab_fe_status = create_vocabulary("fe_operas.status", "Stato opera edilizia")
    fe_statuses = [
        ("fe_operas.status.new", "Nuovo"),
        ("fe_operas.status.existing", "Esistente"),
        ("fe_operas.status.demolished", "Demolito"),
    ]
    for i, (key, value) in enumerate(fe_statuses, 1):
        create_term(vocab_fe_status, key, value, i)
    
    # =============================================================================
    # RIEPILOGO
    # =============================================================================
    print("\n" + "=" * 60)
    print("RIEPILOGO")
    print("=" * 60)
    vocab_count = Vocabulary.objects.count()
    term_count = Term.objects.count()
    print(f"Vocabolari creati: {vocab_count}")
    print(f"Termini creati: {term_count}")
    print("\nI vocabolari sono ora disponibili nei form di:")
    print("  - Fondi (fond_type, access_condition, use_condition, preservation, description_type)")
    print("  - Unità (unit_type, unit_type_term, access_condition, use_condition, preservation, physical_type, medium)")
    print("  - Danni unità (unit_damages.code)")
    print("  - Creatori (creator_type, creator_names.qualifier, creator_legal_statuses.legal_status)")
    print("  - Custodi (custodian_type, custodians.legal_status, custodian_names.qualifier, custodian_buildings.custodian_building_type, custodian_contacts.contact_type)")
    print("  - Progetti (projects.project_type, projects.status)")
    print("  - Voci di indice (headings.heading_type)")
    print("  - Editori (editors.editing_type)")
    print("  - Oggetti digitali (digital_objects.digital_object_type)")
    print("  - Anagrafiche (anagraphics.anagraphic_type)")
    print("  - FE (fe_operas.status)")
    print("\n" + "=" * 60)

if __name__ == '__main__':
    seed_vocabularies()
