from django.core.management.base import BaseCommand
from archimista_python.archive.models import Group, Fond, Unit, Creator, Custodian, CreatorCorporateType, CustodianType

class Command(BaseCommand):
    help = 'Popola il database con dati mock archivistici per i test della UI'

    def handle(self, *args, **kwargs):
        self.stdout.write("Avvio del popolamento dati...")

        # Pulisci il DB
        Group.objects.all().delete()
        Fond.objects.all().delete()
        
        # 1. Crea Gruppo
        group = Group.objects.create(name="Archivio Storico Comunale", short_name="ASC")

        # 2. Crea Tipi
        corp_type = CreatorCorporateType.objects.create(corporate_type="Ente Pubblico")
        cust_type = CustodianType.objects.create(custodian_type="Archivio di Stato")

        # 3. Creator & Custodian
        creator = Creator.objects.create(
            creator_type="E", 
            creator_corporate_type=corp_type, 
            abstract="Comune storico fondato nel XII secolo.",
            group=group
        )
        
        custodian = Custodian.objects.create(
            custodian_type=cust_type,
            owner="Ministero dei Beni Culturali",
            group=group
        )

        # 4. Fondi
        fond1 = Fond.objects.create(
            name="Fondo Deliberazioni Comunali",
            fond_type="Fondo",
            abstract="Raccolta delle deliberazioni storiche dal 1800 al 1950.",
            history="Versato nel 1960 dal Comune.",
            group=group,
            position=1
        )

        fond2 = Fond.objects.create(
            name="Raccolta Fotografica Cuneo",
            fond_type="Raccolta",
            abstract="Fotografie della città di Cuneo nel XX secolo.",
            group=group,
            position=2
        )

        # 5. Unita' Radice e Figli
        unit1 = Unit.objects.create(
            fond=fond1,
            title="Delibere della Giunta 1850",
            unit_type="Fascicolo",
            reference_number="Busta 1, Fasc. 1",
            content="Verbali delle sedute della giunta comunale dell'anno 1850.",
            position=1
        )

        unit2 = Unit.objects.create(
            fond=fond1,
            title="Delibere della Giunta 1851",
            unit_type="Fascicolo",
            reference_number="Busta 1, Fasc. 2",
            content="Verbali delle sedute della giunta comunale dell'anno 1851.",
            position=2
        )

        unit3 = Unit.objects.create(
            fond=fond2,
            title="Piazza Galimberti (1920)",
            unit_type="Fotografia",
            reference_number="Foto 1",
            content="Stampa alla gelatina bromuro d'argento.",
            position=1
        )

        self.stdout.write(self.style.SUCCESS('Completato! Dati mock inseriti con successo.'))
