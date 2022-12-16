from logging import exception

from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import HttpResponseRedirect, csrf_protect_m
from django.contrib.admin.utils import unquote
from django.db import connection, connections, transaction, utils
from django.urls import path
from django.contrib.auth.models import User
from django.core.management.commands import migrate
from django.db.models import signals


from .models import *
from .utils.triggers_factory import TriggersFactory
from .utils.useful_tools import _elegant_unpair


def _default_database_type() -> str:
    return str(settings.DATABASES['default']['ENGINE'].split('.')[-1]).lower()


def _is_utility_application(app_label: str):
    if app_label == 'django_data_battery':
        return True
    if app_label == 'admin':
        return True
    if app_label == 'auth':
        return True
    if app_label == 'contenttypes':
        return True
    if app_label == 'sessions':
        return True
    if app_label == 'reversion':
        return True
    return False


class DjangoModelAdmin(admin.ModelAdmin):
    change_list_template = 'django_data_battery/admin_change_list_django_model.html'

    actions = ['_refresh']

    database_type = _default_database_type()

    list_display = ('id', 'type_name')
    # list_filter = ('id', 'type_name')
    search_fields = ('id', 'type_name')
    ordering = ('type_name',)

    def _refresh(self, request, queryset=None):
        added_count = 0

        for model in apps.get_models():  # Returns a "list" of all models created
            if _is_utility_application(model._meta.app_label):
                continue
            django_type = f'{model._meta.app_label}.{model.__name__}'
            django_model = DjangoModel.objects.filter(
                type_name__iexact=django_type).first()
            if not django_model:
                django_model = DjangoModel(type_name=django_type)
                django_model.save()
                added_count += 1

            # Create triggers
            if self.database_type == 'sqlite3':
                try:
                    cursor = connection.cursor()
                    for statement in TriggersFactory.create_statements_on_insert_sqlite(django_type):
                        cursor.execute(statement)
                except BaseException as e:
                    exception(e)
            else:
                raise BaseException(
                    f'Database type: {self.database_type} is not handling')

        if added_count:
            msg = "Added {} new django models".format(added_count)
            self.message_user(request, msg, messages.SUCCESS)

        return HttpResponseRedirect("../")

    _refresh.short_description = 'Refresh all models'

    def get_urls(self):
        urls = super().get_urls()
        urls = [
            path('_refresh/', self._refresh),
        ] + urls
        return urls

    def has_add_permission(self, request):
        return False

    class Meta:
        model = DjangoModel
        fields = ['id', 'django_type']


