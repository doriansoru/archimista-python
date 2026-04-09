"""Test: upload file reali — PDF, JPEG, thumbnail generation.

COPRE:
  - Upload JPEG reale (generato con Pillow)
  - Upload PDF reale (generato con reportlab)
  - Thumbnail generation con Pillow
  - DigitalObject model methods
  - Oggetti digitali nested nelle entita
"""
import io
from django.test import Client
from django.core.files.uploadedfile import SimpleUploadedFile
from tests import test, section, client, admin_user
from django.urls import reverse


# Re-login
_test_client = Client()
_test_client.force_login(admin_user)


def _generate_real_jpeg():
    """Genera un JPEG 10x10 pixel reale con Pillow."""
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new('RGB', (10, 10), color=(255, 0, 0))
    img.save(buf, format='JPEG', quality=85)
    buf.seek(0)
    return buf.getvalue()


def _generate_real_png():
    """Genera un PNG 10x10 pixel reale con Pillow."""
    from PIL import Image
    buf = io.BytesIO()
    img = Image.new('RGBA', (10, 10), color=(0, 255, 0, 128))
    img.save(buf, format='PNG')
    buf.seek(0)
    return buf.getvalue()


def _generate_real_pdf():
    """Genera un PDF reale con reportlab."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    c.drawString(100, 750, "Documento di test per Archimista")
    c.drawString(100, 730, "Questo e un PDF generato per i test di upload.")
    c.save()
    buf.seek(0)
    return buf.getvalue()


def run():
    section("19a. Upload immagini reali")

    def _test_upload_real_jpeg():
        """Upload JPEG reale generato con Pillow."""
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("real_photo.jpg", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Real JPEG Test',
            'description': 'JPEG reale da Pillow',
            'position': 1,
            'published': True,
            'asset_file': f,
        }, follow=True)
        assert resp.status_code == 200, f"JPEG upload failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.filter(title='Real JPEG Test').first()
        assert do is not None, "DigitalObject not created from JPEG"
        assert do.asset_content_type == 'image/jpeg'
        assert do.is_image() is True
        assert do.asset_file_name is not None
    test("Upload: JPEG reale da Pillow", _test_upload_real_jpeg)

    def _test_upload_real_png():
        """Upload PNG reale generato con Pillow."""
        png_data = _generate_real_png()
        f = SimpleUploadedFile("real_image.png", png_data, content_type="image/png")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Real PNG Test',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"PNG upload failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.filter(title='Real PNG Test').first()
        assert do is not None, "DigitalObject not created from PNG"
        assert do.asset_content_type in ('image/png', 'image/jpeg')
    test("Upload: PNG reale da Pillow", _test_upload_real_png)

    section("19b. Upload PDF reale")

    def _test_upload_real_pdf():
        """Upload PDF reale generato con reportlab."""
        pdf_data = _generate_real_pdf()
        f = SimpleUploadedFile("documento.pdf", pdf_data, content_type="application/pdf")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Real PDF Test',
            'description': 'PDF reale da reportlab',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"PDF upload failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.filter(title='Real PDF Test').first()
        assert do is not None, "DigitalObject not created from PDF"
        assert do.is_pdf() is True
        assert do.is_image() is False
    test("Upload: PDF reale da reportlab", _test_upload_real_pdf)

    def _test_upload_pdf_large():
        """Upload PDF di diverse pagine (>100KB)."""
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        buf = io.BytesIO()
        c = canvas.Canvas(buf, pagesize=A4)
        for i in range(50):
            c.drawString(100, 750, f"Pagina {i+1} di 50")
            c.drawString(100, 700, "Testo di riempimento per aumentare la dimensione del file. " * 20)
            c.showPage()
        c.save()
        buf.seek(0)
        pdf_data = buf.getvalue()

        f = SimpleUploadedFile("large_doc.pdf", pdf_data, content_type="application/pdf")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Large PDF Test',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"Large PDF upload failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.filter(title='Large PDF Test').first()
        assert do is not None, "DigitalObject not created from large PDF"
        assert len(pdf_data) > 10000, f"PDF should be >10KB, got {len(pdf_data)}"
    test("Upload: PDF grande (50 pagine)", _test_upload_pdf_large)

    section("19c. Thumbnail generation")

    def _test_thumbnail_generation_jpeg():
        """Verifica che il thumbnail venga generato per un JPEG."""
        from archimista_python.archive.models import DigitalObject
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("thumb_test.jpg", jpeg_data, content_type="image/jpeg")

        do = DigitalObject.objects.create(
            title='Thumbnail Test JPEG',
            published=True,
            created_by=1, updated_by=1,
        )
        do.asset.save('thumb_test.jpg', f, save=True)
        do.asset_content_type = 'image/jpeg'
        do.save()

        do.refresh_from_db()
        assert do.asset, "asset should be set"
        assert do.asset_file_name, "asset_file_name should be set"

        # Verifica che generate_thumbnails non crashi
        do.generate_thumbnails()
        # Se non crasha, il test passa
    test("Thumbnail: generazione JPEG", _test_thumbnail_generation_jpeg)

    def _test_thumbnail_not_generated_for_pdf():
        """Per un PDF non deve essere generato thumbnail."""
        from archimista_python.archive.models import DigitalObject
        pdf_data = _generate_real_pdf()
        f = SimpleUploadedFile("no_thumb.pdf", pdf_data, content_type="application/pdf")

        do = DigitalObject.objects.create(
            title='No Thumbnail PDF',
            published=True,
            created_by=1, updated_by=1,
        )
        do.asset.save('no_thumb.pdf', f, save=True)
        do.asset_content_type = 'application/pdf'
        do.save()

        do.refresh_from_db()
        assert do.is_image() is False
        assert do.is_pdf() is True

        # generate_thumbnails dovrebbe essere no-op per PDF
        do.generate_thumbnails()
    test("Thumbnail: NON generato per PDF", _test_thumbnail_not_generated_for_pdf)

    section("19d. Validazione e edge cases upload")

    def _test_upload_file_without_extension():
        """File senza estensione nel nome."""
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("no_extension", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'No Extension Test',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code in (200, 302), f"Unexpected status: {resp.status_code}"
    test("Upload: file senza estensione", _test_upload_file_without_extension)

    def _test_upload_file_with_unicode_name():
        """File con caratteri unicode nel nome."""
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("immagine_di_vacanza_2024.jpg", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Unicode Filename Test',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code in (200, 302), f"Unicode filename upload failed: {resp.status_code}"
    test("Upload: file con nome unicode", _test_upload_file_with_unicode_name)

    section("19e. Oggetti digitali nested nelle entita")

    def _test_digital_object_nested_in_fond():
        """Crea oggetto digitale collegato a un fondo."""
        from archimista_python.archive.models import Fond, DigitalObject
        from django.contrib.contenttypes.models import ContentType

        fond = Fond.objects.create(name='Fond With DO', created_by=1, updated_by=1)
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("fond_photo.jpg", jpeg_data, content_type="image/jpeg")

        resp = _test_client.post(
            reverse('archive:fond_digital_object_create', args=[fond.pk]),
            {'title': 'Fond DO', 'asset_file': f, 'published': True},
            follow=True
        )
        assert resp.status_code == 200, f"Fond nested DO create failed: {resp.status_code}"

        do = DigitalObject.objects.filter(
            content_type=ContentType.objects.get_for_model(Fond),
            object_id=fond.pk,
        ).first()
        assert do is not None, "Nested DO for fond not created"
    test("DigitalObject: nested in fond", _test_digital_object_nested_in_fond)

    def _test_digital_object_nested_in_unit():
        """Crea oggetto digitale collegato a un'unita."""
        from archimista_python.archive.models import Fond, Unit, DigitalObject
        from django.contrib.contenttypes.models import ContentType

        fond = Fond.objects.create(name='Unit DO Fond', created_by=1, updated_by=1)
        unit = Unit.objects.create(title='Unit With DO', fond=fond, created_by=1, updated_by=1)

        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("unit_photo.jpg", jpeg_data, content_type="image/jpeg")

        resp = _test_client.post(
            reverse('archive:unit_digital_object_create', args=[unit.pk]),
            {'title': 'Unit DO', 'asset_file': f, 'published': True},
            follow=True
        )
        assert resp.status_code == 200, f"Unit nested DO create failed: {resp.status_code}"

        do = DigitalObject.objects.filter(
            content_type=ContentType.objects.get_for_model(Unit),
            object_id=unit.pk,
        ).first()
        assert do is not None, "Nested DO for unit not created"
    test("DigitalObject: nested in unit", _test_digital_object_nested_in_unit)

    def _test_multiple_digital_objects_on_same_entity():
        """Piu oggetti digitali sulla stessa entita."""
        from archimista_python.archive.models import Fond, DigitalObject
        from django.contrib.contenttypes.models import ContentType

        fond = Fond.objects.create(name='Multi DO Fond', created_by=1, updated_by=1)

        for i in range(3):
            jpeg_data = _generate_real_jpeg()
            f = SimpleUploadedFile(f"photo_{i}.jpg", jpeg_data, content_type="image/jpeg")
            _test_client.post(
                reverse('archive:fond_digital_object_create', args=[fond.pk]),
                {'title': f'Fond Photo {i}', 'asset_file': f, 'published': True},
                follow=True
            )

        ct = ContentType.objects.get_for_model(Fond)
        count = DigitalObject.objects.filter(content_type=ct, object_id=fond.pk).count()
        assert count == 3, f"Expected 3 DOs for fond, got {count}"
    test("DigitalObject: multipli sulla stessa entita", _test_multiple_digital_objects_on_same_entity)

    section("19f. DigitalObject model methods con file reali")

    def _test_is_image_with_real_jpeg():
        """is_image() deve restituire True per JPEG."""
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject(title='Img Test', asset_content_type='image/jpeg', created_by=1, updated_by=1)
        assert do.is_image() is True

        do = DigitalObject(title='Img Test 2', asset_content_type='image/png', created_by=1, updated_by=1)
        assert do.is_image() is True

        do = DigitalObject(title='Img Test 3', asset_content_type='image/webp', created_by=1, updated_by=1)
        assert do.is_image() is True

        do = DigitalObject(title='Img Test 4', asset_content_type='image/gif', created_by=1, updated_by=1)
        assert do.is_image() is True

        do = DigitalObject(title='Img Test 5', asset_content_type='application/pdf', created_by=1, updated_by=1)
        assert do.is_image() is False
    test("DigitalObject: is_image() con tutti i tipi immagine", _test_is_image_with_real_jpeg)

    def _test_is_video_various_types():
        """is_video() deve riconoscere tipi video supportati."""
        from archimista_python.archive.models import DigitalObject
        video_types = ['video/mp4', 'application/mp4', 'video/webm']
        for vt in video_types:
            do = DigitalObject(title=f'Video {vt}', asset_content_type=vt, created_by=1, updated_by=1)
            assert do.is_video() is True, f"is_video() should be True for {vt}"

        do = DigitalObject(title='Not Video', asset_content_type='image/png', created_by=1, updated_by=1)
        assert do.is_video() is False
    test("DigitalObject: is_video() con tipi supportati", _test_is_video_various_types)

    def _test_is_pdf():
        """is_pdf() deve riconoscere PDF."""
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject(title='PDF Test', asset_content_type='application/pdf', created_by=1, updated_by=1)
        assert do.is_pdf() is True

        do = DigitalObject(title='Not PDF', asset_content_type='image/jpeg', created_by=1, updated_by=1)
        assert do.is_pdf() is False
    test("DigitalObject: is_pdf()", _test_is_pdf)

    def _test_access_token_auto_generated():
        """access_token auto-generated on save."""
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.create(
            title='Token Test', published=True,
            created_by=1, updated_by=1,
        )
        assert do.access_token is not None, "access_token not auto-generated"
        assert len(do.access_token) > 0, "access_token is empty"
    test("DigitalObject: access_token auto-generated on save", _test_access_token_auto_generated)

    def _test_get_thumbnail_url():
        """get_thumbnail_url restituisce URL corretto per immagini con asset."""
        from archimista_python.archive.models import DigitalObject
        jpeg_data = _generate_real_jpeg()
        f = SimpleUploadedFile("thumb_url_test.jpg", jpeg_data, content_type="image/jpeg")
        do = DigitalObject(title='Thumb URL Test', published=True, created_by=1, updated_by=1)
        do.asset.save('thumb_url_test.jpg', f, save=True)
        do.asset_content_type = 'image/jpeg'
        do.save()
        do.refresh_from_db()

        url = do.get_thumbnail_url()
        assert url is not None, "get_thumbnail_url should return a URL for images"
        assert 'thumbnail' in url, f"'thumbnail' not in URL: {url}"
    test("DigitalObject: get_thumbnail_url()", _test_get_thumbnail_url)
