"""
.. module::  core.models
   :synopsis:  Shared Django-utils core  models module.

Shared Django-utils core  models module.
"""
from __future__ import absolute_import
import logging
import inflection

from django.contrib.sites.models import Site
from django.utils.translation import gettext as _

from django.db import models

from utils.core import class_name
from . import fields
from . import constants


logger = logging.getLogger(__name__)


def verbose_class_name(class_name):
    """Generate verbose name from class name.
    """
    verbose_name = inflection.underscore(class_name)
    verbose_name = verbose_name.replace('_', ' ')
    return verbose_name


def pluralize(name):
    """Pluralize a name.
    """
    return inflection.pluralize(name)


def db_table_for_class(class_name):
    """Convert class name to db table name.
    """
    table_name = inflection.underscore(class_name)
    return table_name


def db_table_for_app_and_class(app_name, table_name, site_label):
    """Generate application table name.
    """
    site_label = site_label or constants.SITE_LABEL
    return '{}_{}_{}'.format(site_label, app_name, table_name)


def db_table(app_name, class_name, site_label=None):
    """Generate db table name.
    """
    return db_table_for_app_and_class(
        app_name, db_table_for_class(class_name), site_label)


def meta(meta_base_classes, app_label=None, **kwargs):
    """Tweak  meta attributes.
    """
    # @TODO: Does not work  in Django 1.9; options not incorporated
    # into migration
    def wrapped(cls):
        class_name_ = class_name(cls)
        verbose_name = verbose_class_name(class_name_)
        plural_name = pluralize(verbose_name)
        table_name = db_table_for_class(class_name_)
        meta_attrs = {
            '__module__': cls.__module__,
            'verbose_name': _(verbose_name),
            'verbose_name_plural': _(plural_name),
            'db_table': db_table_for_app_and_class(app_label, table_name)
        }
        if app_label is not None:
            meta_attrs['app_label'] = app_label

        if meta_base_classes is not None:
            if not isinstance(meta_base_classes, tuple):
                meta_base = (meta_base_classes,)
            else:
                meta_base = meta_base_classes
        else:
            meta_base = (object, )
        meta_attrs.update(kwargs)
        meta = type('Meta', meta_base, meta_attrs)
        _meta = cls._meta
        _meta.db_table = meta.db_table
        _meta.verbose_name = meta.verbose_name
        _meta.verbose_name_plural = meta.verbose_name_plural
        cls.Meta = meta
        return cls

    return wrapped


class VersionedModelManager(models.Manager):
    """Versioned object manager class.
    """

    def get_or_none(self, *args, **kwargs):
        """Return an object instance or none.

        :param args: Positional argument list.
        :type args: list.
        :param kwargs: Key words arguments.
        :type kwargs: dict.
        :returns:  An instance of Model or None.
        """
        try:
            return self.get(*args, **kwargs)
        except self.model.DoesNotExist:
            return None


class VersionedModel(models.Model):
    """An abstract base class for application object versioning.
    """
    class Meta(object):
        abstract = True
        get_latest_by = 'update_time'

    objects = VersionedModelManager()
    id = fields.auto_field()
    uuid = fields.uuid_field()
    version = fields.integer_field()
    enabled = fields.boolean_field(default=True)
    deleted = fields.boolean_field(default=False)
    creation_time = fields.datetime_field(auto_now_add=True)
    update_time = fields.datetime_field(auto_now=True)

    # user who created the instance
    creation_user = fields.user_field(
        related_name="%(app_label)s_%(class)s_related_creation_user")

    # user who triggered the instance update
    update_user = fields.user_field(
        related_name="%(app_label)s_%(class)s_related_update_user")

    # user on whose behalf change is made
    effective_user = fields.user_field(
        related_name="%(app_label)s_%(class)s_related_effective_user")

    site = fields.foreign_key_field(
        Site,
        related_name="%(app_label)s_%(class)s_related_site")

    def __init__(self, *args, **kwargs):
        super(VersionedModel, self).__init__(*args, **kwargs)

    def save(self, *args, **kwargs):
        """Save an instance.
        """
        self.version += 1
        update_user = kwargs.pop("update_user", None)
        if update_user is not None:
            self.update_user = update_user
        effective_user = kwargs.pop("effective_user", None)
        if update_user is not None:
            self.effective_user = effective_user
        super(VersionedModel, self).save(*args, **kwargs)


class NamedModelManager(VersionedModelManager):
    """Named object manager class.
    """
    def named_instance(self, name):
        """Find a named instance.
        """
        try:
            return self.get(name=name)
        except self.model.DoesNotExist:
            logger.warn('Failed to retrieve instance of type (%s) named (%s)',
                        class_name(self.model), name)
            return self.get(name=constants.UNKNOWN)


class NamedModel(VersionedModel):
    """Abstract base class for named model instances.

    Designed to facilitate the capture of static reference data
    types such as countries, currencies, and languages.
    """
    class Meta(VersionedModel.Meta):
        abstract = True
        ordering = ("name",)

    objects = NamedModelManager()
    name = fields.name_field()
    alias = fields.name_field(blank=True, null=True, unique=False)
    description = fields.description_field(blank=True, null=True)

    @property
    def display_name(self):
        return self.alias if self.alias else self.name

    def __str__(self):
        return self.display_name


class PrioritizedModel(models.Model):
    """An abstract base class for models requiring priority.
    Associate a priority with an instance.
    """
    class Meta(object):
        abstract = True

    priority = fields.priority_field()