


INSERT_TRIGGER_TEMPLATE_SQLITE='''

CREATE TRIGGER [IF NOT EXISTS] trigger_name 
   [BEFORE|AFTER|INSTEAD OF] [INSERT|UPDATE|DELETE] 
   ON table_name
   [WHEN condition]
BEGIN
 statements;
END;

'''

UPDATE_TRIGGER_TEMPLATE='''

CREATE TRIGGER validate_email_before_insert_leads 
   BEFORE INSERT ON leads
BEGIN
   SELECT
      CASE
	WHEN NEW.email NOT LIKE '%_@__%.__%' THEN
   	  RAISE (ABORT,'Invalid email address')
       END;
END;
'''

DELETE_TRIGGER_TEMPLATE='''


'''