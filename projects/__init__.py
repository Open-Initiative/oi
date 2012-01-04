from StringIO import StringIO
from django.core import serializers
from django.core.serializers import base
from django.core.serializers import python
from django.utils.encoding import is_protected_type

def oiserialize(format, queryset, **options):
    """
    Serialize a queryset (or any iterator that returns database objects) using
    a certain serializer.
    """
    s = serializers.get_serializer(format)()
    s._oiserialize(queryset, **options)
    return s.getvalue()

serializers.oiserialize = oiserialize

def _oiserialize(self, queryset, **options):
    """
    Serialize a queryset.
    """
    self.options = options

    self.stream = options.pop("stream", StringIO())
    self.selected_fields = options.pop("fields", None)
    self.use_natural_keys = options.pop("use_natural_keys", False)
    self.extra_fields = options.pop("extra_fields", [])

    self.start_serialization()
    for obj in queryset:
        self.start_object(obj)
        for field in obj._meta.local_fields:
            if field.serialize:
                if field.rel is None:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_field(obj, field)
                else:
                    if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                        self.handle_fk_field(obj, field)
        for field in obj._meta.many_to_many:
            if field.serialize:
                if self.selected_fields is None or field.attname in self.selected_fields:
                    self.handle_m2m_field(obj, field)
        for field in self.extra_fields:
            self.handle_extra_field(obj, field)
        self.end_object(obj)
    self.end_serialization()
    return self.getvalue()

base.Serializer._oiserialize = _oiserialize

def handle_extra_field(self, obj, field_name):
    value = obj
    try:
        for field in field_name.split("."):
            value = value.__getattribute__(field)
            if callable(value):
                value = value()
    except AttributeError:
        return None
    # Protected types (i.e., primitives like None, numbers, dates,
    # and Decimals) are passed through as is. All other values are
    # converted to string first.
    if is_protected_type(value):
        self._current[field_name.replace(".","_")] = value
    else:
        self._current[field_name.replace(".","_")] = str(value)

python.Serializer.handle_extra_field = handle_extra_field
