from logging import exception

from django.apps import apps
from django.conf import settings
from django.contrib import admin, messages
from django.contrib.admin.options import HttpResponseRedirect
from django.db import connection
from django.urls import path

from .models import *
from .utils.triggers_factory import TriggersFactory


def _default_database_type() -> str:
    return str(settings.DATABASES['default']['ENGINE'].split('.')[-1]).lower()


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
            if model._meta.app_label == 'django_data_battery':
                continue
            if model._meta.app_label == 'admin':
                continue
            if model._meta.app_label == 'auth':
                continue
            if model._meta.app_label == 'contenttypes':
                continue
            if model._meta.app_label == 'sessions':
                continue
            if model._meta.app_label == 'reversion':
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
                    cursor.execute(
                        TriggersFactory.create_trigger_on_insert_sqlite(django_type))
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


admin.site.register(DjangoModel, DjangoModelAdmin)
