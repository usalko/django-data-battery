from django.db import models
from django.utils.translation import gettext_lazy as _


class DeletedIds(models.Model):

    class Meta:
        'Deleted ids (pay attention for id in that table compound value described in algo in django_model.py modules)'
        verbose_name = _('deleted id')
        verbose_name_plural = _('deleted ids')
        db_table = 'django_data_battery_deleted_ids'

    id = models.IntegerField(primary_key=True)
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
