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


DO $$
DECLARE
    tbl text;
BEGIN
    FOR tbl IN
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
            AND table_type = 'BASE TABLE'
            AND table_name <> 'alembic_version'
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS insert_audit_row ON public.%I;
            CREATE TRIGGER insert_audit_row
            AFTER INSERT OR UPDATE ON public.%I
            FOR EACH ROW
            EXECUTE FUNCTION insert_audit_row();',
            tbl, tbl
        );
    END LOOP;
END;
$$;
