#!/usr/bin/env python
"""
Script per pulire i vocabolari da termini duplicati/non originali.
Mantiene SOLO i termini originali di Archimista Ruby.

STATUS: Eseguito il 2026-04-02
- Eliminati 53 termini non-Ruby + 8 duplicati
- Vocabolari puliti: unit_damages.code (23), units.preservation (6), 
  units.unit_type (3), units.physical_type (21), units.medium (6)

Esegue la pulizia dei seguenti vocabolari:
- unit_damages.code (deve avere 23 termini Ruby)
- units.preservation (deve avere 6 termini Ruby)
- units.unit_type (deve avere 3 termini Ruby)
- units.physical_type (deve avere 21 termini Ruby)
- units.medium (deve avere 6 termini Ruby)

Utilizzo:
    python clean_vocabularies.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')
django.setup()

from archimista_python.archive.models import Term, Vocabulary

# Termini originali Ruby per ogni vocabolario
# Solo questi devono rimanere
RUBY_TERMS = {
    'unit_damages.code': [
        'humidity', 'flood', 'rodents', 'insects', 'fire',
        'laceration', 'stain', 'mutilation', 'perforation', 'folds',
        'discoloration', 'crease', 'fragile', 'funghi_e_batteri', 'strappi',
        'fogli_staccati', 'ingiallimento', 'lacune', 'sbiadimento', 'dispersione',
        'acidita', 'usura', 'rottura_cuciture',
    ],
    'units.preservation': [
        'excellent', 'good', 'discreet', 'mediocre', 'bad', 'very_bad',
    ],
    'units.unit_type': [
        'list', 'file', 'item',
    ],
    'units.physical_type': [
        'album', 'busta', 'cartella', 'faldone', 'fascicolo',
        'filza', 'foglio', 'manifesto', 'mappa', 'mazzo',
        'opuscolo', 'pacco', 'plico', 'quaderno', 'registro',
        'rivista', 'rotolo', 'scatola', 'scheda', 'taccuino',
        'volume',
    ],
    'units.medium': [
        'paper', 'parchment', 'linen_paper', 'cardboard', 'film', 'other',
    ],
}

def clean_vocabulary(vocab_name, ruby_keys):
    """Elimina termini non presenti nella lista Ruby originale."""
    try:
        vocab = Vocabulary.objects.get(name=vocab_name)
    except Vocabulary.DoesNotExist:
        print(f"⚠️  Vocabolario non trovato: {vocab_name}")
        return 0
    
    # Trova tutti i termini del vocabolario
    all_terms = Term.objects.filter(vocabulary=vocab)
    total = all_terms.count()
    
    # Trova i termini da eliminare (quelli NON nella lista Ruby)
    to_delete = []
    to_keep = []
    
    for term in all_terms:
        # Estrai la chiave dal term_key (es. "unit_damages.code.lacune" -> "lacune")
        key_parts = term.term_key.split('.')
        actual_key = key_parts[-1] if key_parts else term.term_key
        
        if actual_key in ruby_keys:
            to_keep.append(term.term_value)
        else:
            to_delete.append((term.id, term.term_key, term.term_value))
    
    # Elimina i termini non Ruby
    deleted_count = 0
    if to_delete:
        print(f"\n🗑️  {vocab_name}:")
        print(f"   Totale termini: {total}")
        print(f"   Da mantenere: {len(to_keep)}")
        print(f"   Da eliminare: {len(to_delete)}")
        print(f"   Termini da eliminare:")
        for term_id, key, value in to_delete:
            print(f"     - {key} => {value}")
            Term.objects.filter(id=term_id).delete()
            deleted_count += 1
    else:
        print(f"✓ {vocab_name}: Nessun termine da eliminare ({len(to_keep)} termini Ruby)")
    
    return deleted_count

def main():
    print("=" * 60)
    print("PULIZIA VOCABOLARI - Mantieni solo termini Ruby originali")
    print("=" * 60)
    
    total_deleted = 0
    
    for vocab_name, ruby_keys in RUBY_TERMS.items():
        deleted = clean_vocabulary(vocab_name, ruby_keys)
        total_deleted += deleted
    
    print("\n" + "=" * 60)
    print(f"TOTALE termini eliminati: {total_deleted}")
    print("=" * 60)
    
    # Verifica finale
    print("\nVerifica finale:")
    for vocab_name, ruby_keys in RUBY_TERMS.items():
        try:
            vocab = Vocabulary.objects.get(name=vocab_name)
            count = Term.objects.filter(vocabulary=vocab).count()
            expected = len(ruby_keys)
            status = "✓" if count == expected else "⚠️"
            print(f"  {status} {vocab_name}: {count}/{expected} termini")
        except Vocabulary.DoesNotExist:
            print(f"  ⚠️  {vocab_name}: VOCABOLARIO NON TROVATO")

if __name__ == '__main__':
    main()
