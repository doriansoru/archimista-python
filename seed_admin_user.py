#!/usr/bin/env python
"""
Crea un singolo utente admin con password temporanea e forza il cambio password al primo accesso.

Uso: python seed_admin_user.py
"""

import os
import sys
import secrets
import string

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'archimista_python.settings')

import django
django.setup()

from django.contrib.auth.models import User
from archimista_python.archive.models import UserProfile


USERNAME = 'admin'
EMAIL = 'admin@archimista.local'

# Genera una password casuale sicura
temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + '!@#$%') for _ in range(12))


def seed_admin_user():
    if User.objects.filter(username=USERNAME).exists():
        user = User.objects.get(username=USERNAME)
        # Reimposta la password e forza il cambio
        profile, _ = UserProfile.objects.get_or_create(user=user)

        if not profile.must_change_password:
            # L'utente ha già cambiato password in passato: la resettiamo
            user.set_password(temp_password)
            user.save()
            profile.must_change_password = True
            profile.save()
            print("=" * 60)
            print(f"  Utente '{USERNAME}' già esistente — Password resettata!")
            print("=" * 60)
            print(f"  Username: {USERNAME}")
            print(f"  Nuova password temporanea: {temp_password}")
            print("=" * 60)
            print("Al prossimo accesso, il sistema richiederà di cambiare la password.")
            print("=" * 60)
        else:
            # L'utente esiste ma non ha ancora cambiato password: mostriamo quella attuale
            print("=" * 60)
            print(f"  Utente '{USERNAME}' già esistente — must_change_password attivo")
            print("=" * 60)
            print(f"  Username: {USERNAME}")
            print(f"  Password temporanea: {temp_password}")
            print("=" * 60)
            print("Nota: la password originale è stata resettata. Usa questa.")
            print("Al primo accesso, il sistema richiederà di cambiarla.")
            print("=" * 60)
        return

    user = User.objects.create_user(
        username=USERNAME,
        email=EMAIL,
        password=temp_password,
        is_staff=True,
        is_superuser=True,
    )

    # Imposta il flag per forzare il cambio password
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.must_change_password = True
    profile.save()

    print("=" * 60)
    print("Utente admin creato con successo!")
    print("=" * 60)
    print(f"  Username: {USERNAME}")
    print(f"  Password temporanea: {temp_password}")
    print("=" * 60)
    print("Al primo accesso, il sistema richiederà di cambiare la password.")
    print("=" * 60)


if __name__ == '__main__':
    seed_admin_user()
