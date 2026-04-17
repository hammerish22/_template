CREATE OR REPLACE FUNCTION insert_audit_row()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    EXECUTE format(
        'INSERT INTO audit.%I SELECT ($1).*',
        TG_TABLE_NAME
    ) USING NEW;
    RETURN NEW;
END;
$$;


DROP EVENT TRIGGER IF EXISTS ensure_insert_audit_row;
DROP FUNCTION IF EXISTS ensure_insert_audit_row();

CREATE OR REPLACE FUNCTION ensure_insert_audit_row()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
DECLARE
    obj        record;
    src_schema text;
    src_table  text;
BEGIN
    FOR obj IN
        SELECT *
        FROM pg_event_trigger_ddl_commands()
        WHERE command_tag = 'CREATE TABLE'
    LOOP
        src_schema := obj.schema_name;
        src_table  := split_part(obj.object_identity, '.', 2);

        CONTINUE WHEN src_schema <> 'public';
        CONTINUE WHEN src_table = '_alembic_version';

        EXECUTE format(
            'DROP TRIGGER IF EXISTS insert_audit_row ON public.%I;
            CREATE TRIGGER insert_audit_row
            AFTER INSERT OR UPDATE ON public.%I
            FOR EACH ROW
            EXECUTE FUNCTION insert_audit_row();',
            src_table, src_table
        );
    END LOOP;
END;
$$;


CREATE EVENT TRIGGER ensure_insert_audit_row
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION ensure_insert_audit_row();
