import csv
from connect import get_connection


def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS PhoneBook (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100),
            phone VARCHAR(20) UNIQUE
        )
    """)
    conn.commit()
    cur.close()
    conn.close()


def search_by_pattern(pattern):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if len(rows) == 0:
        print("nothing found")
    else:
        for r in rows:
            print(r)


def upsert_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL upsert_contact(%s, %s)", (name, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("done")


def update_contact(old_phone, new_name=None, new_phone=None):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL update_contact(%s, %s, %s)", (old_phone, new_name, new_phone))
    conn.commit()
    cur.close()
    conn.close()
    print("updated")


def bulk_insert(contacts):
    if len(contacts) == 0:
        print("no contacts")
        return
    data = [[name, phone] for name, phone in contacts]
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM bulk_insert_contacts(%s::TEXT[][])", (data,))
    rejected = cur.fetchall()
    conn.commit()
    cur.close()
    conn.close()
    print("inserted:", len(contacts) - len(rejected))
    if len(rejected) > 0:
        print("rejected:")
        for r in rejected:
            print(" ", r)


def import_csv(filepath):
    contacts = []
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            contacts.append((row['name'], row['phone']))
    print("importing", len(contacts), "rows...")
    bulk_insert(contacts)


def console_bulk_add():
    contacts = []
    while True:
        name = input("name (empty to stop): ").strip()
        if name == '':
            break
        phone = input("phone: ").strip()
        contacts.append((name, phone))
    if len(contacts) > 0:
        bulk_insert(contacts)
    else:
        print("nothing entered")


def show_page(page, page_size):
    offset = (page - 1) * page_size
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM get_contacts_page(%s, %s)", (page_size, offset))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    if len(rows) == 0:
        print("no more contacts")
        return False
    print(f"\npage {page}:")
    for r in rows:
        print(r)
    return True


def browse_pages():
    page = 1
    try:
        page_size = int(input("page size [5]: ").strip() or 5)
    except:
        page_size = 5
    while True:
        has_rows = show_page(page, page_size)
        if not has_rows:
            break
        nav = input("n=next p=prev q=quit: ").strip()
        if nav == 'n':
            page += 1
        elif nav == 'p':
            if page > 1:
                page -= 1
        elif nav == 'q':
            break


def delete_contact(username=None, phone=None):
    if username is None and phone is None:
        print("give me something to delete")
        return
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("CALL delete_contact(%s, %s)", (username, phone))
    conn.commit()
    cur.close()
    conn.close()
    print("deleted")


def menu():
    create_table()
    while True:
        print("\n1. browse")
        print("2. search")
        print("3. add new contact")
        print("4. update existing contact")
        print("5. bulk add from console")
        print("6. import csv")
        print("7. delete by phone")
        print("8. delete by name")
        print("0. exit")
        choice = input("pick: ")

        if choice == '1':
            browse_pages()
        elif choice == '2':
            pat = input("pattern: ")
            search_by_pattern(pat)
        elif choice == '3':
            name = input("name: ")
            phone = input("phone: ")
            upsert_contact(name, phone)
        elif choice == '4':
            old = input("current phone of contact to update: ")
            new_name = input("new name (leave empty to keep): ").strip() or None
            new_phone = input("new phone (leave empty to keep): ").strip() or None
            update_contact(old, new_name, new_phone)
        elif choice == '5':
            console_bulk_add()
        elif choice == '6':
            path = input("csv path [contacts.csv]: ") or "contacts.csv"
            import_csv(path)
        elif choice == '7':
            phone = input("phone: ")
            delete_contact(phone=phone)
        elif choice == '8':
            name = input("name: ")
            delete_contact(username=name)
        elif choice == '0':
            break
        else:
            print("invalid")


menu()
