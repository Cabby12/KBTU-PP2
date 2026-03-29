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

def add_contact(name, phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO PhoneBook (name, phone) VALUES (%s, %s) ON CONFLICT (phone) DO NOTHING", (name, phone))
    conn.commit()
    cur.close()
    conn.close()

def import_csv(filepath):
    with open(filepath, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            add_contact(row['name'], row['phone'])
    print("done importing")

def console_add():
    while True:
        name = input("name (or 'q' to stop): ")
        if name == 'q':
            break
        phone = input("phone: ")
        add_contact(name, phone)
        print("saved")

def search(name=None, phone=None):
    conn = get_connection()
    cur = conn.cursor()
    if name and phone:
        cur.execute("SELECT * FROM PhoneBook WHERE name ILIKE %s AND phone LIKE %s", (f'%{name}%', f'%{phone}%'))
    elif name:
        cur.execute("SELECT * FROM PhoneBook WHERE name ILIKE %s", (f'%{name}%',))
    elif phone:
        cur.execute("SELECT * FROM PhoneBook WHERE phone LIKE %s", (f'%{phone}%',))
    else:
        cur.execute("SELECT * FROM PhoneBook")
    rows = cur.fetchall()
    for r in rows:
        print(r)
    cur.close()
    conn.close()

def update_contact(old_phone, new_name=None, new_phone=None):
    conn = get_connection()
    cur = conn.cursor()
    if new_name:
        cur.execute("UPDATE PhoneBook SET name = %s WHERE phone = %s", (new_name, old_phone))
    if new_phone:
        cur.execute("UPDATE PhoneBook SET phone = %s WHERE phone = %s", (new_phone, old_phone))
    conn.commit()
    cur.close()
    conn.close()
    print("updated")

def delete_by_phone(phone):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM PhoneBook WHERE phone = %s", (phone,))
    conn.commit()
    cur.close()
    conn.close()
    print("deleted")

def delete_by_name(name):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM PhoneBook WHERE name ILIKE %s", (f'%{name}%',))
    conn.commit()
    cur.close()
    conn.close()
    print("deleted")

def menu():
    create_table()
    while True:
        print("\n1. show all")
        print("2. search")
        print("3. add from console")
        print("4. import csv")
        print("5. update")
        print("6. delete by phone")
        print("7. delete by name")
        print("0. exit")
        choice = input("pick: ")

        if choice == '1':
            search()
        elif choice == '2':
            n = input("name (leave empty to skip): ") or None
            p = input("phone (leave empty to skip): ") or None
            search(n, p)
        elif choice == '3':
            console_add()
        elif choice == '4':
            f = input("csv path [contacts.csv]: ") or "contacts.csv"
            import_csv(f)
        elif choice == '5':
            old = input("current phone: ")
            n = input("new name (skip): ") or None
            p = input("new phone (skip): ") or None
            update_contact(old, n, p)
        elif choice == '6':
            delete_by_phone(input("phone: "))
        elif choice == '7':
            delete_by_name(input("name: "))
        elif choice == '0':
            break

menu()

