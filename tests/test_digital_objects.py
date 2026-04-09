"""Test: DigitalObject CRUD — global + nested per entity, file upload, validation, thumbnails."""
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from tests import test, section, client, admin_user
from django.test import Client
from django.urls import reverse


# Re-login for this module
_test_client = Client()
_test_client.force_login(admin_user)


def run():
    section("10a. DigitalObject — global create (file upload)")

    def _test_digital_object_create_get():
        resp = _test_client.get(reverse('archive:digital_object_create'))
        assert resp.status_code == 200
    test("DigitalObject: create GET (global)", _test_digital_object_create_get)

    def _test_digital_object_create_post_valid():
        # Minimal valid JPEG file (1x1 pixel)
        jpeg_data = (
            b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01'
            b'\x00\x00\xff\xdb\x00C\x00\x08\x06\x06\x07\x06\x05\x08\x07\x07'
            b'\x07\t\t\x08\n\x0c\x14\r\x0c\x0b\x0b\x0c\x19\x12\x13\x0f\x14\x1d'
            b'\x1a\x1f\x1e\x1d\x1a\x1c\x1c $.\' ",#\x1c\x1c(7telemarketing7\x1c\x1c'
            b'\xff\xc0\x00\x0b\x08\x00\x01\x00\x01\x01\x01\x11\x00\xff\xc4\x00'
            b'\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00'
            b'\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00'
            b'\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00'
            b'\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81'
            b'\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a'
            b'%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87'
            b'\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6'
            b'\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5'
            b'\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3'
            b'\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa'
            b'\xff\xda\x00\x08\x01\x01\x00\x00?\x00\xfb\xd4\xff\xd9'
        )
        f = SimpleUploadedFile("test_image.jpg", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Test DO Global',
            'description': 'Test description',
            'position': 1,
            'published': True,
            'asset_file': f,
        }, follow=True)
        assert resp.status_code == 200, f"DO create failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.filter(title='Test DO Global').first()
        assert do is not None, "DigitalObject not created"
        assert do.access_token is not None, "access_token not generated"
        assert do.asset_file_name is not None, "asset_file_name not populated"
        assert do.asset_content_type is not None, "asset_content_type not populated"
        assert do.created_by == 1, f"created_by should be 1, got {do.created_by}"
        assert do.updated_by == 1, f"updated_by should be 1, got {do.updated_by}"
    test("DigitalObject: create POST con file JPEG valido", _test_digital_object_create_post_valid)

    def _test_digital_object_create_post_invalid_file_type():
        txt_file = SimpleUploadedFile("test.txt", b"hello world", content_type="text/plain")
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'Invalid DO',
            'asset_file': txt_file,
        })
        # Should fail validation (form error, not 302 redirect)
        assert resp.status_code == 200, f"Expected 200 (form error), got {resp.status_code}"
        assert b'asset_file' in resp.content or resp.context is not None, "Form error not shown"
    test("DigitalObject: create POST con tipo file invalido (rejected)", _test_digital_object_create_post_invalid_file_type)

    def _test_digital_object_create_post_no_file():
        resp = _test_client.post(reverse('archive:digital_object_create'), {
            'title': 'No File DO',
            'description': 'No file',
            'published': True,
        }, follow=True)
        # Should succeed — file is optional (required=False)
        assert resp.status_code == 200
    test("DigitalObject: create POST senza file (allowed)", _test_digital_object_create_post_no_file)

    section("10b. DigitalObject — detail, update, delete")

    def _test_digital_object_detail():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.first()
        if not do:
            jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'
            f = SimpleUploadedFile("detail_test.jpg", jpeg_data, content_type="image/jpeg")
            do = DigitalObject.objects.create(
                title='Detail Test DO', description='Detail desc',
                published=True, created_by=1, updated_by=1,
            )
        resp = _test_client.get(reverse('archive:digital_object_detail', args=[do.pk]))
        assert resp.status_code == 200, f"DO detail failed: {resp.status_code}"
    test("DigitalObject: detail view", _test_digital_object_detail)

    def _test_digital_object_update_get():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.first()
        if not do:
            do = DigitalObject.objects.create(
                title='Update Test DO', published=True, created_by=1, updated_by=1,
            )
        resp = _test_client.get(reverse('archive:digital_object_edit', args=[do.pk]))
        assert resp.status_code == 200, f"DO update GET failed: {resp.status_code}"
    test("DigitalObject: update GET", _test_digital_object_update_get)

    def _test_digital_object_update_post():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.create(
            title='Update POST DO', published=True, created_by=1, updated_by=1,
        )
        resp = _test_client.post(reverse('archive:digital_object_edit', args=[do.pk]), {
            'title': 'Updated DO Title',
            'description': 'Updated description',
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"DO update POST failed: {resp.status_code}"
        do.refresh_from_db()
        assert do.title == 'Updated DO Title', f"Title not updated: {do.title}"
        assert do.updated_by == 1, f"updated_by should be 1, got {do.updated_by}"
    test("DigitalObject: update POST", _test_digital_object_update_post)

    def _test_digital_object_delete_get():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.create(
            title='Delete Test DO', published=True, created_by=1, updated_by=1,
        )
        resp = _test_client.get(reverse('archive:digital_object_delete', args=[do.pk]))
        assert resp.status_code == 200, f"DO delete confirm failed: {resp.status_code}"
    test("DigitalObject: delete confirm GET", _test_digital_object_delete_get)

    def _test_digital_object_delete_post():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.create(
            title='Delete POST DO', published=True, created_by=1, updated_by=1,
        )
        pk = do.pk
        resp = _test_client.post(reverse('archive:digital_object_delete', args=[pk]), follow=True)
        assert resp.status_code == 200
        assert not DigitalObject.objects.filter(pk=pk).exists(), "DigitalObject not deleted"
    test("DigitalObject: delete POST", _test_digital_object_delete_post)

    section("10c. DigitalObject — nested under entities (fond, unit, creator, custodian, source)")

    def _test_nested_digital_object_fond_create():
        from archimista_python.archive.models import Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='DO Fond Test', created_by=1, updated_by=1)

        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'
        f = SimpleUploadedFile("nested_fond.jpg", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:fond_digital_object_create', args=[fond.pk]), {
            'title': 'Fond Nested DO',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"Nested DO fond create failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        from django.contrib.contenttypes.models import ContentType
        do = DigitalObject.objects.filter(
            title='Fond Nested DO',
            content_type=ContentType.objects.get_for_model(Fond),
            object_id=fond.pk,
        ).first()
        assert do is not None, "Nested DigitalObject for fond not created"
    test("DigitalObject: nested create under fond", _test_nested_digital_object_fond_create)

    def _test_nested_digital_object_unit_create():
        from archimista_python.archive.models import Unit, Fond
        fond = Fond.objects.filter(name='Fondo Test Modificato').first()
        if not fond:
            fond = Fond.objects.create(name='DO Unit Fond', created_by=1, updated_by=1)
        unit = Unit.objects.filter(fond=fond).first()
        if not unit:
            unit = Unit.objects.create(title='DO Unit Test', fond=fond, created_by=1, updated_by=1)

        jpeg_data = b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00\xff\xd9'
        f = SimpleUploadedFile("nested_unit.jpg", jpeg_data, content_type="image/jpeg")
        resp = _test_client.post(reverse('archive:unit_digital_object_create', args=[unit.pk]), {
            'title': 'Unit Nested DO',
            'asset_file': f,
            'published': True,
        }, follow=True)
        assert resp.status_code == 200, f"Nested DO unit create failed: {resp.status_code}"

        from archimista_python.archive.models import DigitalObject
        from django.contrib.contenttypes.models import ContentType
        do = DigitalObject.objects.filter(
            title='Unit Nested DO',
            content_type=ContentType.objects.get_for_model(Unit),
            object_id=unit.pk,
        ).first()
        assert do is not None, "Nested DigitalObject for unit not created"
    test("DigitalObject: nested create under unit", _test_nested_digital_object_unit_create)

    def _test_nested_digital_object_creator_list():
        from archimista_python.archive.models import Creator
        creator = Creator.objects.first()
        if not creator:
            creator = Creator.objects.create(creator_type='P', created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:creator_digital_object_list', args=[creator.pk]))
        assert resp.status_code == 200
    test("DigitalObject: nested list under creator", _test_nested_digital_object_creator_list)

    def _test_nested_digital_object_custodian_list():
        from archimista_python.archive.models import Custodian, CustodianType
        ctype, _ = CustodianType.objects.get_or_create(custodian_type='DO Cust Test')
        custodian = Custodian.objects.filter(custodian_type=ctype).first()
        if not custodian:
            custodian = Custodian.objects.create(custodian_type=ctype, created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:custodian_digital_object_list', args=[custodian.pk]))
        assert resp.status_code == 200
    test("DigitalObject: nested list under custodian", _test_nested_digital_object_custodian_list)

    def _test_nested_digital_object_source_list():
        from archimista_python.archive.models import Source
        source = Source.objects.filter(short_title='Fonte Test').first()
        if not source:
            source = Source.objects.create(short_title='DO Source Test', source_type_code='1', created_by=1, updated_by=1)
        resp = _test_client.get(reverse('archive:source_digital_object_list', args=[source.pk]))
        assert resp.status_code == 200
    test("DigitalObject: nested list under source", _test_nested_digital_object_source_list)

    section("10d. DigitalObject — model methods")

    def _test_digital_object_is_image():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject(
            title='Image Test', asset_content_type='image/jpeg',
            created_by=1, updated_by=1,
        )
        assert do.is_image() is True
        do.asset_content_type = 'application/pdf'
        assert do.is_image() is False
    test("DigitalObject: is_image() method", _test_digital_object_is_image)

    def _test_digital_object_is_video():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject(
            title='Video Test', asset_content_type='video/mp4',
            created_by=1, updated_by=1,
        )
        assert do.is_video() is True
        do.asset_content_type = 'image/png'
        assert do.is_video() is False
    test("DigitalObject: is_video() method", _test_digital_object_is_video)

    def _test_digital_object_is_pdf():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject(
            title='PDF Test', asset_content_type='application/pdf',
            created_by=1, updated_by=1,
        )
        assert do.is_pdf() is True
        do.asset_content_type = 'image/jpeg'
        assert do.is_pdf() is False
    test("DigitalObject: is_pdf() method", _test_digital_object_is_pdf)

    def _test_digital_object_access_token_auto_generated():
        from archimista_python.archive.models import DigitalObject
        do = DigitalObject.objects.create(
            title='Token Test', published=True,
            created_by=1, updated_by=1,
        )
        assert do.access_token is not None, "access_token not auto-generated"
        assert len(do.access_token) > 0, "access_token is empty"
    test("DigitalObject: access_token auto-generated on save", _test_digital_object_access_token_auto_generated)

    section("10e. DigitalObject — global list with search")

    def _test_digital_object_list_with_search():
        resp = _test_client.get(reverse('archive:digital_object_list'))
        assert resp.status_code == 200

        resp = _test_client.get(reverse('archive:digital_object_list') + '?q=Test')
        assert resp.status_code == 200
    test("DigitalObject: global list + search", _test_digital_object_list_with_search)
