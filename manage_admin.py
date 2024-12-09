from app import app, db, bcrypt
from models import Admin
from getpass import getpass

def check_admin_credentials():
    username = input("Enter admin username: ")
    password = getpass("Enter admin password: ")

    with app.app_context():  # Ensure the app context is available
        admin = Admin.query.filter_by(username=username).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        print("Admin credentials are valid.")
    else:
        print("Invalid credentials. Please try again.")

def check_password_match():
    username = input("Enter admin username: ")
    password = getpass("Enter admin password: ")

    with app.app_context():  # Ensure the app context is available
        admin = Admin.query.filter_by(username=username).first()

    if admin and bcrypt.check_password_hash(admin.password, password):
        print("Password matches the admin credentials.")
    else:
        print("Password does not match or admin not found.")

def add_admin():
    username = input("Enter new admin username: ")
    password = getpass("Enter new password: ")

    with app.app_context():  # Ensure the app context is available
        # Check if admin with the same username already exists
        existing_admin = Admin.query.filter_by(username=username).first()

        if existing_admin:
            print(f"Admin with username '{username}' already exists.")
            return

        # Create a new admin user with hashed password
        hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
        new_admin = Admin(username=username, password=hashed_password)

        try:
            db.session.add(new_admin)
            db.session.commit()
            print(f"New admin '{username}' created successfully.")
        except Exception as e:
            print(f"Error adding new admin: {e}")
            db.session.rollback()

def update_admin_password():
    username = input("Enter admin username whose password you want to update: ")

    with app.app_context():  # Ensure the app context is available
        admin = Admin.query.filter_by(username=username).first()
    if admin:
        new_password = getpass("Enter new password: ")
        hashed_password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        admin.password = hashed_password
        try:
            db.session.commit()
            print(f"Password for admin '{username}' updated successfully.")
        except Exception as e:
            print(f"Error updating password: {e}")
            db.session.rollback()
    else:
        print(f"No admin found with username '{username}'.")

def show_admins():
    with app.app_context():  # Ensure the app context is available
        try:
            admins = Admin.query.all()
            if not admins:
                print("No admins found in the database.")
            else:
                print("List of all admin credentials:")
                for admin in admins:
                    # Showing both username and hashed password
                    print(f"Username: {admin.username}, Password (hashed): {admin.password}")
        except Exception as e:
            print(f"Error fetching admins: {e}")

def main():
    while True:
        print("Admin Management System")
        print("1. Check admin credentials")
        print("2. Check if password matches")
        print("3. Add new admin")
        print("4. Update admin password")
        print("5. Show list of admin credentials")
        print("6. Exit")

        choice = input("Enter your choice (1/2/3/4/5/6): ")

        if choice == '1':
            check_admin_credentials()
        elif choice == '2':
            check_password_match()
        elif choice == '3':
            add_admin()
        elif choice == '4':
            update_admin_password()
        elif choice == '5':
            show_admins()
        elif choice == '6':
            print("Exiting the system.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == '__main__':
    main()
