from django.db import models
from django.utils.translation import gettext_lazy as _



'''
DESCRIPTION FOR AN ALGORITHM FOR COMPOUND ID value (@see also http://szudzik.com/ElegantPairing.pdf)

..._ids table has the structure

id
django_model_id

def elegant_pair(x, y):
    return y*y + x if x != max(x, y) else x*x + x + y
    
def elegant_unpair(z, y):
    return (z - y*y, y) if (z - y*y) < y else (y, )

function elegantPair(x, y) {
  return (x >= y) ? (x * x + x + y) : (y * y + x);
}

function elegantUnpair(z) {
  var sqrtz = Math.floor(Math.sqrt(z)),
    sqz = sqrtz * sqrtz;
  return ((z - sqz) >= sqrtz) ? [sqrtz, z - sqz - sqrtz] : [z - sqz, sqrtz];
}

1. Get real id for the django model
   real_id = id & HIGH_ORDER_MASK
   
2. Get compound id for the django model
   id = real_id | INVERTED_HIGH_ORDER_MASK & (HIGH_ORDER_MASK * django_model_id)



'''

class DjangoModel(models.Model):
    type_name = models.CharField(
        max_length=150, unique=True, verbose_name='type name'),

    class Meta:
        'Django models for synchronization with wikibase'
        verbose_name = _('django model')
        verbose_name_plural = _('django models')
        db_table = 'django_data_battery_django_models'