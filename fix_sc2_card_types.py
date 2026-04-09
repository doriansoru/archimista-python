#!/usr/bin/env python
"""
Script per aggiornare card_type delle schede SC2 esistenti.
Per le schede con card_type='SC2' o vuoto, determina il tipo corretto
in base ai campi compilati.

Utilizzo:
    python fix_sc2_card_types.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()

from archimista_python.archive.models import Sc2

def fix_sc2_card_types():
    print("=" * 60)
    print("FIX SC2 CARD TYPES")
    print("=" * 60)

    # Trova tutte le schede SC2 con card_type vuoto o 'SC2'
    sc2_cards = Sc2.objects.filter(card_type__in=['', 'SC2', None])
    
    if not sc2_cards.exists():
        print("\nNessuna scheda SC2 da aggiornare.")
        return

    print(f"\nTrovate {sc2_cards.count()} schede SC2 da verificare.")
    
    updated = 0
    for sc2 in sc2_cards:
        # Determina il tipo in base ai campi compilati
        # Fotografia (F): ha lrc (luogo ripresa) o lrd (data ripresa)
        if sc2.lrc or sc2.lrd:
            sc2.card_type = 'F'
            sc2.save()
            updated += 1
            print(f"  ✓ Scheda {sc2.pk} ({sc2.unit}) → F (Fotografia)")
            continue
        
        # Disegno Tecnico (DT): ha dpgf (numero tavola) o cmmr (numero commessa)
        if sc2.dpgf or sc2.cmmr:
            sc2.card_type = 'DT'
            sc2.save()
            updated += 1
            print(f"  ✓ Scheda {sc2.pk} ({sc2.unit}) → DT (Disegno Tecnico)")
            continue
        
        # Cartografia (CARS): ha sdts (rappresentazione tematica) o ort (orientamento)
        if sc2.sdts or sc2.ort:
            sc2.card_type = 'CARS'
            sc2.save()
            updated += 1
            print(f"  ✓ Scheda {sc2.pk} ({sc2.unit}) → CARS (Cartografia)")
            continue
        
        # Se ha solo sdtt (tipo rappresentazione), potrebbe essere D (Disegno artistico)
        if sc2.sdtt:
            sc2.card_type = 'D'
            sc2.save()
            updated += 1
            print(f"  ✓ Scheda {sc2.pk} ({sc2.unit}) → D (Disegno Artistico)")
            continue
        
        # Se ha solo sgti (soggetto iconografico), potrebbe essere S (Stampa)
        if sc2.sgti:
            sc2.card_type = 'S'
            sc2.save()
            updated += 1
            print(f"  ✓ Scheda {sc2.pk} ({sc2.unit}) → S (Stampa)")
            continue
        
        # Se ha solo misa/misl (misure), non possiamo determinare
        print(f"  ⚠ Scheda {sc2.pk} ({sc2.unit}) → Impossibile determinare il tipo")

    print(f"\n{'=' * 60}")
    print(f"Aggiornate {updated} schede su {sc2_cards.count()} trovate.")
    print(f"{'=' * 60}")

if __name__ == '__main__':
    fix_sc2_card_types()
