#!/usr/bin/env python
"""Seed script per popolare la tabella source_types con i dati esatti da Ruby.

Fonte: db/seeds/source_types.json di Archimista Ruby.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()

from archimista_python.archive.models import SourceType

# Dati esatti da Ruby db/seeds/source_types.json
SOURCE_TYPES_DATA = [
    # Root types
    (1, 'bibliografia', None, 1),
    (2, 'strumento di corredo', None, 2),
    (3, 'fonte archivistica', None, 3),
    (4, 'fonte normativa', None, 4),
    # Bibliografia children
    (1001, 'libro', 1, 1),
    (1002, 'capitolo di libro', 1, 2),
    (1003, 'articolo di rivista', 1, 3),
    (1004, 'atti di convegno', 1, 4),
    (1005, 'intervento in convegno', 1, 5),
    (1006, 'altro', 1, 6),
    # Strumento di corredo children
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


def seed():
    print("Seed source_types...")
    created = 0
    updated = 0
    for code, name, parent, pos in SOURCE_TYPES_DATA:
        obj, is_new = SourceType.objects.update_or_create(
            code=code,
            defaults={
                'source_type': name,
                'parent_code': parent,
                'position': pos,
            }
        )
        if is_new:
            created += 1
        else:
            updated += 1

    print(f"  Creati: {created}, Aggiornati: {updated}")
    print(f"  Totale: {SourceType.objects.count()} record")

    print("\nTipologie root:")
    for st in SourceType.objects.filter(parent_code__isnull=True).order_by('position'):
        print(f"  {st.code}: {st.source_type}")

    print("\nSottotipologie:")
    for parent in SourceType.objects.filter(parent_code__isnull=True).order_by('position'):
        children = list(SourceType.objects.filter(parent_code=parent.code).order_by('position'))
        if children:
            print(f"  {parent.source_type}:")
            for ch in children:
                print(f"    {ch.code}: {ch.source_type}")


if __name__ == '__main__':
    seed()
