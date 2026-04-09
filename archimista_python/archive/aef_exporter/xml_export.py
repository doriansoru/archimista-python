"""
XML Export for AEF — SAN, EAD, and METS formats.

Mirrors Ruby's stream(), stream_ead(), and stream_mets() methods.
Generates XML files using lxml, then packages into ZIP.
"""

import os
import zipfile
import tempfile
import shutil
from lxml import etree
from datetime import datetime

from .constants import APP_VERSION
from archimista_python.archive.models import (
    Fond, Unit, Creator, Custodian, Source,
    RelCreatorFond, RelCustodianFond, RelProjectFond,
)


def generate_xml_export(exporter, format_type):
    """
    Generate XML export in the specified format.

    Args:
        exporter: AEFExporter instance with populated fond_ids etc.
        format_type: 'san', 'ead', or 'mets'

    Returns:
        bytes: ZIP file content
    """
    tmp_dir = tempfile.mkdtemp(prefix='xml_export_')
    try:
        if format_type == 'san':
            _generate_san_export(exporter, tmp_dir)
        elif format_type == 'ead':
            _generate_ead_export(exporter, tmp_dir)
        elif format_type == 'mets':
            _generate_mets_export(exporter, tmp_dir)
        else:
            raise ValueError(f"Unknown XML format: {format_type}")

        # Package into ZIP
        zip_path = os.path.join(tmp_dir, 'export.zip')
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(tmp_dir):
                for fname in files:
                    if fname == 'export.zip':
                        continue
                    full_path = os.path.join(root, fname)
                    arc_name = os.path.relpath(full_path, tmp_dir)
                    zf.write(full_path, arc_name)

            # Add digital object files if requested
            if exporter.include_digital_objects:
                from .digital_objects import add_digital_objects_to_zip
                add_digital_objects_to_zip(
                    zf, exporter.fond_ids, exporter.unit_ids_collected,
                    exporter.creator_ids, exporter.custodian_ids,
                    exporter.source_ids,
                )

        with open(zip_path, 'rb') as f:
            return f.read()
    finally:
        if tmp_dir and os.path.exists(tmp_dir):
            shutil.rmtree(tmp_dir)


# ─── SAN Export (cat-import format) ─────────────────────────────────────

def _generate_san_export(exporter, out_dir):
    """Generate SAN (cat-import) XML export."""
    # Fonds
    if exporter.fond_ids:
        _san_export_fonds(exporter.fond_ids, out_dir)
    # Creators
    if exporter.creator_id:
        _san_export_creator(exporter.creator_id, out_dir)
    elif exporter.creator_ids:
        _san_export_creators(exporter.creator_ids, out_dir)
    # Custodians
    if exporter.custodian_id:
        _san_export_custodian(exporter.custodian_id, out_dir)
    elif exporter.custodian_ids:
        _san_export_custodians(exporter.custodian_ids, out_dir)
    # Sources
    if exporter.source_id:
        _san_export_source(exporter.source_id, out_dir)
    elif exporter.source_ids:
        _san_export_sources(exporter.source_ids, out_dir)


def _san_export_fonds(fond_ids, out_dir):
    """Export fonds in SAN cat-import format."""
    from archimista_python.archive.models import Fond
    fonda = Fond.objects.filter(pk__in=fond_ids).order_by('id')
    for fond in fonda:
        root = etree.Element(
            '{http://san.mibac.it/cat-import/}catListRecords',
            nsmap={
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
                None: 'http://san.mibac.it/cat-import/',
            }
        )
        _san_cat_header(root)
        _san_cat_record_fond(root, fond)
        _write_xml(root, out_dir, f'complessi_{fond.id}.xml')


