"""
.. module::  core.fields
   :synopsis:  django-utils core model fields utilities module.

The *fields* module is a collection of Django model fields utilities
designed to foster common field usage and facilitate configuration changes.
"""
from __future__ import absolute_import

import uuid
import inflection

from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core import validators
from django.utils.translation import gettext as _

from timezone_field import TimeZoneField
from macaddress.fields import MACAddressField
from phonenumber_field.modelfields import PhoneNumberField

from utils.core import class_name

# Note: each factory function has '_field' suffix to minimize conflicts with
# core and 3rd party python modules and foster naming consistency albeit
# while introducing somewhat undesirable verbosity
#


def auto_field(**kwargs):
    """
    Return a new instance of auto increment model field.
    """
    defaults = dict(
        blank=True,
        null=False,
        primary_key=True,
        unique=True)
    defaults.update(kwargs)
    return models.AutoField(**defaults)


def boolean_field(**kwargs):
    """
    Return a new instance of boolean model field.
    """
    defaults = dict(
        blank=False,
        null=False,
        default=False)
    defaults.update(kwargs)
    return models.BooleanField(**defaults)


def file_field(upload_to, **kwargs):
    """
    Return a new instance of file model field.
    """
    return models.FileField(upload_to=upload_to, **kwargs)

CHAR_FIELD_MAX_LENGTH = 1024


def char_field(**kwargs):
    """
    Return a new instance of char model field.
    """
    defaults = dict(
        max_length=CHAR_FIELD_MAX_LENGTH,
        blank=False,
        null=False,
        unique=False)
    defaults.update(kwargs)
    return models.CharField(**defaults)


def date_field(**kwargs):
    """
    Return a new instance of date model field.
    """
    defaults = dict(auto_now=False,
                    auto_now_add=False,
                    blank=False,
                    null=False)
    defaults.update(kwargs)
    return models.DateField(**defaults)


def datetime_field(**kwargs):
    """
    Return a new instance of datetime model field.
    """
    defaults = dict(auto_now=False,
                    auto_now_add=False,
                    blank=False,
                    null=False)
    defaults.update(kwargs)
    return models.DateTimeField(**defaults)


def decimal_field(max_digits, decimal_places, **kwargs):
    """
    Return a new instance of decimal model field.
    """
    defaults = dict(
        decimal_places=decimal_places,
        max_digits=max_digits,
        default=0,
        blank=False, null=False)
    defaults.update(kwargs)
    return models.DecimalField(**defaults)


def floating_point_field(**kwargs):
    """
    Return a new instance of floating point model field.
    """
    defaults = dict(
        blank=False,
        null=False,
        default=0.0)
    defaults.update(kwargs)
    return models.FloatField(**defaults)


def foreign_key_field(to, **kwargs):
    """
    Return a new instance of foreign key model field.
    """
    defaults = dict(
        blank=False,
        db_constraint=True,
        null=False,
        on_delete=models.PROTECT)

    defaults.update(kwargs)
    return models.ForeignKey(to, **defaults)


def image_field(**kwargs):
    """
    Return a new instance of image model field.
    """
    return models.ImageField(**kwargs)


def integer_field(**kwargs):
    """
    Return a new instance of integer model field.
    """
    defaults = dict(
        default=0,
        blank=False, null=False)
    defaults.update(kwargs)
    return models.IntegerField(**defaults)


def ip_address_field(**kwargs):
    """
    Return a new instance of ip address model field.
    """
    defaults = dict(
        null=False,
        blank=False)
    defaults.update(kwargs)
    return models.GenericIPAddressField(**defaults)


def many_to_many_field(to, db_table, **kwargs):
    """
    Return a new instance of many to many model field.
    """
    defaults = dict(
        db_constraint=True,
        null=True,
        blank=True)

    related_name = kwargs.pop('related_name', None)
    defaults.update(kwargs)

    related_name = (
        related_name or
        '{}_set'.format(inflection.camelize(class_name(to))))

    return models.ManyToManyField(
        to,
        db_table=db_table,
        related_name=related_name,
        **defaults)


def one_to_one_field(to, **kwargs):
    """
    Return a new instance of one-to-one model field.
    """
    defaults = dict(
        blank=False,
        db_constraint=True,
        null=False,
        on_delete=models.PROTECT)

    defaults.update(kwargs)
    return models.OneToOneField(to, **defaults)


def small_integer_field(**kwargs):
    """
    Return a new instance of small integer model field.
    """
    defaults = dict(
        default=0,
        blank=False, null=False)
    defaults.update(kwargs)
    return models.SmallIntegerField(**defaults)


def text_field(**kwargs):
    """
    Return a new instance of text model field.
    """
    defaults = dict(
        blank=True,
        null=True,
        unique=False)
    defaults.update(kwargs)
    return models.TextField(**defaults)

URL_FIELD_MAX_LENGTH = 255


