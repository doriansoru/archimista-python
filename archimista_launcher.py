"""
Archimista Launcher — Smart startup script for the bundled application.

All Django imports are at module level so PyInstaller can detect them.
"""

import os
import sys
import webbrowser
import threading
import time
import secrets
import string
import pathlib

# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------
def _is_frozen():
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')


def _app_dir():
    if _is_frozen():
        return pathlib.Path(sys.executable).parent
    return pathlib.Path(__file__).resolve().parent


APP_DIR = _app_dir()
os.chdir(str(APP_DIR))

# Ensure current directory is on sys.path
app_dir_str = str(APP_DIR)
if app_dir_str not in sys.path:
    sys.path.insert(0, app_dir_str)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')

# ---------------------------------------------------------------------------
# Django setup — MUST happen before any other Django import
# ---------------------------------------------------------------------------
import django
django.setup()

from django.core.management import call_command

DB_PATH = APP_DIR / 'db.sqlite3'


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------
def _banner(title):
    w = 60
    print()
    print('=' * w)
    print('  ' + title)
    print('=' * w)


def _ok(msg):
    print('  [OK] ' + msg)


def _err(msg):
    print('  [ERRORE] ' + msg)


def _info(msg):
    print('  ' + msg)


# ---------------------------------------------------------------------------
# Seed script runners (import dynamically to avoid issues at bundle time)
# ---------------------------------------------------------------------------
def _run_seed_vocabularies():
    """Run seed_vocabularies.py logic."""
    from archimista_python.archive.models import Vocabulary, Term

    def create_vocabulary(name, description=None):
        vocab, created = Vocabulary.objects.get_or_create(
            name=name,
            defaults={'description': description} if description else {}
        )
        if created:
            print('    Creato vocabolario: ' + name)
        return vocab

    def create_term(vocab, term_key, term_value, position=1):
        term, created = Term.objects.update_or_create(
            vocabulary=vocab,
            term_key=term_key,
            defaults={
                'term': term_value,
                'term_value': term_value,
                'position': position
            }
        )
        return term

    def sync_terms(vocab, terms_list):
        valid_keys = [t[0] for t in terms_list]
        Term.objects.filter(vocabulary=vocab).exclude(term_key__in=valid_keys).delete()
        for i, (key, value) in enumerate(terms_list, 1):
            Term.objects.update_or_create(
                vocabulary=vocab,
                term_key=key,
                defaults={
                    'term': value,
                    'term_value': value,
                    'position': i
                }
            )

    # All vocabulary data
    vocab_data = {
        'fonds.fond_type': ('Tipologia del fondo archivistico', [
            ('fonds.fond_type.collection', 'Collezione'),
            ('fonds.fond_type.fonds', 'Fondo'),
            ('fonds.fond_type.fonds_group', 'Gruppo di fondi'),
            ('fonds.fond_type.subfonds', 'Subfondo'),
            ('fonds.fond_type.series', 'Serie'),
            ('fonds.fond_type.subseries', 'Sottoserie'),
            ('fonds.fond_type.file', 'Fascicolo'),
            ('fonds.fond_type.subfile', 'Sottofascicolo'),
            ('fonds.fond_type.item', 'Unita'),
            ('fonds.fond_type.section', 'Sezione'),
            ('fonds.fond_type.other', 'Altro'),
        ]),
        'fonds.access_condition': ('Condizione di accesso al fondo', [
            ('fonds.access_condition.liberamente_accessibile', 'liberamente accessibile'),
            ('fonds.access_condition.accessibile_previa_autorizzazione', 'accessibile previa autorizzazione'),
            ('fonds.access_condition.non_consultabile', 'non consultabile'),
            ('fonds.access_condition.parzialmente_accessibile', 'parzialmente accessibile'),
        ]),
        'fonds.use_condition': ('Condizione d\'uso del fondo', [
            ('fonds.use_condition.libera', 'libera'),
            ('fonds.use_condition.consentita_per_uso_studio', 'consentita per uso studio'),
            ('fonds.use_condition.a_pagamento', 'a pagamento'),
            ('fonds.use_condition.negata', 'negata'),
        ]),
        'fonds.preservation': ('Stato di conservazione fondo', [
            ('fonds.preservation.excellent', 'ottimo'),
            ('fonds.preservation.good', 'buono'),
            ('fonds.preservation.discreet', 'discreto'),
            ('fonds.preservation.mediocre', 'mediocre'),
            ('fonds.preservation.bad', 'cattivo'),
            ('fonds.preservation.very_bad', 'pessimo'),
        ]),
        'fonds.description_type': ('Tipo di descrizione archivistica', [
            ('fonds.description_type.analytic', 'Analitica'),
            ('fonds.description_type.summary', 'Sintetica'),
            ('fonds.description_type.intermediate', 'Intermedia'),
            ('fonds.description_type.detailed', 'Dettagliata'),
        ]),
        'units.unit_type': ('Tipo di unita archivistica', [
            ('units.unit_type.list', 'registro o altra unita rilegata'),
            ('units.unit_type.file', 'fascicolo o altra unita complessa'),
            ('units.unit_type.item', 'unita documentaria'),
        ]),
        'units.physical_type': ('Tipo fisico dell\'unita archivistica', [
            ('units.physical_type.album', 'album'),
            ('units.physical_type.busta', 'busta'),
            ('units.physical_type.cartella', 'cartella'),
            ('units.physical_type.faldone', 'faldone'),
            ('units.physical_type.fascicolo', 'fascicolo'),
            ('units.physical_type.filza', 'filza'),
            ('units.physical_type.foglio', 'foglio'),
            ('units.physical_type.manifesto', 'manifesto'),
            ('units.physical_type.mappa', 'mappa'),
            ('units.physical_type.mazzo', 'mazzo'),
            ('units.physical_type.opuscolo', 'opuscolo'),
            ('units.physical_type.pacco', 'pacco'),
            ('units.physical_type.plico', 'plico'),
            ('units.physical_type.quaderno', 'quaderno'),
            ('units.physical_type.registro', 'registro'),
            ('units.physical_type.rivista', 'rivista'),
            ('units.physical_type.rotolo', 'rotolo'),
            ('units.physical_type.scatola', 'scatola'),
            ('units.physical_type.scheda', 'scheda'),
            ('units.physical_type.taccuino', 'taccuino'),
            ('units.physical_type.volume', 'volume'),
        ]),
        'units.medium': ('Supporto materiale', [
            ('units.medium.paper', 'carta'),
            ('units.medium.parchment', 'pergamena'),
            ('units.medium.linen_paper', 'carta telata'),
            ('units.medium.cardboard', 'cartoncino'),
            ('units.medium.film', 'pellicola'),
            ('units.medium.other', 'altro'),
        ]),
        'units.level_type': ('Tipo di livello archivistico', [
            ('units.level_type.collection', 'Collezione'),
            ('units.level_type.fonds', 'Fondo'),
            ('units.level_type.series', 'Serie'),
            ('units.level_type.subseries', 'Sottoserie'),
            ('units.level_type.file', 'Fascicolo'),
            ('units.level_type.item', 'Unita'),
        ]),
        'unit_damages.code': ('Tipologia danni', [
            ('unit_damages.code.humidity', 'danni da umidita'),
            ('unit_damages.code.flood', 'danni da alluvione'),
            ('unit_damages.code.rodents', 'danni da roditori'),
            ('unit_damages.code.insects', 'danni da insetti'),
            ('unit_damages.code.fire', 'danni da incendio'),
            ('unit_damages.code.laceration', 'lacerazione'),
            ('unit_damages.code.stain', 'macchia'),
            ('unit_damages.code.mutilation', 'mutilazione'),
            ('unit_damages.code.perforation', 'perforazione'),
            ('unit_damages.code.folds', 'piegature'),
            ('unit_damages.code.discoloration', 'scoloritura'),
            ('unit_damages.code.crease', 'sgualcitura'),
            ('unit_damages.code.fragile', 'fragilita del supporto'),
            ('unit_damages.code.funghi_e_batteri', 'funghi e batteri'),
            ('unit_damages.code.strappi', 'strappi'),
            ('unit_damages.code.fogli_staccati', 'fogli staccati'),
            ('unit_damages.code.ingiallimento', 'ingiallimento della carta'),
            ('unit_damages.code.lacune', 'lacune'),
            ('unit_damages.code.sbiadimento', 'sbiadimento'),
            ('unit_damages.code.dispersione', 'dispersione'),
            ('unit_damages.code.acidita', 'acidita'),
            ('unit_damages.code.usura', 'usura'),
            ('unit_damages.code.rottura_cuciture', 'rottura delle cuciture'),
        ]),
        'creators.creator_type': ('Tipo di creatore', [
            ('creators.creator_type.person', 'Persona'),
            ('creators.creator_type.family', 'Famiglia'),
            ('creators.creator_type.organization', 'Ente/Organizzazione'),
        ]),
        'custodians.custodian_type': ('Tipo di custode', [
            ('custodians.custodian_type.archive', 'Archivio'),
            ('custodians.custodian_type.library', 'Biblioteca'),
            ('custodians.custodian_type.museum', 'Museo'),
            ('custodians.custodian_type.institution', 'Istituzione'),
            ('custodians.custodian_type.private', 'Privato'),
            ('custodians.custodian_type.other', 'Altro'),
        ]),
        'headings.heading_type': ('Tipo di voce di indice', [
            ('headings.heading_type.corporate_body', 'Ente'),
            ('headings.heading_type.person', 'Persona'),
            ('headings.heading_type.family', 'Famiglia'),
            ('headings.heading_type.geographic', 'Toponimo'),
            ('headings.heading_type.other', 'Altro'),
        ]),
        'editors.editing_type': ('Tipo di compilazione', [
            ('editors.editing_type.aggiornamento_scheda', 'aggiornamento scheda'),
            ('editors.editing_type.inserimento_dati', 'inserimento dati'),
            ('editors.editing_type.integrazione_successiva', 'integrazione successiva'),
            ('editors.editing_type.prima_redazione', 'prima redazione'),
            ('editors.editing_type.revisione', 'revisione'),
            ('editors.editing_type.rielaborazione', 'rielaborazione'),
            ('editors.editing_type.schedatura', 'schedatura'),
        ]),
        'digital_objects.digital_object_type': ('Tipo di oggetto digitale', [
            ('digital_objects.digital_object_type.image', 'Immagine'),
            ('digital_objects.digital_object_type.text', 'Testo'),
            ('digital_objects.digital_object_type.audio', 'Audio'),
            ('digital_objects.digital_object_type.video', 'Video'),
            ('digital_objects.digital_object_type.dataset', 'Dataset'),
            ('digital_objects.digital_object_type.other', 'Altro'),
        ]),
        'projects.project_type': ('Tipologia d\'intervento', [
            ('censimento', 'Censimento/guida'),
            ('riordino', 'Riordino e inventariazione'),
            ('recupero', 'Recupero e rielaborazione di corredo pregresso'),
            ('elenchi', 'Elenchi'),
        ]),
        'projects.status': ('Status del progetto', [
            ('in_corso', 'In corso'),
            ('concluso', 'Concluso/consegnato'),
            ('revisione', 'Revisione'),
            ('pubblicato', 'Pubblicato/da pubblicare'),
        ]),
    }

    print('  Popolamento vocabolari...')
    for vocab_name, (desc, terms) in vocab_data.items():
        vocab = create_vocabulary(vocab_name, desc)
        for i, (key, value) in enumerate(terms, 1):
            create_term(vocab, key, value, i)

    # Access/use conditions shared between fonds and units
    access_conditions = [
        ('liberamente_accessibile', 'liberamente accessibile'),
        ('accessibile_previa_autorizzazione', 'accessibile previa autorizzazione'),
        ('non_consultabile', 'non consultabile'),
        ('parzialmente_accessibile', 'parzialmente accessibile'),
    ]
    use_conditions = [
        ('libera', 'libera'),
        ('consentita_per_uso_studio', 'consentita per uso studio'),
        ('a_pagamento', 'a pagamento'),
        ('negata', 'negata'),
    ]

    # Unit-specific vocabularies
    for prefix, terms in [('units.access_condition', access_conditions),
                           ('units.use_condition', use_conditions)]:
        vocab = create_vocabulary(prefix, prefix.replace('_', ' ').title())
        for i, (key, value) in enumerate(terms, 1):
            create_term(vocab, prefix + '.' + key, value, i)

    # Unit preservation
    vocab = create_vocabulary('units.preservation', 'Stato di conservazione unita')
    for i, (key, value) in enumerate([
        ('units.preservation.excellent', 'ottimo'),
        ('units.preservation.good', 'buono'),
        ('units.preservation.discreet', 'discreto'),
        ('units.preservation.mediocre', 'mediocre'),
        ('units.preservation.bad', 'cattivo'),
        ('units.preservation.very_bad', 'pessimo'),
    ], 1):
        create_term(vocab, key, value, i)

    # More vocabularies
    more = {
        'creator_names.qualifier': ('Qualificatore per nomi di creatore', [
            ('creator_names.qualifier.birth_name', 'Nome di nascita'),
            ('creator_names.qualifier.pseudonym', 'Pseudonimo'),
            ('creator_names.qualifier.variant', 'Variante'),
            ('creator_names.qualifier.alternative', 'Alternativo'),
        ]),
        'creator_legal_statuses.legal_status': ('Stato giuridico del creatore', [
            ('creator_legal_statuses.legal_status.public', 'Pubblico'),
            ('creator_legal_statuses.legal_status.private', 'Privato'),
            ('creator_legal_statuses.legal_status.mixed', 'Misto'),
        ]),
        'custodians.legal_status': ('Stato giuridico del custode', [
            ('custodians.legal_status.public', 'Pubblico'),
            ('custodians.legal_status.private', 'Privato'),
        ]),
        'custodian_names.qualifier': ('Qualificatore per nomi di custode', [
            ('custodian_names.qualifier.official', 'Ufficiale'),
            ('custodian_names.qualifier.variant', 'Variante'),
            ('custodian_names.qualifier.alternative', 'Alternativo'),
        ]),
        'custodian_buildings.custodian_building_type': ('Tipo di edificio del custode', [
            ('custodian_buildings.custodian_building_type.main', 'Edificio principale'),
            ('custodian_buildings.custodian_building_type.annex', 'Annesso'),
            ('custodian_buildings.custodian_building_type.depot', 'Deposito'),
            ('custodian_buildings.custodian_building_type.other', 'Altro'),
        ]),
        'custodian_contacts.contact_type': ('Tipo di contatto', [
            ('custodian_contacts.contact_type.phone', 'Telefono'),
            ('custodian_contacts.contact_type.fax', 'Fax'),
            ('custodian_contacts.contact_type.email', 'Email'),
            ('custodian_contacts.contact_type.website', 'Sito web'),
            ('custodian_contacts.contact_type.address', 'Indirizzo'),
        ]),
        'project_managers.qualifier': ('Qualificatore responsabile progetto', [
            ('responsabile_scientifico', 'Responsabile scientifico'),
            ('responsabile_operativo', 'Responsabile operativo'),
            ('schedatore', 'Schedatore'),
            ('coordinatore', 'Coordinatore'),
        ]),
        'project_stakeholders.qualifier': ('Qualificatore stakeholder', [
            ('finanziamento', 'Finanziamento'),
            ('realizzazione', 'Realizzazione'),
            ('promozione', 'Promozione'),
            ('coordinamento_operativo', 'Coordinamento operativo'),
        ]),
        'units.file_type': ('Tipo file', [
            ('units.file_type.personal', 'Personale'),
            ('units.file_type.family', 'Famiglia'),
            ('units.file_type.corporate', 'Aziendale'),
        ]),
        'anagraphics.anagraphic_type': ('Tipo anagrafica', [
            ('anagraphics.anagraphic_type.person', 'Persona'),
            ('anagraphics.anagraphic_type.family', 'Famiglia'),
        ]),
        'fe_operas.status': ('Stato opera edilizia', [
            ('fe_operas.status.new', 'Nuovo'),
            ('fe_operas.status.existing', 'Esistente'),
            ('fe_operas.status.demolished', 'Demolito'),
        ]),
    }
    for vocab_name, (desc, terms) in more.items():
        vocab = create_vocabulary(vocab_name, desc)
        for i, (key, value) in enumerate(terms, 1):
            create_term(vocab, key, value, i)


