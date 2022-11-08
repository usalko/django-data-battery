from django.db import models
from django.utils.translation import gettext_lazy as _


class InflightUpdateIds(models.Model):

    class Meta:
        'Inflight update ids (pay attention for id in that table compound value described in algo in django_model.py modules)'
        verbose_name = _('inflight update id')
        verbose_name_plural = _('inflight update ids')
        db_table = 'django_data_battery_inflight_update_ids'

    id = models.IntegerField(primary_key=True)
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
