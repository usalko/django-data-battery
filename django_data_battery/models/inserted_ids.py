from django.db import models


class InsertedIds(models.Model):

    class Meta:
        # unique_together = (('id', 'django_model'),)
        description = 'Inserted ids (pay attention for id in that table compound value described in algo in django_model.py modules)'

    id = models.IntegerField(primary_key=True)
    django_model = models.ForeignKey('DjangoModel', on_delete=models.CASCADE)