def _run_seed_source_types():
    """Run seed_source_types.py logic."""
    from archimista_python.archive.models import SourceType

    data = [
        (1, 'bibliografia', None, 1),
        (2, 'strumento di corredo', None, 2),
        (3, 'fonte archivistica', None, 3),
        (4, 'fonte normativa', None, 4),
        (1001, 'libro', 1, 1),
        (1002, 'capitolo di libro', 1, 2),
        (1003, 'articolo di rivista', 1, 3),
        (1004, 'atti di convegno', 1, 4),
        (1005, 'intervento in convegno', 1, 5),
        (1006, 'altro', 1, 6),
        (2001, 'banca dati', 2, 1),
        (2002, 'censimento', 2, 2),
        (2003, 'documenti', 2, 3),
        (2004, 'edizione di fonti', 2, 4),
        (2005, 'elenco', 2, 5),
        (2006, 'elenco di consistenza', 2, 6),
        (2007, 'elenco di deposito', 2, 7),
        (2008, 'elenco di versamento', 2, 8),
        (2009, 'guida', 2, 9),
        (2010, 'indice', 2, 10),
        (2011, 'inventario', 2, 11),
        (2012, 'inventario analitico', 2, 12),
        (2013, 'inventario sommario', 2, 13),
        (2014, 'inventario topografico', 2, 14),
        (2015, 'regesto', 2, 15),
        (2016, 'repertorio', 2, 16),
        (2017, 'repertorio alfabetico', 2, 17),
        (2018, 'repertorio cronologico', 2, 18),
        (2019, 'rubrica', 2, 19),
        (2020, 'schedario', 2, 20),
        (2021, 'schedatura', 2, 21),
        (2022, 'titolario', 2, 22),
    ]

    for code, name, parent, pos in data:
        SourceType.objects.update_or_create(
            code=code,
            defaults={
                'source_type': name,
                'parent_code': parent,
                'position': pos,
            }
        )


