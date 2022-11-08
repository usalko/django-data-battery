from django.db import models
from django.utils.translation import gettext_lazy as _



class UpdatedIds(models.Model):

    class Meta:
        'Updated ids (pay attention for id in that table compound value described in algo in django_model.py modules)'
        verbose_name = _('updated id')
        verbose_name_plural = _('updated ids')
        db_table = 'django_data_battery_updated_ids'

    id = models.IntegerField(primary_key=True)
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
