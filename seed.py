import os
import django
from django.db import connection

print("Pre-inizializzazione Django...")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()
print("Post-inizializzazione Django.")

from archimista_python.archive.models import (
    Group, Fond, Unit, Creator, Custodian, CreatorCorporateType, CustodianType,
    Heading, DigitalObject, RelCreatorFond, RelFondHeading,
    Classification, BiogHist, Event, RelCustodianFond, RelUnitHeading,
    Institution, Source, Sc2, IccdAuthor, IccdDescription
)

print("Avvio del popolamento dati...")

def clear_database():
    print("Inizio pulizia database...")
    with connection.cursor() as cursor:
        cursor.execute("PRAGMA foreign_keys = OFF;")
        
        # Lista di tutti i modelli da ripulire
        models = [
            Sc2, IccdDescription, IccdAuthor,
            Event, BiogHist, DigitalObject, 
            RelUnitHeading, RelFondHeading, RelCustodianFond, RelCreatorFond,
            Heading, Unit, Classification, Fond, 
            Custodian, Creator, CustodianType, CreatorCorporateType,
            Institution, Source, Group
        ]
        
        for model in models:
            model.objects.all().delete()
            print(f"Deleted {model.__name__}")
            
        cursor.execute("PRAGMA foreign_keys = ON;")
    print("Database ripulito.")

try:
    clear_database()

    group = Group.objects.create(name="Archivio Storico Comunale", short_name="ASC")
    print("Created Group")
    
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
    print("Created CorpType")
    
    cust_type = CustodianType.objects.create(custodian_type="Archivio di Stato")
    print("Created CustType")
 
    creator = Creator.objects.create(
        creator_type="E", 
        creator_corporate_type=corp_types[0], 
        abstract="Comune storico fondato nel XII secolo.",
        group=group
    )
    print("Created Creator")

    custodian = Custodian.objects.create(
        custodian_type=cust_type,
        owner="Ministero dei Beni Culturali",
        group=group
    )
    print("Created Custodian")

    fond1 = Fond.objects.create(
        name="Fondo Deliberazioni Comunali",
        fond_type="Fondo",
        abstract="Raccolta delle deliberazioni storiche dal 1800 al 1950.",
        history="Versato nel 1960 dal Comune.",
        group=group,
        position=1
    )
    print("Created Fond")

    # Relazione tra Creatore e Fondo
    RelCreatorFond.objects.create(creator=creator, fond=fond1)
    print("Created RelCreatorFond")

    # Voci di Indice
    h1 = Heading.objects.create(name="Giuseppe Garibaldi", heading_type="Persona", dates="1807-1882", group=group)
    h2 = Heading.objects.create(name="Torino", heading_type="Luogo", group=group)
    print("Created Headings")

    # Relazione tra Fondo e Voce di Indice
    RelFondHeading.objects.create(fond=fond1, heading=h2)
    print("Created RelFondHeading")

    # Classificazione (Titolario)
    cat1 = Classification.objects.create(name="Affari Generali", code="1", group=group)
    cat1_1 = Classification.objects.create(name="Protocollo", code="1.1", parent=cat1, group=group)
    print("Created Classification")

    unit1 = Unit.objects.create(
        fond=fond1,
        title="Delibere della Giunta 1850",
        unit_type="Fascicolo",
        reference_number="Busta 1, Fasc. 1",
        content="Verbali delle sedute della giunta comunale dell'anno 1850.",
        position=1,
        classification=cat1_1
    )
    print("Created Unit and linked to Classification")

    # Oggetto Digitale polimorfico collegato all'Unità
    from django.contrib.contenttypes.models import ContentType
    DigitalObject.objects.create(
        content_type=ContentType.objects.get_for_model(unit1),
        object_id=unit1.id,
        title="Scansione verbale 12 Marzo 1850",
        asset_file_name="verbale_1850_03_12.pdf",
        asset_content_type="application/pdf",
        asset_file_size=1024500,
        group=group
    )
    print("Created DigitalObject")

    # Biografie ed Eventi
    BiogHist.objects.create(
        content_object=creator,
        body="Il Comune è un ente territoriale con autonomia statutaria.",
        abstract="Storia sintetica dell'ente."
    )
    print("Created BiogHist for Creator")

    Event.objects.create(
        content_object=fond1,
        event_type="Creazione",
        start_date_display="1800",
        end_date_display="1950",
        preferred=True
    )
    print("Created Event for Fond")

    # DATI SPECIALISTICI FASE 5
    # Scheda Sc2 (Disegno Tecnico)
    Sc2.objects.create(
        unit=unit1,
        card_type="SC2",
        sgti="Pianta del piano terra",
        mtce="Inchiostro su carta",
        sdtt="Planimetria",
    )
    print("Created Sc2 card")

    # Scheda Iccd
    author = IccdAuthor.objects.create(name="Anonimo piemontese", role="Disegnatore")
    iccd = IccdDescription.objects.create(
        unit=unit1,
        denomination="Verbale di giunta",
        object_type="Documento cartaceo",
        category="Archivio storico",
        age_century="XIX secolo"
    )
    iccd.authors.add(author)
    print("Created Iccd card")

    print("Completato! Dati mock Fase 5 inseriti correttamente.")
except Exception as e:
    import traceback
    print(f"Errore durante il seeding: {e}")
    traceback.print_exc()