def _san_export_creator(creator_id, out_dir):
    """Export a single creator in SAN cat-import format."""
    from archimista_python.archive.models import Creator
    try:
        creator = Creator.objects.get(pk=creator_id)
    except Creator.DoesNotExist:
        return
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={'xsi': 'http://www.w3.org/2001/XMLSchema-instance', None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    _san_cat_record_creator(root, creator)
    _write_xml(root, out_dir, f'soggetto_produttore_{creator_id}.xml')


def _san_export_creators(creator_ids, out_dir):
    """Export multiple creators in SAN cat-import format."""
    from archimista_python.archive.models import Creator
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    for cid in creator_ids:
        try:
            creator = Creator.objects.get(pk=cid)
            _san_cat_record_creator(root, creator)
        except Creator.DoesNotExist:
            pass
    _write_xml(root, out_dir, 'soggetti_produttori.xml')


def _san_export_custodian(custodian_id, out_dir):
    """Export a single custodian in SAN cat-import format."""
    from archimista_python.archive.models import Custodian
    try:
        custodian = Custodian.objects.get(pk=custodian_id)
    except Custodian.DoesNotExist:
        return
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    _san_cat_record_custodian(root, custodian)
    _write_xml(root, out_dir, f'soggetto_conservatore_{custodian_id}.xml')


def _san_export_custodians(custodian_ids, out_dir):
    """Export multiple custodians in SAN cat-import format."""
    from archimista_python.archive.models import Custodian
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    for cid in custodian_ids:
        try:
            custodian = Custodian.objects.get(pk=cid)
            _san_cat_record_custodian(root, custodian)
        except Custodian.DoesNotExist:
            pass
    _write_xml(root, out_dir, 'soggetti_conservatori.xml')


def _san_export_source(source_id, out_dir):
    """Export a single source in SAN cat-import format."""
    from archimista_python.archive.models import Source
    try:
        source = Source.objects.get(pk=source_id)
    except Source.DoesNotExist:
        return
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    _san_cat_record_source(root, source)
    _write_xml(root, out_dir, f'fonte_{source_id}.xml')


def _san_export_sources(source_ids, out_dir):
    """Export multiple sources in SAN cat-import format."""
    from archimista_python.archive.models import Source
    root = etree.Element(
        '{http://san.mibac.it/cat-import/}catListRecords',
        nsmap={None: 'http://san.mibac.it/cat-import/'}
    )
    _san_cat_header(root)
    for sid in source_ids:
        try:
            source = Source.objects.get(pk=sid)
            _san_cat_record_source(root, source)
        except Source.DoesNotExist:
            pass
    _write_xml(root, out_dir, 'fonti.xml')


def _san_cat_header(root):
    """Add catheader element to SAN export."""
    header = etree.SubElement(root, 'catHeader')
    system_id = etree.SubElement(header, 'systemId')
    system_id.text = 'Archimista Python'
    contact = etree.SubElement(header, 'contact')
    name_el = etree.SubElement(contact, 'name')
    name_el.text = 'Admin'
    mail_el = etree.SubElement(contact, 'mail')
    mail_el.text = 'admin@archimista.it'
    filedesc = etree.SubElement(header, 'filedesc')
    title_el = etree.SubElement(filedesc, 'title')
    title_el.text = 'Export Archimista'
    date_el = etree.SubElement(filedesc, 'date')
    date_el.text = datetime.now().strftime('%Y-%m-%d')


def _san_cat_record_fond(root, fond):
    """Add a fond as catRecord in SAN format."""
    cat_record = etree.SubElement(root, 'catRecord')
    header = etree.SubElement(cat_record, 'catRecordHeader')
    header.set('type', 'complesso archivistico')
    rec_id = etree.SubElement(header, 'id')
    rec_id.text = f'CA-{fond.id}'
    update = etree.SubElement(header, 'lastUpdate')
    update.text = datetime.now().strftime('%Y-%m-%d')

    body = etree.SubElement(cat_record, 'catRecordBody')
    ead = etree.SubElement(body, 'ead', attrib={
        'xmlns': 'http://san.mibac.it/ead-san/',
    })
    archdesc = etree.SubElement(ead, 'archdesc')
    if fond.fond_type:
        archdesc.set('otherlevel', fond.fond_type)
        archdesc.set('level', 'otherlevel')
    else:
        archdesc.set('level', 'fonds')

    did = etree.SubElement(archdesc, 'did')
    unitid = etree.SubElement(did, 'unitid')
    unitid.text = f'CA-{fond.id}'
    unittitle = etree.SubElement(did, 'unittitle')
    unittitle.text = fond.name or ''
    if hasattr(fond, 'preferred_event') and fond.preferred_event:
        unitdate = etree.SubElement(did, 'unitdate')
        unitdate.text = str(fond.preferred_event)
    physdesc = etree.SubElement(did, 'physdesc')
    if fond.length:
        extent = etree.SubElement(physdesc, 'extent')
        extent.text = str(fond.length)
    if fond.extent:
        extent2 = etree.SubElement(physdesc, 'extent')
        extent2.text = str(fond.extent)

    if fond.abstract:
        abstract = etree.SubElement(did, 'abstract')
        abstract.text = fond.abstract[:200] if fond.abstract else ''
    elif fond.description:
        abstract = etree.SubElement(did, 'abstract')
        abstract.text = (fond.description or '')[:200]

    # Origination (creators)
    if hasattr(fond, 'creators'):
        for creator in getattr(fond, 'creators', [])[:10]:
            orig = etree.SubElement(did, 'origination')
            orig.text = f'SP-{creator.id}'

    # Repository (custodians)
    if hasattr(fond, 'custodians'):
        for cust in getattr(fond, 'custodians', [])[:10]:
            repo = etree.SubElement(did, 'repository')
            repo.text = f'SC-{cust.id}'

    # Process info
    proc = etree.SubElement(archdesc, 'processinfo')
    pub = etree.SubElement(proc, 'p')
    pub.text = 'Pubblicato' if fond.published else 'Non pubblicato'


def _san_cat_record_creator(root, creator):
    """Add a creator as catRecord in SAN format (EAC-CPF)."""
    cat_record = etree.SubElement(root, 'catRecord')
    header = etree.SubElement(cat_record, 'catRecordHeader')
    header.set('type', 'soggetto produttore')
    rec_id = etree.SubElement(header, 'id')
    rec_id.text = f'SP-{creator.id}'

    body = etree.SubElement(cat_record, 'catRecordBody')
    eac = etree.SubElement(body, 'eac-cpf', attrib={
        'xmlns': 'http://san.mibac.it/eac-san/',
    })
    control = etree.SubElement(eac, 'control')
    record_id = etree.SubElement(control, 'otherRecordId')
    record_id.text = f'SP-{creator.id}'
    status = etree.SubElement(control, 'maintenanceStatus')
    status.text = 'revised'

    cpf = etree.SubElement(eac, 'cpfDescription')
    identity = etree.SubElement(cpf, 'identity')

    # Entity type
    ctype = creator.creator_type or ''
    if ctype == 'P':
        et = etree.SubElement(identity, 'entityType')
        et.text = 'person'
    elif ctype == 'F':
        et = etree.SubElement(identity, 'entityType')
        et.text = 'family'
    else:
        et = etree.SubElement(identity, 'entityType')
        et.text = 'corporateBody'

    # Name entry
    name_entry = etree.SubElement(identity, 'nameEntry')
    pref_name = etree.SubElement(name_entry, 'part')
    # Try to get preferred name
    try:
        pn = creator.creator_names.filter(preferred=True).first()
        if pn:
            if pn.first_name or pn.last_name:
                pref_name.text = f'{pn.first_name} {pn.last_name}'.strip()
            elif pn.name:
                pref_name.text = pn.name
    except Exception:
        pass
    if pref_name.text is None:
        pref_name.text = f'Soggetto produttore {creator.id}'

    description = etree.SubElement(cpf, 'description')
    if creator.residence:
        place = etree.SubElement(description, 'place')
        place.text = str(creator.residence)[:200]

    if creator.abstract:
        bio = etree.SubElement(description, 'biogHist')
        bio.text = str(creator.abstract)[:500]


def _san_cat_record_custodian(root, custodian):
    """Add a custodian as catRecord in SAN format (SCONS)."""
    cat_record = etree.SubElement(root, 'catRecord')
    header = etree.SubElement(cat_record, 'catRecordHeader')
    header.set('type', 'soggetto conservatore')
    rec_id = etree.SubElement(header, 'id')
    rec_id.text = f'SC-{custodian.id}'

    body = etree.SubElement(cat_record, 'catRecordBody')
    scons = etree.SubElement(body, 'scons', attrib={
        'xmlns': 'http://san.mibac.it/scons-san/',
    })

    # Preferred name
    pref_name = etree.SubElement(scons, 'formaautorizzata')
    try:
        pn = custodian.custodian_names.filter(preferred=True).first()
        pref_name.text = pn.name if pn else f'Conservatore {custodian.id}'
    except Exception:
        pref_name.text = f'Conservatore {custodian.id}'

    # Identifier
    ident = etree.SubElement(scons, 'identifier')
    ident.text = f'SC-{custodian.id}'

    # Buildings
    try:
        for building in custodian.custodian_buildings.all()[:10]:
            loc = etree.SubElement(scons, 'localizzazione')
            if building.address:
                addr = etree.SubElement(loc, 'indirizzo')
                addr.text = str(building.address)[:200]
            if building.city:
                city = etree.SubElement(loc, 'citta')
                city.text = str(building.city)[:100]
    except Exception:
        pass

    # Services and accessibility
    if custodian.services:
        srv = etree.SubElement(scons, 'servizi')
        srv.text = str(custodian.services)[:500]
    if custodian.accessibility:
        acc = etree.SubElement(scons, 'altroaccesso')
        acc.text = str(custodian.accessibility)[:500]


def _san_cat_record_source(root, source):
    """Add a source as catRecord in SAN format."""
    cat_record = etree.SubElement(root, 'catRecord')
    header = etree.SubElement(cat_record, 'catRecordHeader')
    header.set('type', 'strumento di ricerca')
    rec_id = etree.SubElement(header, 'id')
    rec_id.text = f'SR-{source.id}'

    body = etree.SubElement(cat_record, 'catRecordBody')
    ead = etree.SubElement(body, 'ead', attrib={
        'xmlns': 'http://san.mibac.it/ricerca-san/',
    })
    eadheader = etree.SubElement(ead, 'eadheader')
    eadid = etree.SubElement(eadheader, 'eadid')
    eadid.text = f'SR-{source.id}'
    filedesc = etree.SubElement(eadheader, 'filedesc')
    titlestmt = etree.SubElement(filedesc, 'titlestmt')
    if source.author:
        author_el = etree.SubElement(titlestmt, 'author')
        author_el.text = str(source.author)[:200]
    if source.title:
        title_el = etree.SubElement(titlestmt, 'titleproper')
        title_el.text = str(source.title)[:200]

    archdesc = etree.SubElement(ead, 'archdesc')
    did = etree.SubElement(archdesc, 'did')
    unitid = etree.SubElement(did, 'unitid')
    unitid.text = f'SR-{source.id}'


def _write_xml(root, out_dir, filename):
    """Write an lxml ElementTree root to an XML file."""
    tree = etree.ElementTree(root)
    tree.write(
        os.path.join(out_dir, filename),
        xml_declaration=True,
        encoding='UTF-8',
        pretty_print=True,
    )


# ─── EAD Export (EAD3 format) ──────────────────────────────────────────

def _generate_ead_export(exporter, out_dir):
    """Generate EAD3 XML export."""
    if exporter.fond_ids:
        _ead_export_fonds(exporter.fond_ids, out_dir)
    if exporter.creator_id:
        _ead_export_creator(exporter.creator_id, out_dir)
    if exporter.custodian_id:
        _ead_export_custodian(exporter.custodian_id, out_dir)
    if exporter.source_id:
        _ead_export_source(exporter.source_id, out_dir)


def _ead_export_fonds(fond_ids, out_dir):
    """Export fonds in EAD3 format."""
    from archimista_python.archive.models import Fond
    fonda = Fond.objects.filter(pk__in=fond_ids).order_by('id')
    for fond in fonda:
        root = etree.Element(
            '{http://ead3.archivists.org/schema/}ead',
            nsmap={
                None: 'http://ead3.archivists.org/schema/',
                'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            }
        )
        _ead_control(root, fond)
        _ead_archdesc(root, fond)
        _write_xml(root, out_dir, f'ead_fond_{fond.id}.xml')


def _ead_export_creator(creator_id, out_dir):
    """Export a creator in EAC-CPF format."""
    from archimista_python.archive.models import Creator
    try:
        creator = Creator.objects.get(pk=creator_id)
    except Creator.DoesNotExist:
        return
    root = etree.Element(
        '{urn:isbn:1-931666-33-4}eac-cpf',
        nsmap={None: 'urn:isbn:1-931666-33-4', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    )
    _ead_cpf_control(root, creator)
    _ead_cpf_description(root, creator)
    _write_xml(root, out_dir, f'ead_creator_{creator_id}.xml')


def _ead_export_custodian(custodian_id, out_dir):
    """Export a custodian in SCONS2 format."""
    from archimista_python.archive.models import Custodian
    try:
        custodian = Custodian.objects.get(pk=custodian_id)
    except Custodian.DoesNotExist:
        return
    root = etree.Element(
        '{http://www.san.beniculturali.it/scons2}scons',
        nsmap={None: 'http://www.san.beniculturali.it/scons2', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    )
    _ead_scons_identification(root, custodian)
    _ead_scons_locations(root, custodian)
    _write_xml(root, out_dir, f'ead_custodian_{custodian_id}.xml')


def _ead_export_source(source_id, out_dir):
    """Export a source in EAD format."""
    from archimista_python.archive.models import Source
    try:
        source = Source.objects.get(pk=source_id)
    except Source.DoesNotExist:
        return
    root = etree.Element(
        '{http://ead3.archivists.org/schema/}ead',
        nsmap={None: 'http://ead3.archivists.org/schema/', 'xsi': 'http://www.w3.org/2001/XMLSchema-instance'}
    )
    _ead_source_control(root, source)
    _write_xml(root, out_dir, f'ead_source_{source_id}.xml')


def _ead_control(root, fond):
    """Add EAD control section."""
    control = etree.SubElement(root, 'control')
    recordid = etree.SubElement(control, 'recordid')
    recordid.text = f'CA-{fond.id}'
    filedesc = etree.SubElement(control, 'filedesc')
    titlestmt = etree.SubElement(filedesc, 'titlestmt')
    titleproper = etree.SubElement(titlestmt, 'titleproper')
    titleproper.text = fond.name or f'Fondo {fond.id}'
    maintenancestatus = etree.SubElement(control, 'maintenancestatus')
    maintenancestatus.text = 'revised'
    maintenanceagency = etree.SubElement(control, 'maintenanceagency')
    agencycode = etree.SubElement(maintenanceagency, 'agencycode')
    agencycode.text = 'Archimista Python'
    languagedeclaration = etree.SubElement(control, 'languagedeclaration')
    lang = etree.SubElement(languagedeclaration, 'language')
    lang.set('langcode', 'it')
    lang.text = 'italiano'


def _ead_archdesc(root, fond):
    """Add EAD archdesc section for a fond."""
    level_map = {
        'archivio': 'fonds', 'fondo': 'fonds', 'subfondo': 'subfonds',
        'serie': 'series', 'sottoserie': 'subseries',
        'fascicolo': 'file', 'unita documentaria': 'item',
    }
    level = level_map.get((fond.fond_type or '').lower(), 'fonds')

    archdesc = etree.SubElement(root, 'archdesc')
    archdesc.set('level', level)
    archdesc.set('id', f'CA-{fond.id}')

    did = etree.SubElement(archdesc, 'did')
    unitid = etree.SubElement(did, 'unitid')
    unitid.text = f'CA-{fond.id}'
    unittitle = etree.SubElement(did, 'unittitle')
    unittitle.text = fond.name or ''

    if fond.length or fond.extent:
        physdesc = etree.SubElement(did, 'physdescstructured', attrib={
            'physdescstructuredtype': 'spaceoccupied',
            'coverage': 'linear',
        })
        if fond.length:
            quantity = etree.SubElement(physdesc, 'quantity')
            quantity.text = str(fond.length)
            unit = etree.SubElement(physdesc, 'unittype')
            unit.text = 'metri lineari'

    if fond.description:
        scopecontent = etree.SubElement(archdesc, 'scopecontent')
        p = etree.SubElement(scopecontent, 'p')
        p.text = str(fond.description)[:500]

    if fond.history:
        custodhist = etree.SubElement(archdesc, 'custodhist')
        p = etree.SubElement(custodhist, 'p')
        p.text = str(fond.history)[:500]


def _ead_cpf_control(root, creator):
    """Add EAC-CPF control section."""
    control = etree.SubElement(root, 'control')
    record_id = etree.SubElement(control, 'recordId')
    record_id.text = f'SP-{creator.id}'
    maintenancestatus = etree.SubElement(control, 'maintenanceStatus')
    maintenancestatus.text = 'revised'
    publicationstatus = etree.SubElement(control, 'publicationStatus')
    publicationstatus.text = 'verified' if creator.published else 'inprocess'
    maintenanceagency = etree.SubElement(control, 'maintenanceAgency')
    agencycode = etree.SubElement(maintenanceagency, 'agencycode')
    agencycode.text = 'Archimista Python'
    languagedeclaration = etree.SubElement(control, 'languageDeclaration')
    lang = etree.SubElement(languagedeclaration, 'language')
    lang.set('langcode', 'it')
    lang.text = 'italiano'


def _ead_cpf_description(root, creator):
    """Add EAC-CPF cpfDescription section."""
    cpf_desc = etree.SubElement(root, 'cpfDescription')
    identity = etree.SubElement(cpf_desc, 'identity')
    identity.set('localType', 'soggettoProduttore')

    ctype = creator.creator_type or ''
    et = etree.SubElement(identity, 'entityType')
    et.text = {'P': 'person', 'F': 'family'}.get(ctype, 'corporateBody')

    name_entry = etree.SubElement(identity, 'nameEntry')
    part = etree.SubElement(name_entry, 'part')
    try:
        pn = creator.creator_names.filter(preferred=True).first()
        if pn:
            part.text = (f'{pn.first_name} {pn.last_name}'.strip() or
                         pn.name or f'Soggetto produttore {creator.id}')
    except Exception:
        part.text = f'Soggetto produttore {creator.id}'

    description = etree.SubElement(cpf_desc, 'description')
    if creator.abstract:
        biog_hist = etree.SubElement(description, 'biogHist')
        p = etree.SubElement(biog_hist, 'p')
        p.text = str(creator.abstract)[:500]


def _ead_scons_identification(root, custodian):
    """Add SCONS2 identification section."""
    info = etree.SubElement(root, 'info')
    date_el = etree.SubElement(info, 'dataEvento')
    date_el.text = datetime.now().strftime('%Y-%m-%d')
    tipo = etree.SubElement(info, 'tipoEvento')
    tipo.text = 'creazione'

    ident = etree.SubElement(root, 'identificativi')
    sistema = etree.SubElement(ident, 'sistema')
    sistema.text = 'Archimista'
    ident_el = etree.SubElement(ident, 'identificativo')
    ident_el.text = f'SC-{custodian.id}'

    # Preferred name
    denom = etree.SubElement(root, 'denominazione')
    nome = etree.SubElement(denom, 'denominazionePrincipale')
    try:
        pn = custodian.custodian_names.filter(preferred=True).first()
        nome.text = pn.name if pn else f'Conservatore {custodian.id}'
    except Exception:
        nome.text = f'Conservatore {custodian.id}'


def _ead_scons_locations(root, custodian):
    """Add SCONS2 locations section."""
    try:
        locations = etree.SubElement(root, 'localizzazioni')
        for building in custodian.custodian_buildings.all()[:10]:
            loc = etree.SubElement(locations, 'localizzazione')
            indirizzo = etree.SubElement(loc, 'indirizzo')
            if building.address:
                den_str = etree.SubElement(indirizzo, 'denominazioneStradale')
                den_str.text = str(building.address)[:200]
            if building.city:
                comune = etree.SubElement(indirizzo, 'comune')
                comune.text = str(building.city)[:100]
    except Exception:
        pass


def _ead_source_control(root, source):
    """Add EAD control section for a source."""
    control = etree.SubElement(root, 'control')
    recordid = etree.SubElement(control, 'recordid')
    recordid.text = f'SR-{source.id}'
    filedesc = etree.SubElement(control, 'filedesc')
    titlestmt = etree.SubElement(filedesc, 'titlestmt')
    if source.author:
        author_el = etree.SubElement(titlestmt, 'author')
        author_el.text = str(source.author)[:200]
    if source.title:
        titleproper = etree.SubElement(titlestmt, 'titleproper')
        titleproper.text = str(source.title)[:200]
    maintenancestatus = etree.SubElement(control, 'maintenancestatus')
    maintenancestatus.text = 'revised'


# ─── METS Export (Digital Objects) ──────────────────────────────────────

def _generate_mets_export(exporter, out_dir):
    """Generate METS XML for digital objects."""
    from archimista_python.archive.models import DigitalObject
    from django.contrib.contenttypes.models import ContentType

    envelope_ns = 'http://san.beniculturali.it/envelope-san/'
    mets_ns = 'http://www.loc.gov/mets/'

    envelope = etree.Element(
        '{%s}envelope' % envelope_ns,
        nsmap={
            None: envelope_ns,
            'mets': mets_ns,
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance',
        }
    )
    envelope.set('CREATED', datetime.now().isoformat())
    header = etree.SubElement(envelope, '{%s}header' % envelope_ns)
    source_el = etree.SubElement(header, '{%s}source' % envelope_ns)
    source_el.text = 'Archimista Python'

    record_list = etree.SubElement(envelope, '{%s}recordList' % envelope_ns)

    # Collect digital objects for all entity types
    entity_map = [
        (Fond, exporter.fond_ids),
        (Unit, exporter.unit_ids_collected),
        (Creator, exporter.creator_ids),
        (Custodian, exporter.custodian_ids),
        (Source, exporter.source_ids),
    ]

    for model_class, ids in entity_map:
        if not ids:
            continue
        ct = ContentType.objects.get_for_model(model_class)
        dobjects = DigitalObject.objects.filter(content_type_id=ct.id, object_id__in=ids)
        for dobj in dobjects:
            _mets_record(record_list, dobj, model_class)

    _write_xml(envelope, out_dir, 'digital_objects_mets.xml')


def _mets_record(record_list, dobj, model_class):
    """Add a single digital object as a METS record."""
    record = etree.SubElement(record_list, 'record')
    record.set('directive', 'UPSERT')

    header = etree.SubElement(record, 'recordHeader')
    identifier = etree.SubElement(header, 'recordIdentifier')
    identifier.text = f'DO-{dobj.id}'

    body = etree.SubElement(record, 'recordBody')
    mets_el = etree.SubElement(body, '{http://www.loc.gov/mets/}mets')

    # Header
    mets_hdr = etree.SubElement(mets_el, '{http://www.loc.gov/mets/}metsHdr')
    mets_hdr.set('CREATEDATE', datetime.now().isoformat())
    mets_hdr.set('RECORDSTATUS', 'Complete')

    # Creator agent
    agent = etree.SubElement(
        mets_hdr, '{http://www.loc.gov/mets/}agent',
        attrib={'TYPE': 'ORGANIZATION', 'ROLE': 'CREATOR'},
    )
    name_el = etree.SubElement(agent, '{http://www.loc.gov/mets/}name')
    name_el.text = 'Archimista Python'

    # File section
    file_sec = etree.SubElement(mets_el, '{http://www.loc.gov/mets/}fileSec')
    if dobj.access_token:
        file_grp = etree.SubElement(
            file_sec, '{http://www.loc.gov/mets/}fileGrp',
            attrib={'USE': 'reference image'},
        )
        file_el = etree.SubElement(
            file_grp, '{http://www.loc.gov/mets/}file',
            attrib={'ID': f'file_{dobj.id}'},
        )
        flocat = etree.SubElement(
            file_el, '{http://www.loc.gov/mets/}FLocat',
            attrib={
                '{http://www.w3.org/1999/xlink}href':
                    f'digital_objects/{dobj.access_token}/{dobj.asset_file_name or dobj.asset.name if dobj.asset else ""}',
                'LOCTYPE': 'URL',
            }
        )
