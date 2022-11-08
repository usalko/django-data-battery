from django.db import models
from django.utils.translation import gettext_lazy as _



class InsertedIds(models.Model):

    class Meta:
        'Inserted ids (pay attention for id in that table compound value described in algo in django_model.py modules)'
        verbose_name = _('inserted id')
        verbose_name_plural = _('inserted ids')
        db_table = 'django_data_battery_inserted_ids'

    id = models.IntegerField(primary_key=True)
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
