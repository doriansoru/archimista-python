#!/usr/bin/env python
"""
Genera un AEF di riferimento completo + export XML per il confronto Python <-> Ruby.

Questo script:
1. Crea dati completi nel DB (Fond + Unit + SC2 + ICCD + FSC + FE + Creator + Custodian
   + Project + relazioni + oggetti digitali)
2. Esporta il fondo in 5 file nella directory tests/regression/reference/:

OUTPUT — File generati:
─────────────────────────────────────────────────────────────────────
File                          Formato       A cosa serve
─────────────────────────────────────────────────────────────────────
reference_aef.aef             ZIP (NDJSON)  Import su Archimista Ruby (estensione .aef)
reference_aef.zip             ZIP (NDJSON)  Confronto automatico Python (stesso contenuto
                                            del .aef, solo estensione diversa)
reference_san.zip             ZIP (XML)     Export CAT-SAN / METS-SAN (standard italiano
                                            Sistema Archivistico Nazionale)
reference_ead.zip             ZIP (XML)     Export EAD3 / EAC-CPF / SCONS2
                                            (standard internazionale + ICAR-IMPORT)
reference_mets.zip            ZIP (XML)     Export METS per oggetti digitali
                                            (envelope SAN + METS)
python_report.pdf             PDF           Report inventario fondo (WeasyPrint)
python_report.rtf             RTF           Report inventario fondo (RtfBuilder)
─────────────────────────────────────────────────────────────────────

Nota: reference_aef.aef e reference_aef.zip sono IDENTICI nel contenuto (stesso ZIP).
La differenza è solo l'estensione: Ruby richiede .aef, i tool Python accettano .zip.

L'export AEF è generato con le opzioni MASSIME per il confronto:
  - ✅ Oggetti digitali inclusi
  - ✅ Entità correlate incluse (creatori, conservatori, progetti, fonti, ecc.)
Così si verifica che tutto il grafo di dati sopravviva al round-trip Python → Ruby → Python.

WORKFLOW CONFRONTO CON RUBY:
1. Esegui questo script → genera tutti i file sopra
2. Copia reference_aef.aef sulla VM VirtualBox
3. Importalo in Archimista Ruby
4. Da Ruby, esporta AEF/PDF/RTF → mettili in tests/regression/ruby_output/
   (opzionale: esporta anche SAN/EAD da Ruby → ruby_export_san.zip, ruby_export_ead.zip)
5. Esegui: python tests/regression/test_ruby_comparison.py
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()

from datetime import date
from django.core.files.base import ContentFile
from django.contrib.contenttypes.models import ContentType

from archimista_python.archive.aef_exporter import AEFExporter
from archimista_python.archive.models import (
    Group,
    Fond, Unit, Creator, Custodian, Project,
    FondName, FondIdentifier, FondLang, FondOwner, FondUrl, FondEditor,
    UnitIdentifier, UnitOtherReferenceNumber, UnitLang, UnitDamage, UnitUrl, UnitEditor,
    CreatorName, CreatorLegalStatus, CreatorUrl, CreatorIdentifier, CreatorActivity, CreatorEditor,
    CustodianName, CustodianIdentifier, CustodianContact, CustodianBuilding, CustodianOwner, CustodianUrl, CustodianEditor,
    CustodianType, CreatorCorporateType,
    Sc2, Sc2TextualElement, Sc2VisualElement, Sc2Author, Sc2AttributionReason,
    Sc2Commission, Sc2CommissionName, Sc2Technique, Sc2Scale,
    IccdDescription, IccdSubject, IccdDamage, IccdTechSpec,
    FscCode, FscOrganization, FscNationality, FscOpen, FscClose,
    FeIdentification, FeContext, FeOpera, FeDesigner, FeCadastral, FeLandParcel,
    FeFractLandParcel, FeFractEdilParcel,
    RelCreatorFond, RelCustodianFond, RelProjectFond,
    RelFondSource, RelFondHeading, RelFondDocumentForm,
    Source, Heading, DocumentForm, Anagraphic, Institution, InstitutionEditor,
    RelUnitHeading, RelUnitSource, RelUnitAnagraphic,
    Event, BiogHist, DigitalObject,
    RelCreatorCreator, RelCreatorInstitution,
    Editor,
)


def clear_reference_data():
    """Pulisce TUTTI i dati dal DB per garantire un AEF pulito."""
    print("  Pulizia dati esistenti...")
    for model in [
        FeFractEdilParcel, FeFractLandParcel, FeLandParcel, FeCadastral,
        FeDesigner, FeOpera, FeContext, FeIdentification,
        FscClose, FscOpen, FscNationality, FscOrganization, FscCode,
        IccdTechSpec, IccdDamage, IccdSubject, IccdDescription,
        Sc2Scale, Sc2Technique, Sc2CommissionName, Sc2Commission,
        Sc2AttributionReason, Sc2Author, Sc2VisualElement, Sc2TextualElement, Sc2,
        UnitEditor, UnitUrl, UnitDamage, UnitLang,
        UnitOtherReferenceNumber, UnitIdentifier,
        Unit,
        FondEditor, FondUrl, FondOwner, FondLang, FondIdentifier, FondName,
        Fond,
        CreatorEditor, CreatorActivity, CreatorIdentifier, CreatorUrl,
        CreatorLegalStatus, CreatorName, Creator,
        CustodianEditor, CustodianUrl, CustodianOwner, CustodianBuilding,
        CustodianContact, CustodianIdentifier, CustodianName, Custodian,
        RelCreatorFond, RelCustodianFond, RelProjectFond,
        RelFondSource, RelFondHeading, RelFondDocumentForm,
        RelUnitHeading, RelUnitSource, RelUnitAnagraphic,
        RelCreatorCreator, RelCreatorInstitution,
        Project, InstitutionEditor, Institution,
        Source, Heading, DocumentForm, Anagraphic,
        Event, BiogHist, DigitalObject, Editor,
        CustodianType, CreatorCorporateType, Group,
    ]:
        model.objects.all().delete()
    print("  DB pulito.")


def create_reference_data():
    """Crea tutti i dati di riferimento con field names corretti."""
    print("Creazione dati di riferimento...")

    # ─── Group ───
    group = Group.objects.create(id=1, name="Test Group")

    # ─── Editor (compilatore) ───
    editor1 = Editor.objects.create(first_name="Mario", last_name="Rossi", group=group)
    editor2 = Editor.objects.create(first_name="Laura", last_name="Bianchi", group=group)
    print(f"  Editor: {editor1}, {editor2}")

    # ─── Institution ───
    institution1 = Institution.objects.create(
        name="Soprintendenza Archivistica del Piemonte",
        description="Ente di tutela archivistica regionale.",
        group=group,
    )
    InstitutionEditor.objects.create(institution=institution1, name="Mario Rossi")
    print(f"  Institution: {institution1.name}")

    # ─── Source (Fonte) ───
    source1 = Source.objects.create(
        short_title="Guida archivi piemontesi",
        title="Guida agli archivi storici piemontesi",
        author="AA.VV.",
        year=2010,
        abstract="Fonte bibliografica principale per la catalogazione.",
        group=group,
    )
    print(f"  Source: {source1.title}")

    # ─── Heading (Voce di indice) ───
    heading1 = Heading.objects.create(
        name="Verdi, Giuseppe",
        heading_type="Persona",
        dates="1850-1920",
        qualifier="Architetto torinese.",
        group=group,
    )
    heading2 = Heading.objects.create(
        name="Torino",
        heading_type="Luogo",
        group=group,
    )
    print(f"  Headings: {heading1.name}, {heading2.name}")

    # ─── DocumentForm (Forma documentaria) ───
    docform1 = DocumentForm.objects.create(
        name="Deliberazione",
        description="Atto deliberativo del consiglio comunale.",
        note="Forma principale.",
        group=group,
    )
    docform2 = DocumentForm.objects.create(
        name="Verbale",
        description="Verbale di seduta.",
        group=group,
    )
    print(f"  DocumentForms: {docform1.name}, {docform2.name}")

    # ─── Anagraphic (Anagrafica persona) ───
    anagraphic1 = Anagraphic.objects.create(
        surname="Bianchi",
        name="Giuseppe",
        group=group,
    )
    print(f"  Anagraphic: {anagraphic1}")

    # ─── Creator (Soggetto produttore) ───
    corp_type, _ = CreatorCorporateType.objects.get_or_create(corporate_type="Ente pubblico territoriale")
    creator = Creator.objects.create(
        creator_type="E",
        creator_corporate_type=corp_type,
        abstract="Comune storico fondato nel XII secolo.",
        history="Attivita amministrativa dal 1850.",
        residence="Torino",
        note="Note aggiuntive sul soggetto.",
        group=group,
    )
    CreatorName.objects.create(
        creator=creator, name="Comune di Torino", preferred=True,
        qualifier="A", note="Denominazione principale.",
    )
    CreatorName.objects.create(
        creator=creator, name="Municipio di Torino", qualifier="Altro",
        note="Denominazione storica.",
    )
    CreatorIdentifier.objects.create(
        creator=creator, identifier="COD-TO-001", identifier_source="Codice IPA",
    )
    CreatorUrl.objects.create(
        creator=creator, url="https://www.comune.torino.it", note="Sito istituzionale.",
    )
    CreatorActivity.objects.create(
        creator=creator, activity="Amministrazione locale dal 1850.",
    )
    CreatorLegalStatus.objects.create(
        creator=creator, legal_status="Ente pubblico territoriale",
        note="Riconosciuto con legge regionale.",
    )
    CreatorEditor.objects.create(
        creator=creator, name="Mario Rossi", qualifier="Catalogatore",
        editing_type="catalogazione", edited_at=date.today().isoformat(),
    )
    Event.objects.create(
        content_type=ContentType.objects.get_for_model(Creator),
        object_id=creator.pk,
        start_date_from=date(1850, 1, 1),
        end_date_to=date(1920, 12, 31),
        start_date_display="1850 - 1920",
        preferred=False,
    )
    print(f"  Creator: Comune di Torino (+ estensioni)")

    # ─── Custodian (Soggetto conservatore) ───
    custodian_type = CustodianType.objects.create(custodian_type="Archivio di Stato")
    custodian = Custodian.objects.create(custodian_type=custodian_type, group=group)
    CustodianName.objects.create(
        custodian=custodian, name="Archivio Storico del Comune di Torino",
        preferred=True, qualifier="OT",
    )
    CustodianIdentifier.objects.create(
        custodian=custodian, identifier="ISAD-TO-001", identifier_source="Codice ICCD",
    )
    CustodianContact.objects.create(
        custodian=custodian, contact_type="Telefono", contact="+39 011 1234567",
    )
    CustodianBuilding.objects.create(
        custodian=custodian, name="Palazzo Civico",
        custodian_building_type="Archivio",
        address="Piazza Palazzo di Citta 1", city="Torino",
        postcode="10122", country="Italia",
    )
    CustodianOwner.objects.create(
        custodian=custodian, owner="Ministero della Cultura",
    )
    CustodianUrl.objects.create(
        custodian=custodian, url="https://www.archiviodistoricotorino.it",
    )
    CustodianEditor.objects.create(
        custodian=custodian, name="Laura Bianchi", qualifier="Responsabile",
        editing_type="catalogazione", edited_at=date.today().isoformat(),
    )
    print(f"  Custodian: Archivio Storico Torino (+ estensioni)")

    # ─── Project ───
    project = Project.objects.create(
        name="Progetto Catalogazione Archivi Storici",
        description="Progetto di catalogazione degli archivi storici comunali.",
        note="Iniziato nel 2020.",
        group=group,
    )
    print(f"  Project: {project.name}")

    # ─── Fond (Fondo archivistico) ───
    fond = Fond.objects.create(
        name="Fondo Deliberazioni Comunali 1850-1920",
        description="Fondo contenente le deliberazioni del Consiglio Comunale di Torino dal 1850 al 1920.",
        abstract="Il fondo raccoglie oltre 70 anni di attivita amministrativa del Comune di Torino.",
        history="Versato nel 1960 dal Comune di Torino all'Archivio Storico. Ordinamento originale mantenuto.",
        arrangement_note="Ordinamento per serie cronologica con sottoserie per materia.",
        related_materials="Materiali correlati presso la Biblioteca Nazionale di Torino.",
        note="Fondo chiuso. Consultazione previa autorizzazione.",
        group=group,
    )
    print(f"  Fond: {fond.name}")

    # Fond extensions
    FondName.objects.create(fond=fond, name="Deliberazioni 1850-1920", qualifier="Titolo alternativo")
    FondName.objects.create(fond=fond, name="Fondo DC", qualifier="Abbreviazione")
    FondIdentifier.objects.create(fond=fond, identifier="F-TO-001", identifier_source="Codice interno")
    FondLang.objects.create(fond=fond, code="ita")
    FondLang.objects.create(fond=fond, code="fra")
    FondOwner.objects.create(fond=fond, owner="Comune di Torino - Segreteria generale")
    FondUrl.objects.create(fond=fond, url="https://archivio.comune.torino.it/fondo-dc", note="Scheda online")
    FondEditor.objects.create(
        fond=fond, name="Mario Rossi", qualifier="Catalogatore",
        editing_type="catalogazione", edited_at=date.today().isoformat(),
    )
    Event.objects.create(
        content_type=ContentType.objects.get_for_model(Fond),
        object_id=fond.pk,
        start_date_from=date(1850, 1, 1),
        end_date_to=date(1920, 12, 31),
        start_date_display="1850 - 1920",
        preferred=False,
    )
    print("  Fond extensions create")

    # ─── Relations: Fond <-> Creator, Custodian, Project, Source, Heading, DocumentForm ───
    RelCreatorFond.objects.create(creator=creator, fond=fond)
    RelCustodianFond.objects.create(custodian=custodian, fond=fond)
    RelProjectFond.objects.create(project=project, fond=fond)
    RelFondSource.objects.create(fond=fond, source=source1)
    RelFondHeading.objects.create(fond=fond, heading=heading1)
    RelFondDocumentForm.objects.create(fond=fond, document_form=docform1)
    print("  Relazioni Fond create")

    # ─── Unit 1: Registro (con SC2 completa) ───
    unit1 = Unit.objects.create(
        fond=fond,
        title="Registro delle deliberazioni 1850-1860",
        content="Registro contenente le deliberazioni del consiglio comunale dal 1850 al 1860, con indici analitici.",
        unit_type="registro o altra unita rilegata",
        physical_type="registro",
        medium="carta",
        reference_number="1",
        given_title=False,
        extent="200 carte",
        arrangement_note="Ordinamento cronologico.",
        physical_description="Legatura in pelle con dorso dorato. Stato di conservazione buono.",
        related_materials="Copie digitali disponibili presso la sala studio.",
        preservation_note="Lievi segni di usura sul dorso.",
        restoration="Restauro effettuato nel 2010.",
        note="Unita di particolare pregio storico.",
        physical_container_type="Registro",
        physical_container_title="Deliberazioni 1850-1860",
        physical_container_number="1",
        created_by=1, updated_by=1,
    )
    UnitIdentifier.objects.create(unit=unit1, identifier="REG-001", note="Registro principale")
    UnitOtherReferenceNumber.objects.create(
        unit=unit1, other_reference_number="Cl. I, mazzo 1", qualifier="Collocazione",
    )
    UnitLang.objects.create(unit=unit1, code="ita")
    UnitDamage.objects.create(unit=unit1, code="lacune", note="Qualche lacuna nelle prime carte")
    UnitUrl.objects.create(unit=unit1, url="https://archivio.comune.torino.it/unit/reg-001")
    UnitEditor.objects.create(
        unit=unit1, name="Mario Rossi", qualifier="Catalogatore",
        editing_type="catalogazione", edited_at=date.today().isoformat(),
    )
    Event.objects.create(
        content_type=ContentType.objects.get_for_model(Unit),
        object_id=unit1.pk,
        start_date_from=date(1850, 1, 1),
        end_date_to=date(1860, 12, 31),
        start_date_display="1850 - 1860",
        preferred=False,
    )
    print(f"  Unit 1: {unit1.title}")

    # SC2 card per unit1 (Disegno tecnico)
    sc2 = Sc2.objects.create(
        unit=unit1, card_type="SC2",
        sgti="Pianta della citta di Torino",
        mtce="Matita e acquerello su carta",
        sdtt="Pianta", sdts="Urbana",
        dpgf="Torino, 1855",
        misa="50 x 70 cm", misl="cm 50,0 x 70,0",
        cmmr="CMMR-001", lrc="1855", ort="Orizzontale",
    )
    Sc2TextualElement.objects.create(
        unit=unit1, isri='Iscrizione in basso a destra: "Veduta di Torino"',
    )
    Sc2VisualElement.objects.create(unit=unit1, stmd="Buono")
    author = Sc2Author.objects.create(
        unit=unit1, autr="Architetto", autn="Giuseppe Verdi", auta="Torino 1820 - 1890",
    )
    Sc2AttributionReason.objects.create(sc2_author=author, autm="Attribuzione certa")
    commission = Sc2Commission.objects.create(unit=unit1, cmmc="Comune di Torino")
    Sc2CommissionName.objects.create(sc2_commission=commission, cmmn="Ufficio Tecnico Comunale")
    Sc2Technique.objects.create(unit=unit1, mtct="Matita")
    Sc2Technique.objects.create(unit=unit1, mtct="Acquerello")
    Sc2Scale.objects.create(unit=unit1, sca="1:2000")
    print(f"    SC2: {sc2.sgti}")

    # ─── Unit 2: Fascicolo personale (con FSC) ───
    unit2 = Unit.objects.create(
        fond=fond,
        parent=unit1,
        ancestry=str(unit1.pk),
        ancestry_depth=1,
        title="Fascicolo personale - Impiegato N. 1",
        content="Fascicolo relativo al dipendente comunale con documenti di assunzione, promozione e pensione.",
        unit_type="fascicolo o altra unita complessa",
        file_type="personale",
        fsc_name="FSC-001",
        fsc_surname="Rossi",
        reference_number="1.1",
        extent="50 carte",
        created_by=1, updated_by=1,
    )
    FscCode.objects.create(unit=unit2, code="FSC-001", note="Codice fascicolo sanitario")
    FscOrganization.objects.create(unit=unit2, organization="Ufficio Personale")
    FscNationality.objects.create(unit=unit2, nationality="Italiana")
    FscOpen.objects.create(unit=unit2, open="1900-01-15", note="Apertura pratica")
    FscClose.objects.create(unit=unit2, close="1950-12-31", note="Chiusura per pensionamento")
    print(f"  Unit 2: {unit2.title} (FSC)")

    # ─── Unit 3: Fascicolo edilizia (con FE) ───
    unit3 = Unit.objects.create(
        fond=fond,
        title="Fascicolo edilizio - Via Roma 10",
        content="Pratica edilizia per la costruzione dell'edificio in Via Roma 10.",
        unit_type="fascicolo o altra unita complessa",
        file_type="edilizia",
        reference_number="2",
        extent="120 carte",
        created_by=1, updated_by=1,
    )
    FeIdentification.objects.create(
        unit=unit3, code="FE-001", file_year=1920,
        category="Edilizia privata", identification_class="Nuova costruzione",
    )
    FeContext.objects.create(
        unit=unit3, number=1, sub_number=1, classification="Edilizia",
        applicant="Dott. Mario Bianchi", request="Permesso di costruzione",
        license_number=1001, license_year=1920, protocol_number=1,
    )
    FeOpera.objects.create(
        unit=unit3, is_present=True, status="resid.",
        building_name="Palazzo Bianchi", building_type="Palazzo",
        place_name="Via Roma", place_type="Strada urbana",
        house_number="10", district="Centro storico",
    )
    FeDesigner.objects.create(unit=unit3, designer_name="Ing. Luigi Neri", designer_role="Progettista")
    FeCadastral.objects.create(
        unit=unit3, way_code=1, cadastral_municipality="Torino", municipality_code=1,
    )
    FeLandParcel.objects.create(unit=unit3, land_parcel_number="100")
    FeFractLandParcel.objects.create(unit=unit3, fract_land_parcel_number=100, edil_parcel_number=1)
    FeFractEdilParcel.objects.create(unit=unit3, fract_edil_parcel_number=1, material_portion=1)
    print(f"  Unit 3: {unit3.title} (FE)")

    # ─── Unit 4: Unita documentaria (con ICCD) ───
    unit4 = Unit.objects.create(
        fond=fond,
        title="Fotografia - Piazza Palazzo di Citta",
        content="Fotografia storica di Piazza Palazzo di Citta, Torino, ca. 1880.",
        unit_type="unita documentaria",
        sc2_tsk="F",
        physical_type="fotografia",
        medium="albumina/carta",
        reference_number="3",
        extent="1 fotografia",
        created_by=1, updated_by=1,
    )
    iccd = IccdDescription.objects.create(
        unit=unit4,
        denomination="Fotografia",
        object_type="Immagine fissa",
        category="Documentazione fotografica storica",
        age_century="XIX",
    )
    IccdSubject.objects.create(
        iccd_description=iccd,
        subject="Veduta urbana con edifici storici e persone in costume d'epoca.",
    )
    IccdDamage.objects.create(unit=unit4, code="sbiadimento", description="Leggero sbiadimento ai bordi.")
    IccdTechSpec.objects.create(
        unit=unit4,
        mtcm="Carta all'albumina",
        mtct="Stampa all'albumina",
        misa="20 x 30 cm",
    )
    print(f"  Unit 4: {unit4.title} (ICCD)")

    # ─── Relations: Unit <-> Heading, Source, Anagraphic ───
    RelUnitHeading.objects.create(unit=unit1, heading=heading2)
    RelUnitSource.objects.create(unit=unit1, source=source1)
    RelUnitAnagraphic.objects.create(unit=unit2, anagraphic=anagraphic1)
    print("  Relazioni Unit create")

    # ─── Creator relations extra ───
    creator2 = Creator.objects.create(creator_type="P", group=group)
    CreatorName.objects.create(creator=creator2, name="Rossi, Mario", preferred=True, qualifier="A")
    RelCreatorCreator.objects.create(
        creator=creator, related_creator=creator2, association_type="ha come dipendente",
    )
    RelCreatorInstitution.objects.create(creator=creator, institution=institution1)
    print(f"  Creator relations: {creator2} associato a {creator}")

    # ─── Digital Object ───
    from PIL import Image
    import io
    img = Image.new('RGB', (100, 100), color=(73, 109, 137))
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='JPEG')
    img_bytes.seek(0)

    dobj = DigitalObject(
        title="Foto copertina registro", published=True,
        content_type=ContentType.objects.get_for_model(Unit),
        object_id=unit1.pk,
        created_by=1, updated_by=1, group=group,
    )
    dobj.asset.save("copertina_registro.jpg", ContentFile(img_bytes.read()), save=True)
    print(f"  DigitalObject: {dobj.title}")

    print("\nDati di riferimento creati con successo!")
    return fond


def export_xml(exporter, format_type, output_dir):
    """Export XML (SAN/EAD/METS) and save to output_dir."""
    format_labels = {'san': 'CAT-SAN', 'ead': 'ICAR-IMPORT (EAD)', 'mets': 'METS'}
    label = format_labels.get(format_type, format_type.upper())
    print(f"\nEsportazione {label}...")
    zip_bytes = exporter.run_xml_export(format_type)

    out_path = os.path.join(output_dir, f'reference_{format_type}.zip')
    os.makedirs(output_dir, exist_ok=True)
    with open(out_path, 'wb') as f:
        f.write(zip_bytes)

    import zipfile, io
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    names = zf.namelist()
    zf.close()
    print(f"  {label}: {out_path} ({len(zip_bytes)} bytes)")
    print(f"  Contenuto: {names}")
    return out_path


def export_aef(fond, output_path):
    """Esporta il fondo in AEF e salva nel path specificato.

    Genera DUE varianti:
    1. reference_aef.aef — formato NDJSON originale (per Ruby import, estensione .aef)
    2. reference_aef.zip — formato NDJSON (per Python tools)

    Inoltre esporta SAN, EAD, METS XML.
    """
    output_dir = os.path.dirname(output_path) or '.'
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nEsportazione AEF per: {fond.name}")
    exporter = AEFExporter(
        fond_id=fond.pk,
        mode='full',
        include_digital_objects=True,
    )
    zip_bytes = exporter.run()

    # Variante 1: .aef per Ruby (stesso contenuto, estensione diversa)
    aef_path = output_path.replace('.zip', '.aef')
    with open(aef_path, 'wb') as f:
        f.write(zip_bytes)
    print(f"AEF (per Ruby): {aef_path} ({len(zip_bytes)} bytes)")

    # Variante 2: .zip per Python tools
    with open(output_path, 'wb') as f:
        f.write(zip_bytes)
    print(f"AEF (per Python): {output_path} ({len(zip_bytes)} bytes)")

    # Info sul contenuto
    import zipfile, io, json
    zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    data_lines = zf.read('data.json').decode('utf-8').strip().split('\n')
    model_counts = {}
    for line in data_lines:
        if line.strip():
            record = json.loads(line)
            for k in record.keys():
                model_counts[k] = model_counts.get(k, 0) + 1

    print(f"\nContenuto AEF ({len(data_lines)} record totali):")
    for model, count in sorted(model_counts.items()):
        print(f"  {model}: {count}")

    # XML exports
    export_xml(exporter, 'san', output_dir)
    export_xml(exporter, 'ead', output_dir)
    export_xml(exporter, 'mets', output_dir)

    return zip_bytes


def generate_reports_from_aef(aef_path, output_dir):
    """Importa l'AEF in un DB separato e genera PDF/RTF, poi pulisce."""
    import tempfile
    import subprocess

    print(f"\nGenerazione report da AEF: {aef_path}")
    print("  (uso database temporaneo separato per non toccare il DB di produzione)")

    # 1) Crea un DB SQLite temporaneo
    tmp_db = tempfile.NamedTemporaryFile(suffix='.sqlite3', delete=False)
    tmp_db_path = tmp_db.name
    tmp_db.close()

    # 2) Scrivi uno script helper temporaneo
    helper_path = os.path.join(os.path.dirname(__file__), '_tmp_report_gen.py')
    with open(helper_path, 'w') as f:
        f.write(f'''
import os, sys
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "archimista_python.settings")

import django
from django.conf import settings
settings.DATABASES["default"]["NAME"] = "{tmp_db_path}"
django.setup()

from django.core.management import call_command
call_command("migrate", "--run-syncdb", verbosity=0)

# NO seed_db — vogliamo solo i dati dall'AEF

# Disable FK checks for import (legacy IDs differ across DBs)
from django.db import connection
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = OFF")

from archimista_python.archive.import_utils import AEFImporter
importer = AEFImporter("{aef_path}", group_id=1)
importer.run()

# Re-enable FK checks
cursor.execute("PRAGMA foreign_keys = ON")

from archimista_python.archive.models import Fond
fond = Fond.objects.first()
if not fond:
    print("ERRORE: Nessun fondo trovato dopo l'importazione AEF")
    sys.exit(1)
print(f"Fondo importato: {{fond.name}} (ID {{fond.pk}})")

# Genera PDF e RTF
from django.test import RequestFactory
from django.template.loader import render_to_string
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration

from archimista_python.archive.views.reports import (
    _get_fond_subtree,
    ReportSettings, EntityReportSettings,
    project_available_attributes_info, custodian_available_attributes_info,
    creator_available_attributes_info, fond_available_attributes_info,
    unit_available_attributes_info, make_html,
)
from archimista_python.archive.rtf_builder import RtfBuilder
from archimista_python.archive.models import Unit

rf = RequestFactory()
request = rf.get(f"/fonds/{{fond.pk}}/report/")
request.COOKIES = {{}}
request.GET = {{}}

report_settings = ReportSettings(None, "inventory", "Inventario di complesso archivistico", "inventory", None)
report_settings.entity_add(EntityReportSettings("project", project_available_attributes_info(), False))
report_settings.entity_add(EntityReportSettings("custodian", custodian_available_attributes_info(), False))
report_settings.entity_add(EntityReportSettings("creator", creator_available_attributes_info(), False))
report_settings.entity_add(EntityReportSettings("fond", fond_available_attributes_info(), False))
report_settings.entity_add(EntityReportSettings("unit", unit_available_attributes_info(), False))
report_settings.initialize_entities_selected_attribute_names(request.GET, request.COOKIES)

fonds = _get_fond_subtree(fond.pk)
root_fond = fonds[0] if fonds else fond
display_sequence_numbers = Unit.display_sequence_numbers_of(root_fond)

fonds_data = []
for fd in fonds:
    creators_sorted = sorted(list(fd.creators.all()), key=lambda x: x.display_name if hasattr(x, "display_name") else "")
    creators_data = [(c, make_html(report_settings, "creator", c)) for c in creators_sorted]
    custodians_data = [(c, make_html(report_settings, "custodian", c)) for c in fd.custodians.all()]
    projects_data = [(p, make_html(report_settings, "project", p)) for p in fd.projects.all()]
    units_data = []
    for u in fd.units.all():
        seq_num = ""
        if hasattr(u, "display_sequence_number_from_hash"):
            seq_num = u.display_sequence_number_from_hash(display_sequence_numbers)
        units_data.append((u, make_html(report_settings, "unit", u), seq_num))
    fond_html = make_html(report_settings, "fond", fd)
    fonds_data.append({{
        "fond": fd,
        "fond_html": fond_html,
        "creators_data": creators_data,
        "custodians_data": custodians_data,
        "projects_data": projects_data,
        "units_data": units_data,
    }})

context = {{
    "fonds_data": fonds_data,
    "root_fond": root_fond,
    "display_sequence_numbers": display_sequence_numbers,
    "report_settings": report_settings,
}}

html_str = render_to_string("archive/inventory_report.html", context)

# PDF
print("Generazione PDF...")
font_config = FontConfiguration()
css_text = """
@page {{
    size: A4;
    margin: 2.5cm 2cm 2.5cm 2cm;
    @bottom-center {{
        content: "pag. " counter(page) " di " counter(pages);
        font-size: 8pt;
    }}
}}
body {{ font-family: Arial, sans-serif; font-size: 10pt; }}
h2 {{ font-size: 16pt; font-weight: bold; }}
h3 {{ font-size: 14pt; font-weight: bold; }}
h4 {{ font-size: 12pt; font-weight: bold; }}
.fldcaption {{ margin-top: 12px; margin-bottom: 2px; }}
.field-header {{ font-weight: bold; }}
.pbi_avoid {{ page-break-inside: avoid; }}
hr {{ border: none; border-bottom: 1px solid #000; margin: 10px 0; }}
"""
css = CSS(string=css_text, font_config=font_config)

pdf_path = "{output_dir}/python_report.pdf"
pdf_bytes = HTML(string=html_str).write_pdf(stylesheets=[css], font_config=font_config)
with open(pdf_path, "wb") as fout:
    fout.write(pdf_bytes)
print(f"PDF: {{pdf_path}} ({{len(pdf_bytes)}} bytes)")

# RTF
print("Generazione RTF...")
rtf_path = "{output_dir}/python_report.rtf"
builder = RtfBuilder(target_id=fond.pk, dest_file=rtf_path)
builder.build_fond_rtf_file(request.GET, request.COOKIES)
print(f"RTF: {{rtf_path}} ({{os.path.getsize(rtf_path)}} bytes)")

# Pulizia connessioni
from django.db import connection
connection.close()
print("OK")
''')

    # 3) Esegui lo script helper
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'archimista_python.settings'
    result = subprocess.run(
        [sys.executable, helper_path],
        capture_output=True, text=True,
        env=env,
        cwd=os.path.dirname(os.path.abspath(__file__)),
        timeout=120,
    )

    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # 4) Pulizia
    if os.path.exists(tmp_db_path):
        os.unlink(tmp_db_path)
        print(f"  DB temporaneo eliminato: {tmp_db_path}")
    if os.path.exists(helper_path):
        os.unlink(helper_path)

    if result.returncode != 0:
        raise RuntimeError(f"Generazione report fallita (exit {result.returncode})")

    pdf_path = os.path.join(output_dir, 'python_report.pdf')
    rtf_path = os.path.join(output_dir, 'python_report.rtf')
    return pdf_path, rtf_path


