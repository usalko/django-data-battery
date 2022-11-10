
from enum import Enum
from django_data_battery.models import DjangoModel
from django.apps import apps


class EventType(Enum):
    INSERT = 0
    UPDATE = 1
    DELETE = 2


class TriggersFactory:

    @classmethod
    def _unique_trigger_name(cls, table_name: str, event_type: EventType) -> str:
        if event_type == EventType.INSERT:
            return f'_{table_name}_insert'
        elif event_type == EventType.UPDATE:
            return f'_{table_name}_update'
        elif event_type == EventType.DELETE:
            return f'_{table_name}_delete'
        raise BaseException(f'Not supported event type: {event_type}')

    @classmethod
    def _django_model_id(cls, type_name: str) -> int:
        # TODO convert table name to type in django manager
        result = DjangoModel.objects.filter(type_name=type_name).first()
        return result.pk if result else None

    @classmethod
    def _model(cls, app_label, model_name) -> str:
        return

    @classmethod
    def create_trigger_on_delete(cls, table_name):
        pass

    @classmethod
    def create_trigger_on_insert_sqlite(cls, django_type: str):
        model = apps.get_model(django_type.split(
            '.')[0], django_type.split('.')[1])
        return f'''
            CREATE TRIGGER IF NOT EXISTS {cls._unique_trigger_name(model._meta.db_table, EventType.INSERT)} 
            AFTER INSERT
            ON {model._meta.db_table}
            BEGIN
                -- TODO: calculate pair function value instead simple NEW.id 
                insert into django_data_battery_inserted_ids (id, django_model_id) values (NEW.id, {cls._django_model_id(django_type)});
            END;
            '''

    @classmethod
    def create_trigger_on_insert_postgres(cls, table_name):
        trigger_function_name = f'_tf_{cls._unique_trigger_name(table_name)}'
        return f'''
    
        CREATE OR REPLACE FUNCTION {trigger_function_name}() RETURNS TRIGGER
        AS $trigger$
            BEGIN
                -- TODO: calculate pair function value instead simple NEW.id 
                insert into django_data_battery_inserted_ids (id, django_model_id) values (NEW.id, {cls._django_model_id(table_name)});
            END;

    
            CREATE TRIGGER IF NOT EXISTS {cls._unique_trigger_name(table_name)} 
            AFTER INSERT
            ON {table_name}
            FOR EACH ROW
            EXECUTE FUNCTION {trigger_function_name}()
            '''

    @classmethod
    def create_trigger_on_insert_mysql(cls, table_name):
        return f'''
            CREATE TRIGGER IF NOT EXISTS {cls._unique_trigger_name(table_name)} 
            AFTER INSERT
            ON {table_name}
            FOR EACH ROW
            BEGIN
                -- TODO: calculate pair function value instead simple NEW.id 
                insert into django_data_battery_inserted_ids (id, django_model_id) values (NEW.id, {cls._django_model_id(table_name)});
            END;
            '''

    @classmethod
    def create_trigger_on_update(cls, table_name):
        pass