class DatabaseConnectionSettingsAdmin(admin.ModelAdmin):
    change_form_template = 'django_data_battery/admin_change_form_database_connection_settings.html'

    def _url(self, obj: DatabaseConnectionSettings):
        return obj.engine

    def _get_or_create_database_id(self, obj: DatabaseConnectionSettings) -> str:
        database_id = str(obj)  # just something unique
        if not (database_id in connections.databases):
            newDatabase = {}
            newDatabase['id'] = database_id
            newDatabase['ENGINE'] = obj.engine
            newDatabase['NAME'] = obj.name
            newDatabase['USER'] = obj.user
            newDatabase['PASSWORD'] = obj.password
            newDatabase['HOST'] = obj.host
            newDatabase['PORT'] = obj.port
            connections.databases[database_id] = newDatabase

        return database_id

    def _save_with_the_child_tree(self, obj: models.Model, using: str):
        try:
            foreign_key_fields = [field_object for field_object in type(
                obj)._meta.get_fields() if isinstance(field_object, models.ForeignKey)]
            for field_object in foreign_key_fields:
                relation_object = getattr(obj, field_object.name)
                if relation_object:
                    self._save_with_the_child_tree(relation_object, using=using)
                    is_force_insert = not relation_object._meta.model.objects.using(using).filter(pk=relation_object.pk).exists()
                    if is_force_insert:
                        relation_object.save(using=using, force_insert=True)
                    else:
                        relation_object.save(using=using, force_update=True)

            is_force_insert = not obj._meta.model.objects.using(using).filter(pk=obj.pk).exists()
            if is_force_insert:
                obj.save(using=using, force_insert=True)
            else:
                obj.save(using=using, force_update=True)
        except BaseException as e:
            raise e

    def _temporary_clear(self, db: str, obj: models.Model, attribute_name: str):
        many_to_many_manager = getattr(obj, attribute_name)
        with transaction.atomic(using=db, savepoint=False):
            signals.m2m_changed.send(
                sender=many_to_many_manager.through, action="pre_clear",
                instance=many_to_many_manager.instance, reverse=many_to_many_manager.reverse,
                model=many_to_many_manager.model, pk_set=None, using=db,
            )
            many_to_many_manager._remove_prefetched_objects()
            filters = many_to_many_manager._build_remove_filters(
                many_to_many_manager.get_queryset().using(db))
            many_to_many_manager.through._default_manager.using(
                db).filter(filters).delete()

            signals.m2m_changed.send(
                sender=many_to_many_manager.through, action="post_clear",
                instance=many_to_many_manager.instance, reverse=many_to_many_manager.reverse,
                model=many_to_many_manager.model, pk_set=None, using=db,
            )

    def _save_and_correct_sequences(self, obj: models.Model, database_id: str, read_circuit_breaker: set, many_to_many_attributes: dict, without_many_to_many: bool):
        if obj in read_circuit_breaker:
            return
        if isinstance(obj, User):
            User(id=obj.pk).save(using=database_id)
            return

        read_circuit_breaker.add(obj)
        global_id = (obj._meta.model_name, obj.pk)
        # Detect all references
        for field_object in type(obj)._meta.get_fields():
            if isinstance(field_object, models.ForeignKey):
                relation_object = getattr(obj, field_object.name)
                if relation_object:
                    self._save_and_correct_sequences(
                        relation_object, database_id, read_circuit_breaker, many_to_many_attributes, without_many_to_many)
                    # setattr(obj, field_object.name, relation_object)
            elif field_object.many_to_many:
                values = []
                attribute_name = None
                many_to_many_references = None
                # for referenced_object in field_object.
                if hasattr(obj, f'{field_object.name}_set'):
                    attribute_name = f'{field_object.name}_set'
                    many_to_many_references = getattr(obj, attribute_name)
                    for relation_object in many_to_many_references.all():
                        self._save_and_correct_sequences(
                            relation_object, database_id, read_circuit_breaker, many_to_many_attributes, without_many_to_many)
                        values.append(relation_object)
                elif hasattr(obj, field_object.name):
                    attribute_name = field_object.name
                    many_to_many_references = getattr(obj, attribute_name)
                    for relation_object in many_to_many_references.all():
                        self._save_and_correct_sequences(
                            relation_object, database_id, read_circuit_breaker, many_to_many_attributes, without_many_to_many)
                        values.append(relation_object)

                # mark many to many attribute
                if not (global_id in many_to_many_attributes):
                    many_to_many_attributes[global_id] = dict()

                if attribute_name and values:
                    many_to_many_attributes[global_id][attribute_name] = values

        try:
            # Empty all many to many
            if global_id in many_to_many_attributes and many_to_many_attributes[global_id]:
                for attribute_name, _ in many_to_many_attributes[global_id].items():
                    self._temporary_clear(database_id, obj, attribute_name)
            # Save all foreign key refs
            self._save_with_the_child_tree(obj, using=database_id)
            # many to many handle
            if global_id in many_to_many_attributes and many_to_many_attributes[global_id] and not without_many_to_many:
                for attribute_name, values in many_to_many_attributes[global_id].items():
                    for value in values:
                        self._save_with_the_child_tree(value, using=database_id)
                    getattr(obj, attribute_name).add(*values)
                obj.save(using=database_id)

        except BaseException as e:
            exception(e)

    def _export_inserted(self, request, obj: DatabaseConnectionSettings = None):
        try:
            database_id = self._get_or_create_database_id(obj)
            for app_label in set([model._meta.app_label for model in apps.get_models()]):
                migrate_command = migrate.Command()
                migrate_command.verbosity = 1
                migrate_command.sync_apps(
                    connections[database_id], app_labels=app_label)

            # TODO: BATCH COPY FROM InsertedIds to the InflightInsertIds

            # with connections[database_id].cursor() as cursor:
            #     cursor.execute('''PRAGMA ignore_check_constraints = 1;''') # Here

            for inflight_id in InsertedIds.objects.all():
                django_object_id, _ = _elegant_unpair(inflight_id.id)
                django_type = inflight_id.django_model.type_name
                model = apps.get_model(django_type.split(
                    '.')[0], django_type.split('.')[1])
                model_instance = model.objects.get(pk=django_object_id)

                many_to_many_attributes = dict()
                self._save_and_correct_sequences(
                    model_instance, database_id, set(), many_to_many_attributes, True)
                if many_to_many_attributes: # Handle the many-to-many
                    self._save_and_correct_sequences(
                        model_instance, database_id, set(), many_to_many_attributes, False)

            self.message_user(
                request, f'Export all inserted for the connection {obj}', messages.SUCCESS)
        except BaseException as e:
            exception(e)
            self.message_user(
                request, f'Sorry, but error occur {e}', messages.ERROR)

    _export_inserted.short_description = 'Export all inserted'

    @csrf_protect_m
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if request.method == 'GET' and '_export_inserted' in request.GET:
            obj = self.get_object(request, unquote(object_id))
            self._export_inserted(request, obj)
            # return HttpResponseRedirect(request.get_full_path())

        return admin.ModelAdmin.changeform_view(
            self, request,
            object_id=object_id,
            form_url=form_url,
            extra_context=extra_context,
        )

    class Meta:
        model = DatabaseConnectionSettings
        fields = '__all__'


admin.site.register(DjangoModel, DjangoModelAdmin)
admin.site.register(DatabaseConnectionSettings,
                    DatabaseConnectionSettingsAdmin)
