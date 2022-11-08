from django.db import models


class InflightUpdateIds(models.Model):

    class Meta:
        unique_together = (('id', 'django_model'),)

    id = models.IntegerField()
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