def main():
    output_dir = os.path.join(os.path.dirname(__file__), 'tests', 'regression', 'reference')
    output_path = os.path.join(output_dir, 'reference_aef.zip')
    aef_path = os.path.join(output_dir, 'reference_aef.aef')

    clear_reference_data()
    fond = create_reference_data()
    export_aef(fond, output_path)
    generate_reports_from_aef(aef_path, output_dir)

    print(f"\n{'=' * 60}")
    print(f"File generati:")
    print(f"  {aef_path}")
    print(f"  {output_path}")
    print(f"  {os.path.join(output_dir, 'reference_san.zip')}")
    print(f"  {os.path.join(output_dir, 'reference_ead.zip')}")
    print(f"  {os.path.join(output_dir, 'reference_mets.zip')}")
    print(f"  {os.path.join(output_dir, 'python_report.pdf')}")
    print(f"  {os.path.join(output_dir, 'python_report.rtf')}")
    print(f"\nPROSSIMI PASSI:")
    print(f"1. Copia {aef_path} sulla VM VirtualBox")
    print(f"2. Importalo in Archimista Ruby")
    print(f"3. Da Ruby, esporta lo stesso fondo con le opzioni:")
    print(f"   ✅ Includi gli oggetti digitali")
    print(f"   ✅ Includi le entità correlate all'oggetto da esportare")
    print(f"   Salva come:")
    print(f"   - AEF  -> tests/regression/ruby_output/ruby_export.aef")
    print(f"   - PDF  -> tests/regression/ruby_output/ruby_report.pdf")
    print(f"   - RTF  -> tests/regression/ruby_output/ruby_report.rtf")
    print(f"   - SAN  -> tests/regression/ruby_output/ruby_export_san.zip  (opzionale)")
    print(f"   - EAD  -> tests/regression/ruby_output/ruby_export_ead.zip  (opzionale)")
    print(f"4. Esegui: python tests/regression/test_ruby_comparison.py")


if __name__ == '__main__':
    main()
