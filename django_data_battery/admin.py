from django.contrib import admin, messages
from django.contrib.admin.options import (HttpResponseRedirect, csrf_protect_m,
                                          unquote)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.db.models import Model
from django.urls import path

from .models import *


class DjangoModelAdmin(admin.ModelAdmin):
    change_list_template = 'django_data_battery/admin_change_list_django_model.html'

    actions = ['_refresh']

    def _refresh(self, request, queryset=None):
        updated_count = 1

        # from django.apps import apps

        # app_models = [model.__name__ for model in apps.get_models()] # Returns a "list" of all models created

        msg = "Marked {} new objects from existing".format(updated_count)
        self.message_user(request, msg, messages.SUCCESS)

        return HttpResponseRedirect("../")

    _refresh.short_description = 'Refresh all models'

    # @csrf_protect_m
    # def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
    #     if request.method == 'POST' and '_refresh' in request.POST:
    #         obj = self.get_object(request, unquote(object_id))
    #         self.make_published(request, obj)
    #         return HttpResponseRedirect(request.get_full_path())

    #     return admin.ModelAdmin.changeform_view(
    #         self, request,
    #         object_id=object_id,
    #         form_url=form_url,
    #         extra_context=extra_context,
    #     )

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
