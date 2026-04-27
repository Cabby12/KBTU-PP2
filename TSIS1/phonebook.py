import csv
import json
from connect import get_connection


def print_rows(rows):
    if len(rows) == 0:
        print("nothing found")
        return
    print(f"\n  {'ID':<4} {'Name':<20} {'Email':<25} {'Birthday':<12} {'Group':<10} Phones")
    print("  " + "-" * 90)
    for r in rows:
        cid, name, email, birthday, grp, phones = r
        print(f"  {str(cid):<4} {str(name or ''):<20} {str(email or ''):<25} {str(birthday or ''):<12} {str(grp or ''):<10} {phones or 'no phones'}")


def add_contact(name, email=None, birthday=None, group=None):
    conn = get_connection()
    cur = conn.cursor()
    try:
        group_id = None
        if group:
            cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group,))
            row = cur.fetchone()
            if row:
                group_id = row[0]
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING",
            (name, email, birthday, group_id)
        )
        conn.commit()
        print("added")
    except Exception as e:
        conn.rollback()
        print("error:", e)
    cur.close()
    conn.close()


def add_phone(name, phone, ptype):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL add_phone(%s, %s, %s)", (name, phone, ptype))
        conn.commit()
        print("phone added")
    except Exception as e:
        conn.rollback()
        print("error:", e)
    cur.close()
    conn.close()


def move_to_group(name, group):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("CALL move_to_group(%s, %s)", (name, group))
        conn.commit()
        print("moved")
    except Exception as e:
        conn.rollback()
        print("error:", e)
    cur.close()
    conn.close()


def search(query):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (query,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def filter_by_group(group_name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday, g.name,
               string_agg(p.phone || ' (' || COALESCE(p.type, '?') || ')', ', ')
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
        LEFT JOIN phones p ON p.contact_id = c.id
        WHERE g.name ILIKE %s
        GROUP BY c.id, c.name, c.email, c.birthday, g.name
        ORDER BY c.name
    """, (group_name,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    print_rows(rows)


def browse_pages():
    page = 1
    try:
        page_size = int(input("page size [5]: ").strip() or 5)
    except:
        page_size = 5
    sort = input("sort by (name/birthday/created_at) [name]: ").strip() or "name"
    if sort not in ("name", "birthday", "created_at"):
        sort = "name"

    while True:
        offset = (page - 1) * page_size
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM get_contacts_page(%s, %s, %s)", (page_size, offset, sort))
        rows = cur.fetchall()
        cur.close()
        conn.close()

        if len(rows) == 0:
            print("no more contacts")
            break

        print(f"\npage {page}:")
        print_rows(rows)

        nav = input("n=next p=prev q=quit: ").strip()
        if nav == 'n':
            page += 1
        elif nav == 'p':
            page = max(1, page - 1)
        elif nav == 'q':
            break


def export_json(filepath="contacts.json"):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT c.id, c.name, c.email, c.birthday::text, g.name
        FROM contacts c
        LEFT JOIN groups g ON g.id = c.group_id
    """)
    contacts = cur.fetchall()
    result = []
    for c in contacts:
        cid, name, email, birthday, grp = c
        cur.execute("SELECT phone, type FROM phones WHERE contact_id = %s", (cid,))
        phones = [{"phone": r[0], "type": r[1]} for r in cur.fetchall()]
        result.append({"name": name, "email": email, "birthday": birthday, "group": grp, "phones": phones})
    cur.close()
    conn.close()
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print("exported", len(result), "contacts to", filepath)


def import_json(filepath="contacts.json"):
    with open(filepath, encoding="utf-8") as f:
        data = json.load(f)
    conn = get_connection()
    cur = conn.cursor()
    for c in data:
        name = c.get("name")
        cur.execute("SELECT id FROM contacts WHERE name ILIKE %s", (name,))
        existing = cur.fetchone()
        if existing:
            ans = input(f"'{name}' already exists. overwrite? (y/n): ").strip().lower()
            if ans != 'y':
                print("skipped", name)
                continue
            cur.execute("DELETE FROM contacts WHERE name ILIKE %s", (name,))
            conn.commit()
        group_id = None
        if c.get("group"):
            cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (c["group"],))
            row = cur.fetchone()
            if row:
                group_id = row[0]
            else:
                cur.execute("INSERT INTO groups (name) VALUES (%s) RETURNING id", (c["group"],))
                group_id = cur.fetchone()[0]
        cur.execute(
            "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) RETURNING id",
            (name, c.get("email"), c.get("birthday"), group_id)
        )
        cid = cur.fetchone()[0]
        for p in c.get("phones", []):
            cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                        (cid, p["phone"], p["type"]))
        conn.commit()
        print("imported", name)
    cur.close()
    conn.close()


