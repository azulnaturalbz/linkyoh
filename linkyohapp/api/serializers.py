import json
import re

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from linkyohapp.image_utils import ImageValidationError, validate_image
from linkyohapp.models import (
    Category,
    District,
    Gig,
    GigContact,
    GigServiceArea,
    ImportedGigSource,
    Location,
    SubCategory,
)


def normalize_phone_number(value):
    if not value:
        return ''
    raw_value = str(value).strip()
    digits = re.sub(r'\D+', '', raw_value)
    if raw_value.startswith('+'):
        return '+' + digits
    if len(digits) == 7:
        return '+501' + digits
    if len(digits) == 10 and digits.startswith('501'):
        return '+' + digits
    return raw_value


def parse_json_list(value, field_name):
    if value in (None, ''):
        return []
    if isinstance(value, str):
        try:
            value = json.loads(value)
        except ValueError:
            raise serializers.ValidationError({field_name: 'Must be valid JSON.'})
    if not isinstance(value, list):
        raise serializers.ValidationError({field_name: 'Must be a list.'})
    return value


class ImportedGigSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=500)
    description = serializers.CharField(max_length=1000)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
    )
    sub_category_id = serializers.PrimaryKeyRelatedField(
        queryset=SubCategory.objects.select_related('category'),
        source='sub_category',
        write_only=True,
    )
    district_id = serializers.PrimaryKeyRelatedField(
        queryset=District.objects.all(),
        source='district',
        write_only=True,
    )
    location_id = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.select_related('local__local_district'),
        source='location',
        write_only=True,
    )
    address_1 = serializers.CharField(max_length=128)
    address_2 = serializers.CharField(max_length=128, required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=17, required=False, allow_blank=True)
    price = serializers.IntegerField(required=False, default=-1)
    call_for_pricing = serializers.BooleanField(required=False, default=True)
    status = serializers.BooleanField(required=False, default=True)
    source_url = serializers.URLField(max_length=500, required=False, allow_blank=True)
    source_notes = serializers.CharField(required=False, allow_blank=True)
    contacts = serializers.JSONField(required=False)
    service_areas = serializers.JSONField(required=False)
    image = serializers.ImageField(write_only=True, required=False, allow_null=True)
    photo = serializers.ImageField(write_only=True, required=False, allow_null=True)

    def validate(self, attrs):
        category = attrs['category']
        sub_category = attrs['sub_category']
        district = attrs['district']
        location = attrs['location']

        if sub_category.category_id != category.id:
            raise serializers.ValidationError({
                'sub_category_id': 'Subcategory must belong to the supplied category.'
            })

        location_district_id = getattr(location.local, 'local_district_id', None)
        if location_district_id != district.id:
            raise serializers.ValidationError({
                'location_id': 'Location must belong to the supplied district.'
            })

        attrs['phone_number'] = normalize_phone_number(attrs.get('phone_number', ''))
        if attrs['phone_number']:
            self._validate_model_phone(attrs['phone_number'], 'phone_number')

        if attrs.get('call_for_pricing', True):
            attrs['price'] = -1
        elif attrs.get('price', -1) < 0:
            raise serializers.ValidationError({
                'price': 'Price must be 0 or greater unless call_for_pricing is true.'
            })

        attrs['contacts'] = self._validate_contacts(parse_json_list(attrs.get('contacts'), 'contacts'))
        attrs['service_areas'] = self._validate_service_areas(
            parse_json_list(attrs.get('service_areas'), 'service_areas')
        )

        image = attrs.get('image') or attrs.get('photo')
        if image:
            try:
                validate_image(image)
            except ImageValidationError as exc:
                raise serializers.ValidationError({'image': str(exc)})
            image.seek(0)

        return attrs

    def find_duplicate(self):
        attrs = self.validated_data
        source_url = attrs.get('source_url', '')
        if source_url:
            source = ImportedGigSource.objects.select_related('gig').filter(
                source_url=source_url,
                duplicate_of__isnull=True,
            ).first()
            if source:
                return source.gig, 'source_url'

        phone_number = attrs.get('phone_number', '')
        if phone_number:
            phone_match = Gig.objects.filter(phone_number=phone_number).first()
            if phone_match:
                return phone_match, 'phone_number'
            contact_match = GigContact.objects.select_related('gig').filter(
                phone_number=phone_number
            ).first()
            if contact_match:
                return contact_match.gig, 'contact_phone_number'

        title_match = Gig.objects.filter(
            title__iexact=attrs['title'],
            location=attrs['location'],
        ).first()
        if title_match:
            return title_match, 'title_location'

        return None, ''

    @transaction.atomic
    def save(self, **kwargs):
        user = kwargs['user']
        imported_by = kwargs.get('imported_by', user)
        attrs = dict(self.validated_data)
        contacts = attrs.pop('contacts', [])
        service_areas = attrs.pop('service_areas', [])
        source_url = attrs.pop('source_url', '')
        source_notes = attrs.pop('source_notes', '')
        image = attrs.pop('image', None) or attrs.pop('photo', None)
        attrs.pop('photo', None)

        gig_kwargs = attrs
        if image:
            gig_kwargs['photo'] = image
        gig = Gig.objects.create(user=user, **gig_kwargs)

        for index, contact in enumerate(contacts):
            GigContact.objects.create(
                gig=gig,
                phone_number=contact['phone_number'],
                description=contact.get('description', ''),
                is_whatsapp=bool(contact.get('is_whatsapp', False)),
                is_primary=bool(contact.get('is_primary', index == 0)),
                order=contact.get('order', index),
            )

        for index, area in enumerate(service_areas):
            GigServiceArea.objects.create(
                gig=gig,
                district=area['district'],
                location=area['location'],
                description=area.get('description', ''),
                is_primary=bool(area.get('is_primary', index == 0)),
                order=area.get('order', index),
            )

        raw_payload = self._safe_raw_payload()
        ImportedGigSource.objects.create(
            gig=gig,
            source_url=source_url,
            source_notes=source_notes,
            raw_payload=raw_payload,
            imported_by=imported_by,
        )
        return gig

    def _validate_contacts(self, contacts):
        normalized_contacts = []
        for index, contact in enumerate(contacts):
            if not isinstance(contact, dict):
                raise serializers.ValidationError({'contacts': f'Item {index + 1} must be an object.'})
            phone_number = normalize_phone_number(contact.get('phone_number', ''))
            if not phone_number:
                raise serializers.ValidationError({'contacts': f'Item {index + 1} requires phone_number.'})
            self._validate_model_phone(phone_number, 'contacts')
            normalized_contacts.append({
                'phone_number': phone_number,
                'description': str(contact.get('description', ''))[:100],
                'is_whatsapp': bool(contact.get('is_whatsapp', False)),
                'is_primary': bool(contact.get('is_primary', index == 0)),
                'order': int(contact.get('order', index)),
            })
        return normalized_contacts

    def _validate_service_areas(self, service_areas):
        normalized_areas = []
        for index, area in enumerate(service_areas):
            if not isinstance(area, dict):
                raise serializers.ValidationError({'service_areas': f'Item {index + 1} must be an object.'})
            try:
                district = District.objects.get(pk=area.get('district_id'))
                location = Location.objects.select_related('local__local_district').get(pk=area.get('location_id'))
            except (District.DoesNotExist, Location.DoesNotExist):
                raise serializers.ValidationError({
                    'service_areas': f'Item {index + 1} has an invalid district_id or location_id.'
                })
            if getattr(location.local, 'local_district_id', None) != district.id:
                raise serializers.ValidationError({
                    'service_areas': f'Item {index + 1} location must belong to its district.'
                })
            normalized_areas.append({
                'district': district,
                'location': location,
                'description': str(area.get('description', ''))[:100],
                'is_primary': bool(area.get('is_primary', index == 0)),
                'order': int(area.get('order', index)),
            })
        return normalized_areas

    def _validate_model_phone(self, phone_number, field_name):
        field = Gig._meta.get_field('phone_number')
        try:
            field.run_validators(phone_number)
        except DjangoValidationError as exc:
            raise serializers.ValidationError({field_name: exc.messages})

    def _safe_raw_payload(self):
        payload = {}
        for key, value in self.initial_data.items():
            if key in ('image', 'photo'):
                continue
            if hasattr(value, 'name') and hasattr(value, 'size'):
                payload[key] = {'name': value.name, 'size': value.size}
            else:
                payload[key] = value
        return payload
