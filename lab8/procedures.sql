CREATE TABLE IF NOT EXISTS PhoneBook (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    phone VARCHAR(20) UNIQUE
);

CREATE OR REPLACE FUNCTION search_contacts(p_pattern TEXT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM PhoneBook pb
        WHERE pb.name ILIKE '%' || p_pattern || '%'
        OR pb.phone LIKE '%' || p_pattern || '%';
END;
$$;

CREATE OR REPLACE PROCEDURE upsert_contact(p_name TEXT, p_phone TEXT)
LANGUAGE plpgsql AS $$
BEGIN
    INSERT INTO PhoneBook (name, phone) VALUES (p_name, p_phone)
    ON CONFLICT (phone) DO UPDATE SET name = EXCLUDED.name;
END;
$$;

CREATE OR REPLACE PROCEDURE update_contact(p_old_phone TEXT, p_new_name TEXT DEFAULT NULL, p_new_phone TEXT DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_new_name IS NOT NULL THEN
        UPDATE PhoneBook SET name = p_new_name WHERE phone = p_old_phone;
    END IF;
    IF p_new_phone IS NOT NULL THEN
        UPDATE PhoneBook SET phone = p_new_phone WHERE phone = p_old_phone;
    END IF;
END;
$$;

CREATE OR REPLACE FUNCTION bulk_insert_contacts(p_data TEXT[][])
RETURNS TABLE(rejected_name TEXT, rejected_phone TEXT, reason TEXT)
LANGUAGE plpgsql AS $$
DECLARE
    i INT;
    v_name TEXT;
    v_phone TEXT;
BEGIN
    FOR i IN 1 .. array_length(p_data, 1) LOOP
        v_name := p_data[i][1];
        v_phone := p_data[i][2];

        IF v_name IS NULL OR trim(v_name) = '' THEN
            rejected_name := v_name;
            rejected_phone := v_phone;
            reason := 'name is empty';
            RETURN NEXT;
            CONTINUE;
        END IF;

        IF v_phone !~ '^[+]?[0-9 \-(]{7,20}$' THEN
            rejected_name := v_name;
            rejected_phone := v_phone;
            reason := 'invalid phone';
            RETURN NEXT;
            CONTINUE;
        END IF;

        CALL upsert_contact(trim(v_name), trim(v_phone));
    END LOOP;
END;
$$;

CREATE OR REPLACE FUNCTION get_contacts_page(p_limit INT, p_offset INT)
RETURNS TABLE(id INT, name VARCHAR, phone VARCHAR)
LANGUAGE plpgsql AS $$
BEGIN
    RETURN QUERY
        SELECT pb.id, pb.name, pb.phone
        FROM PhoneBook pb
        ORDER BY pb.name
        LIMIT p_limit OFFSET p_offset;
END;
$$;

CREATE OR REPLACE PROCEDURE delete_contact(p_username TEXT DEFAULT NULL, p_phone TEXT DEFAULT NULL)
LANGUAGE plpgsql AS $$
BEGIN
    IF p_phone IS NOT NULL THEN
        DELETE FROM PhoneBook WHERE phone = p_phone;
    END IF;
    IF p_username IS NOT NULL THEN
        DELETE FROM PhoneBook WHERE name ILIKE '%' || p_username || '%';
    END IF;
END;
$$;
