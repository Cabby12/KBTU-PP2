CREATE OR REPLACE FUNCTION search_contacts(p_query TEXT)
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, grp VARCHAR, phones TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT DISTINCT c.id, c.name, c.email, c.birthday, g.name,
               string_agg(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g  ON g.id = c.group_id
        LEFT JOIN phones p  ON p.contact_id = c.id
        WHERE c.name  ILIKE '%' || p_query || '%'
           OR c.email ILIKE '%' || p_query || '%'
           OR p.phone  LIKE '%' || p_query || '%'
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name;
END;
$$;

CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT, p_sort TEXT DEFAULT 'name')
RETURNS TABLE(id INT, name VARCHAR, email VARCHAR, birthday DATE, grp VARCHAR, phones TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY EXECUTE format(
        'SELECT c.id, c.name, c.email, c.birthday, g.name,
                string_agg(p.phone || '' ('' || COALESCE(p.type, ''?'') || '')'', '', '')
         FROM contacts c
         LEFT JOIN groups g ON g.id = c.group_id
         LEFT JOIN phones p ON p.contact_id = c.id
         GROUP BY c.id, c.name, c.email, c.birthday, g.name
         ORDER BY c.%I
         LIMIT %s OFFSET %s',
        p_sort, p_limit, p_offset
    );
END;
$$;

CREATE OR REPLACE PROCEDURE add_phone(p_contact_name VARCHAR, p_phone VARCHAR, p_type VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_id INT;
BEGIN
    SELECT id INTO v_id FROM contacts WHERE name ILIKE p_contact_name;
    IF v_id IS NULL THEN
        RAISE NOTICE 'contact not found: %', p_contact_name;
        RETURN;
    END IF;
    INSERT INTO phones (contact_id, phone, type) VALUES (v_id, p_phone, p_type);
END;
$$;

CREATE OR REPLACE PROCEDURE move_to_group(p_contact_name VARCHAR, p_group_name VARCHAR)
LANGUAGE plpgsql AS $$
DECLARE
    v_contact_id INT;
    v_group_id   INT;
BEGIN
    SELECT id INTO v_contact_id FROM contacts WHERE name ILIKE p_contact_name;
    IF v_contact_id IS NULL THEN
        RAISE NOTICE 'contact not found: %', p_contact_name;
        RETURN;
    END IF;
    SELECT id INTO v_group_id FROM groups WHERE name ILIKE p_group_name;
    IF v_group_id IS NULL THEN
        INSERT INTO groups (name) VALUES (p_group_name) RETURNING id INTO v_group_id;
    END IF;
    UPDATE contacts SET group_id = v_group_id WHERE id = v_contact_id;
END;
$$;