def import_csv(filepath="contacts.csv"):
    conn = get_connection()
    cur = conn.cursor()
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name     = row.get("name", "").strip()
            email    = row.get("email", "").strip() or None
            birthday = row.get("birthday", "").strip() or None
            group    = row.get("group", "").strip() or None
            phone    = row.get("phone", "").strip() or None
            ptype    = row.get("phone_type", "mobile").strip() or "mobile"
            if not name:
                continue
            group_id = None
            if group:
                cur.execute("SELECT id FROM groups WHERE name ILIKE %s", (group,))
                r = cur.fetchone()
                group_id = r[0] if r else None
            try:
                cur.execute(
                    "INSERT INTO contacts (name, email, birthday, group_id) VALUES (%s, %s, %s, %s) ON CONFLICT (name) DO NOTHING RETURNING id",
                    (name, email, birthday, group_id)
                )
                result = cur.fetchone()
                if result and phone:
                    cur.execute("INSERT INTO phones (contact_id, phone, type) VALUES (%s, %s, %s)",
                                (result[0], phone, ptype))
                conn.commit()
            except Exception as e:
                conn.rollback()
                print("error on row", name, e)
    cur.close()
    conn.close()
    print("csv import done")


def delete_contact(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM contacts WHERE name ILIKE %s", (name,))
    conn.commit()
    cur.close()
    conn.close()
    print("deleted")


def update_contact(old_name, new_name=None, new_email=None, new_birthday=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT id FROM contacts WHERE name ILIKE %s", (old_name,))
    row = cur.fetchone()
    if not row:
        print("contact not found:", old_name)
        cur.close()
        conn.close()
        return
    cid = row[0]
    try:
        if new_name:
            cur.execute("UPDATE contacts SET name = %s WHERE id = %s", (new_name, cid))
        if new_email:
            cur.execute("UPDATE contacts SET email = %s WHERE id = %s", (new_email, cid))
        if new_birthday:
            cur.execute("UPDATE contacts SET birthday = %s WHERE id = %s", (new_birthday, cid))
        conn.commit()
        print("updated")
    except Exception as e:
        conn.rollback()
        print("error:", e)
    cur.close()
    conn.close()


def menu():
    while True:
        print("\n1.  browse / sort")
        print("2.  search (name / email / phone)")
        print("3.  filter by group")
        print("4.  add contact")
        print("5.  add phone to contact")
        print("6.  move contact to group")
        print("7.  update contact")
        print("8.  delete contact")
        print("9.  import csv")
        print("10. export json")
        print("11. import json")
        print("0.  exit")
        choice = input("pick: ").strip()

        if choice == '1':
            browse_pages()
        elif choice == '2':
            q = input("search: ").strip()
            search(q)
        elif choice == '3':
            g = input("group (Family/Work/Friend/Other): ").strip()
            filter_by_group(g)
        elif choice == '4':
            name     = input("name: ").strip()
            email    = input("email (optional): ").strip() or None
            birthday = input("birthday YYYY-MM-DD (optional): ").strip() or None
            group    = input("group (Family/Work/Friend/Other): ").strip() or None
            add_contact(name, email, birthday, group)
        elif choice == '5':
            name  = input("contact name: ").strip()
            phone = input("phone: ").strip()
            ptype = input("type (home/work/mobile): ").strip() or "mobile"
            add_phone(name, phone, ptype)
        elif choice == '6':
            name  = input("contact name: ").strip()
            group = input("group name: ").strip()
            move_to_group(name, group)
        elif choice == '7':
            old      = input("name of contact to update: ").strip()
            new_name = input("new name (leave empty to keep): ").strip() or None
            new_email    = input("new email (leave empty to keep): ").strip() or None
            new_birthday = input("new birthday (leave empty to keep): ").strip() or None
            update_contact(old, new_name, new_email, new_birthday)
        elif choice == '8':
            name = input("name to delete: ").strip()
            delete_contact(name)
        elif choice == '9':
            path = input("csv path [contacts.csv]: ").strip() or "contacts.csv"
            import_csv(path)
        elif choice == '10':
            path = input("json path [contacts.json]: ").strip() or "contacts.json"
            export_json(path)
        elif choice == '11':
            path = input("json path [contacts.json]: ").strip() or "contacts.json"
            import_json(path)
        elif choice == '0':
            break
        else:
            print("invalid")


menu()
