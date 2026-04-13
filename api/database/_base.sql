CREATE SCHEMA IF NOT EXISTS audit;

DROP EVENT TRIGGER IF EXISTS create_audit_table;
DROP FUNCTION IF EXISTS create_audit_table();

CREATE OR REPLACE FUNCTION create_audit_table()
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
        CONTINUE WHEN src_table = 'alembic_version';

        EXECUTE format(
            'CREATE TABLE IF NOT EXISTS audit.%I (
                audit_uid BIGSERIAL PRIMARY KEY,
                LIKE public.%I INCLUDING DEFAULTS EXCLUDING CONSTRAINTS EXCLUDING INDEXES
            )',
            src_table, src_table
        );
    END LOOP;
END;
$$;

CREATE EVENT TRIGGER create_audit_table
ON ddl_command_end
WHEN TAG IN ('CREATE TABLE')
EXECUTE FUNCTION create_audit_table();


DROP EVENT TRIGGER IF EXISTS alter_audit_table;
DROP FUNCTION IF EXISTS alter_audit_table();

CREATE OR REPLACE FUNCTION alter_audit_table()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
DECLARE
    obj        record;
    col        record;
    src_schema text;
    src_table  text;
BEGIN
    FOR obj IN
        SELECT *
        FROM pg_event_trigger_ddl_commands()
        WHERE command_tag = 'ALTER TABLE'
    LOOP
        src_schema := obj.schema_name;
        src_table  := split_part(obj.object_identity, '.', 2);

        CONTINUE WHEN src_schema <> 'public';
        CONTINUE WHEN src_table = 'alembic_version';

        -- ADD COLUMN: columns in public not yet in audit
        FOR col IN
            SELECT
                c.column_name,
                c.udt_name,
                c.character_maximum_length,
                c.is_nullable,
                c.column_default
            FROM information_schema.columns c
            WHERE c.table_schema = 'public'
                AND c.table_name = src_table
                AND c.column_name NOT IN (
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'audit'
                        AND table_name = src_table
                )
        LOOP
            EXECUTE format(
                'ALTER TABLE audit.%I ADD COLUMN IF NOT EXISTS %I %s%s%s',
                src_table,
                col.column_name,
                col.udt_name || COALESCE('(' || col.character_maximum_length || ')', ''),
                CASE WHEN col.is_nullable = 'NO' THEN ' NOT NULL' ELSE '' END,
                CASE WHEN col.column_default IS NOT NULL THEN ' DEFAULT ' || col.column_default ELSE '' END
            );
        END LOOP;

        -- DROP COLUMN: columns in audit (excluding audit_uid) not in public
        FOR col IN
            SELECT c.column_name
            FROM information_schema.columns c
            WHERE c.table_schema = 'audit'
                AND c.table_name = src_table
                AND c.column_name <> 'audit_uid'
                AND c.column_name NOT IN (
                    SELECT column_name
                    FROM information_schema.columns
                    WHERE table_schema = 'public'
                        AND table_name = src_table
                )
        LOOP
            EXECUTE format(
                'ALTER TABLE audit.%I DROP COLUMN IF EXISTS %I',
                src_table,
                col.column_name
            );
        END LOOP;

        -- ALTER COLUMN TYPE: columns where type differs between public and audit
        FOR col IN
            SELECT
                p.column_name,
                p.udt_name,
                p.character_maximum_length
            FROM information_schema.columns p
            JOIN information_schema.columns a
                ON a.table_schema = 'audit'
                AND a.table_name  = src_table
                AND a.column_name = p.column_name
            WHERE p.table_schema = 'public'
                AND p.table_name = src_table
                AND a.column_name <> 'audit_uid'
                AND (
                    p.udt_name <> a.udt_name
                    OR COALESCE(p.character_maximum_length, 0) <> COALESCE(a.character_maximum_length, 0)
                )
        LOOP
            EXECUTE format(
                'ALTER TABLE audit.%I ALTER COLUMN %I TYPE %s',
                src_table,
                col.column_name,
                col.udt_name || COALESCE('(' || col.character_maximum_length || ')', '')
            );
        END LOOP;

    END LOOP;
END;
$$;

CREATE EVENT TRIGGER alter_audit_table
ON ddl_command_end
WHEN TAG IN ('ALTER TABLE')
EXECUTE FUNCTION alter_audit_table();


DROP EVENT TRIGGER IF EXISTS drop_audit_table;
DROP FUNCTION IF EXISTS drop_audit_table();

CREATE OR REPLACE FUNCTION drop_audit_table()
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
        FROM pg_event_trigger_dropped_objects()
        WHERE object_type = 'table'
    LOOP
        src_schema := obj.schema_name;
        src_table  := obj.object_name;

        CONTINUE WHEN src_schema <> 'public';
        CONTINUE WHEN src_table = 'alembic_version';

        EXECUTE format(
            'DROP TABLE IF EXISTS audit.%I',
            src_table
        );
    END LOOP;
END;
$$;

CREATE EVENT TRIGGER drop_audit_table
ON sql_drop
WHEN TAG IN ('DROP TABLE')
EXECUTE FUNCTION drop_audit_table();