def url_field(**kwargs):
    """
    Return a new instance of url model field.
    """
    defaults = dict(
        max_length=URL_FIELD_MAX_LENGTH,
        null=False,
        blank=False)
    defaults.update(kwargs)
    return models.URLField(**defaults)


def uuid_field(**kwargs):
    """
    Return a new instance of uuid model field.
    """
    defaults = dict(
        unique=True,
        default=uuid.uuid4,
        db_index=True,
        editable=False)
    defaults.update(kwargs)
    return models.UUIDField(**defaults)


def annotation_field(**kwargs):
    """
    Return a new instance of annotation model field.
    """
    defaults = dict(
        blank=False,
        null=False,
        unique=False)
    defaults.update(kwargs)
    return text_field(**defaults)


def description_field(**kwargs):
    """
    Return a new instance of description model field.
    """
    defaults = dict(
        blank=False,
        null=False,
        unique=False)
    defaults.update(kwargs)
    return text_field(**defaults)

GEO_LOCATION_MAX_DIGITS = 9
GEO_LOCATION_DECIMAL_PLACES = 6


def latitude_validator(value):
    """
    Latitude validation
    """
    valid = -90 < value < 90
    if not valid:
        raise ValidationError(_('latitude not in range of -90 < value < 90'))
    return value


def longitude_validator(value):
    """
    Longitude validation
    """
    valid = -180 < value < 180
    if not valid:
        raise ValidationError(_('longitude not in range of -90 < value < 90'))
    return value


def geo_location_field(**kwargs):
    """
    Return a new instance of geo location model field.
    """
    defaults = dict(
        max_digits=GEO_LOCATION_MAX_DIGITS,
        decimal_places=GEO_LOCATION_DECIMAL_PLACES)
    defaults.update(kwargs)
    return decimal_field(**defaults)


def longitude_field(**kwargs):
    defaults = dict(
        validators=[longitude_validator])
    defaults.update(kwargs)
    return geo_location_field(**defaults)


def latitude_field(**kwargs):
    defaults = dict(
        validators=[latitude_validator])
    defaults.update(kwargs)
    return geo_location_field(**defaults)


def mac_address_field(**kwargs):
    """
    Return a new instance of mac address model field.
    """
    defaults = dict(
        unique=True,
        null=False,
        blank=False)
    defaults.update(kwargs)
    return MACAddressField(**defaults)

NAME_FIELD_MAX_LENGTH = 255


def name_field(**kwargs):
    """
    Return a new instance of name model field.
    """
    defaults = dict(
        max_length=NAME_FIELD_MAX_LENGTH,
        unique=True,
        db_index=True,
        null=False,
        blank=False)
    defaults.update(kwargs)
    return char_field(**defaults)


def user_field(**kwargs):
    """
    Return a new instance of a user model field.
    """
    return foreign_key_field(User, **kwargs)


USER_AGENT_FIELD_MAX_LENGTH = 512


def user_agent_field(**kwargs):
    """
    Return a new instance of user agent model field.
    """
    defaults = dict(
        null=False,
        blank=False,
        max_length=USER_AGENT_FIELD_MAX_LENGTH)
    defaults.update(kwargs)
    return char_field(**defaults)

# @TODO: revisit approach for default time zone field
DEFAULT_TIME_ZONE = 'America/New_York'


def time_zone_field(**kwargs):
    """
    Create time zone field instance
    """
    defaults = dict(
        null=False,
        blank=False,
        default=DEFAULT_TIME_ZONE)
    defaults.update(kwargs)
    return TimeZoneField(**defaults)


def phone_number_field(**kwargs):
    """
    Create phone number field instance
    """
    defaults = dict(
        null=False,
        blank=False)
    defaults.update(kwargs)
    return PhoneNumberField(**defaults)


def email_field(**kwargs):
    """
    Create email field instance
    """
    defaults = dict(
        null=False,
        blank=False)
    defaults.update(kwargs)
    return models.EmailField(**defaults)

_im_schemes = ["im", "xmpp"]


def instance_messaging_field(**kwargs):
    """
    Create instance messaging field instance
    """
    defaults = dict(
        null=False,
        blank=False,
        validators=[validators.URLValidator(schemes=_im_schemes)])
    defaults.update(kwargs)
    return url_field(**defaults)

_url_schemes = ['http', 'https', 'ftp', 'ftps']
_other_schemes = ['tel', 'mailto', 'urn']
_uri_schemes = _im_schemes + _url_schemes + _other_schemes


def uri_field(**kwargs):
    """
    Create uri field instance.

    Generic uri capture and validation.
    """
    defaults = dict(
        null=False,
        blank=False,
        validators=[validators.URLValidator(schemes=_uri_schemes)])
    defaults.update(kwargs)
    return url_field(**defaults)


def priority_field(**kwargs):
    """
    Create a priority field instance
    """
    defaults = dict(
        default=0)
    defaults.update(kwargs)
    return models.PositiveSmallIntegerField(**defaults)