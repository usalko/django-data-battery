from unittest import TestCase
from django_data_battery.utils.triggers_factory import TriggersFactory


class TriggersFactoryTest(TestCase):

    def test_insert_trigger_sqlite(self):
        trigger_creation_text = TriggersFactory.create_trigger_on_insert_sqlite(
            'table1')
        self.assertIsNotNone(trigger_creation_text)

    def test_insert_trigger_postgresql(self):

        self.assertTrue(True)

    def test_insert_trigger_mysql(self):

        self.assertTrue(True)