def _run_seed_demo():
    """Run seed.py demo data logic."""
    from archimista_python.archive.models import (
        Group, Fond, Unit, Creator, Custodian, CreatorCorporateType, CustodianType,
        Heading, DigitalObject, RelCreatorFond, RelFondHeading,
        Classification, BiogHist, Event, RelCustodianFond, RelUnitHeading,
        Institution, Source, Sc2, IccdAuthor, IccdDescription
    )
    from django.contrib.contenttypes.models import ContentType

    # Clear
    from django.db import connection
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA foreign_keys = OFF;')
    for model in [Sc2, IccdDescription, IccdAuthor, Event, BiogHist,
                   DigitalObject, RelUnitHeading, RelFondHeading, RelCustodianFond,
                   RelCreatorFond, Heading, Unit, Classification, Fond,
                   Custodian, Creator, CustodianType, CreatorCorporateType,
                   Institution, Source, Group]:
        model.objects.all().delete()
    with connection.cursor() as cursor:
        cursor.execute('PRAGMA foreign_keys = ON;')

    group = Group.objects.create(name='Archivio Storico Comunale', short_name='ASC')

    corp_types = []
    for ct_name in [
        'stato', 'regione', 'ente pubblico territoriale',
        'ente funzionale territoriale', 'ente economico / impresa',
        'ente di credito, assicurativo, previdenziale',
        'ente di assistenza e beneficenza', 'ente sanitario',
        'ente di istruzione e ricerca',
        'ente di cultura, ricreativo, sportivo, turistico',
        'partito politico, organizzazione sindacale',
        'ordine professionale, associazione di categoria',
        'ente e associazione della chiesa cattolica',
        'ente e associazione di culto acattolico',
        'preunitario', 'organo giudiziario',
        'organo periferico dello stato', 'ente ecclesiastico',
    ]:
        corp_types.append(CreatorCorporateType.objects.create(corporate_type=ct_name))

    cust_type = CustodianType.objects.create(custodian_type='Archivio di Stato')

    creator = Creator.objects.create(
        creator_type='E',
        creator_corporate_type=corp_types[0],
        abstract='Comune storico fondato nel XII secolo.',
        group=group
    )

    custodian = Custodian.objects.create(
        custodian_type=cust_type,
        owner='Ministero dei Beni Culturali',
        group=group
    )

    fond1 = Fond.objects.create(
        name='Fondo Deliberazioni Comunali',
        fond_type='Fondo',
        abstract='Raccolta delle deliberazioni storiche dal 1800 al 1950.',
        history='Versato nel 1960 dal Comune.',
        group=group,
        position=1
    )

    RelCreatorFond.objects.create(creator=creator, fond=fond1)

    h1 = Heading.objects.create(name='Giuseppe Garibaldi', heading_type='Persona',
                                 dates='1807-1882', group=group)
    h2 = Heading.objects.create(name='Torino', heading_type='Luogo', group=group)

    RelFondHeading.objects.create(fond=fond1, heading=h2)

    cat1 = Classification.objects.create(name='Affari Generali', code='1', group=group)
    cat1_1 = Classification.objects.create(name='Protocollo', code='1.1',
                                            parent=cat1, group=group)

    unit1 = Unit.objects.create(
        fond=fond1,
        title='Delibere della Giunta 1850',
        unit_type='Fascicolo',
        reference_number='Busta 1, Fasc. 1',
        content='Verbali delle sedute della giunta comunale dell\'anno 1850.',
        position=1,
        classification=cat1_1
    )

    DigitalObject.objects.create(
        content_type=ContentType.objects.get_for_model(unit1),
        object_id=unit1.id,
        title='Scansione verbale 12 Marzo 1850',
        asset_file_name='verbale_1850_03_12.pdf',
        asset_content_type='application/pdf',
        asset_file_size=1024500,
        group=group
    )

    BiogHist.objects.create(
        content_object=creator,
        body='Il Comune e un ente territoriale con autonomia statutaria.',
        abstract='Storia sintetica dell\'ente.'
    )

    Event.objects.create(
        content_object=fond1,
        event_type='Creazione',
        start_date_display='1800',
        end_date_display='1950',
        preferred=True
    )

    Sc2.objects.create(
        unit=unit1,
        card_type='SC2',
        sgti='Pianta del piano terra',
        mtce='Inchiostro su carta',
        sdtt='Planimetria',
    )

    author = IccdAuthor.objects.create(name='Anonimo piemontese', role='Disegnatore')
    iccd = IccdDescription.objects.create(
        unit=unit1,
        denomination='Verbale di giunta',
        object_type='Documento cartaceo',
        category='Archivio storico',
        age_century='XIX secolo'
    )
    iccd.authors.add(author)


