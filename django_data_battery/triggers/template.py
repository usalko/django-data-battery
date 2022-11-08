


INSERT_TRIGGER_TEMPLATE_SQLITE='''

CREATE TRIGGER [IF NOT EXISTS] trigger_name 
   [BEFORE|AFTER|INSTEAD OF] [INSERT|UPDATE|DELETE] 
   ON table_name
   [WHEN condition]
BEGIN
 statements;
END;

'''

INSERT_TRIGGER_TEMPLATE_POSTGRES='''

CREATE OR REPLACE FUNCTION process_emp_audit() RETURNS TRIGGER AS $emp_audit$
    BEGIN
        --
        -- Create rows in emp_audit to reflect the operations performed on emp,
        -- making use of the special variable TG_OP to work out the operation.
        --
        IF (TG_OP = 'DELETE') THEN
            INSERT INTO emp_audit
                SELECT 'D', now(), user, o.* FROM old_table o;
        ELSIF (TG_OP = 'UPDATE') THEN
            INSERT INTO emp_audit
                SELECT 'U', now(), user, n.* FROM new_table n;
        ELSIF (TG_OP = 'INSERT') THEN
            INSERT INTO emp_audit
                SELECT 'I', now(), user, n.* FROM new_table n;
        END IF;
        RETURN NULL; -- result is ignored since this is an AFTER trigger
    END;
$emp_audit$ LANGUAGE plpgsql;

CREATE TRIGGER emp_audit_ins
    AFTER INSERT ON emp
    REFERENCING NEW TABLE AS new_table
    FOR EACH STATEMENT EXECUTE FUNCTION process_emp_audit();


'''


INSERT_TRIGGER_TEMPLATE_MYSQL='''

CREATE TRIGGER upd_check BEFORE UPDATE ON account
       FOR EACH ROW
       BEGIN
           IF NEW.amount < 0 THEN
               SET NEW.amount = 0;
           ELSEIF NEW.amount > 100 THEN
               SET NEW.amount = 100;
           END IF;
       END;//


'''

UPDATE_TRIGGER_TEMPLATE='''


'''

DELETE_TRIGGER_TEMPLATE='''


'''