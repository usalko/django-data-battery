
from enum import Enum
from django_data_battery.models import DjangoModel


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
    def _django_model_id(cls, table_name: str) -> int:
        # TODO convert table name to type in django manager
        django_model, _ = DjangoModel.objects.get_or_create({'django_type': table_name})
        return django_model.pk

    @classmethod
    def create_trigger_on_delete(cls, table_name):
        pass

    @classmethod
    def create_trigger_on_insert_sqlite(cls, table_name):
        return f'''
            CREATE TRIGGER IF NOT EXISTS {cls._unique_trigger_name(table_name)} 
            AFTER INSERT
            ON {table_name}
            BEGIN
                -- TODO: calculate pair function value instead simple NEW.id 
                insert into django_data_battery_inserted_ids (id, django_model_id) values (NEW.id, {cls._django_model_id(table_name)});
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
