VERSION = (0, 1, 57, 'alpha')


def get_release():
    return '-'.join([get_version(), VERSION[-1]])


def get_version():
    """
    Returns only digit parts of version.
    """
    return '.'.join(str(i) for i in VERSION[:3])


__author__ = 'usalko'
__docformat__ = 'restructuredtext en'
__copyright__ = 'Copyright 2022, usalko'
__license__ = 'Apache Software License'
__version__ = get_version()
__maintainer__ = 'usalko'
__email__ = 'ivict@rambler.ru'
__status__ = 'Development'

# default the django_data_battery app config
default_app_config = 'django_data_battery.apps.AppConfig'