def _run_seed_admin_user(username='admin', password=None):
    """Create admin user."""
    from django.contrib.auth.models import User
    from archimista_python.archive.models import UserProfile

    if password is None:
        password = ''.join(
            secrets.choice(string.ascii_letters + string.digits + '!@#$%')
            for _ in range(12)
        )

    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.must_change_password = True
        profile.save()
        return password, False

    user = User.objects.create_user(
        username=username,
        email='admin@archimista.local',
        password=password,
        is_staff=True,
        is_superuser=True,
    )
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.must_change_password = True
    profile.save()
    return password, True


# ---------------------------------------------------------------------------
# First-run setup
# ---------------------------------------------------------------------------
def _first_run_setup():
    """Run the complete first-run initialization."""
    _banner('Prima esecuzione — Configurazione iniziale')

    # --- Passo 1/5: Migrazioni ---
    _info('Passo 1/5: Applicazione migrazioni database...')
    try:
        call_command('migrate', '--no-input')
        _ok('Migrazioni applicate.')
    except Exception as e:
        _err('Migrazioni fallite: ' + str(e))
        sys.exit(1)

    # --- Passo 2/5: Vocabolari ---
    _info('Passo 2/5: Popolamento vocabolari controllati...')
    try:
        _run_seed_vocabularies()
        _ok('Vocabolari popolati.')
    except Exception as e:
        _err('Seed vocabolari fallito: ' + str(e))
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # --- Passo 3/5: Source types ---
    _info('Passo 3/5: Popolamento tipologie di fonte...')
    try:
        _run_seed_source_types()
        _ok('Tipologie di fonte popolate.')
    except Exception as e:
        _err('Seed source_types fallito: ' + str(e))
        sys.exit(1)

    # --- Passo 4/5: Demo data (optional) ---
    print()
    _info('Passo 4/5: Dati di esempio')
    while True:
        try:
            answer = input('  Vuoi inserire i dati di esempio? (S/n): ').strip().lower()
        except (EOFError, KeyboardInterrupt):
            answer = 'n'
            print()
        if answer in ('', 's', 'si', 'y', 'yes'):
            _info('Inserimento dati di esempio in corso...')
            try:
                _run_seed_demo()
                _ok('Dati di esempio inseriti.')
            except Exception as e:
                _err('Seed dati fallito: ' + str(e))
                import traceback
                traceback.print_exc()
                sys.exit(1)
            break
        elif answer in ('n', 'no'):
            _info('Dati di esempio saltati.')
            break
        else:
            _info('Rispondi S oppure N.')

    # --- Passo 5/5: Admin user ---
    _info('Passo 5/5: Creazione utente admin...')

    temp_password, is_new = _run_seed_admin_user()

    print()
    print('=' * 60)
    print('  UTENTE ADMIN CREATO — SALVA QUESTE CREDENZIALI!')
    print('=' * 60)
    print('  Username: admin')
    print('  Password: ' + temp_password)
    print('=' * 60)
    print('  Al primo accesso ti sara chiesto di cambiare la password.')
    print('=' * 60)
    print()

    creds_file = APP_DIR / 'admin_credentials.txt'
    try:
        with open(creds_file, 'w', encoding='utf-8') as f:
            f.write('Archimista — Credenziali admin\n')
            f.write('=' * 40 + '\n')
            f.write('Username: admin\n')
            f.write('Password: ' + temp_password + '\n')
            f.write('=' * 40 + '\n')
            f.write('Al primo accesso il sistema chiedera di cambiare la password.\n')
            f.write('Generato il: ' + time.strftime('%Y-%m-%d %H:%M:%S') + '\n')
        _ok('Credenziali salvate in: ' + str(creds_file))
    except Exception:
        _err('Impossibile salvare le credenziali su file. Annotale manualmente!')


# ---------------------------------------------------------------------------
# Server startup
# ---------------------------------------------------------------------------
def _start_server():
    """Start the Django dev server and open the browser."""
    _banner('Avvio di Archimista')

    if not DB_PATH.exists():
        _err('Database non trovato. Esegui prima la configurazione iniziale.')
        _info('Elimina il file "first_run.done" se presente e riprova.')
        input('\nPremi Invio per uscire...')
        sys.exit(1)

    port = 8000
    url = 'http://127.0.0.1:' + str(port)

    _info('Server avviato su ' + url)
    _info('Premi Ctrl+C per fermare il server.')
    print()

    def _open_browser():
        time.sleep(2)
        webbrowser.open(url)

    t = threading.Thread(target=_open_browser, daemon=True)
    t.start()

    # Disable autoreloader — breaks in PyInstaller (sys.argv is empty)
    call_command('runserver', '127.0.0.1:' + str(port), '--noreload')


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    _banner('Archimista — Archivistico digitale')

    first_run_marker = APP_DIR / 'first_run.done'

    if not first_run_marker.exists():
        _first_run_setup()
        try:
            first_run_marker.touch()
        except Exception:
            pass

    _start_server()


if __name__ == '__main__':
    main()
