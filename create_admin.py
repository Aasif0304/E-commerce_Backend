import sys
import os

# Prevent Cython DLL issues on Windows
os.environ["DISABLE_SQLALCHEMY_CEXT"] = "1"

from database import SessionLocal
from models.user_model import User
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

def make_admin(email="admin@ecommerce.com", password="admin123", name="Super Admin"):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            user.role = "ADMIN"
            if password:
                user.hashed_password = password_hash.hash(password)
            db.commit()
            print(f"SUCCESS: Existing user '{email}' updated to role 'ADMIN'!")
        else:
            new_user = User(
                name=name,
                email=email,
                hashed_password=password_hash.hash(password),
                role="ADMIN",
            )
            db.add(new_user)
            db.commit()
            print(f"SUCCESS: Created new admin user '{email}' with password '{password}'!")
    except Exception as e:
        print(f"ERROR: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    email = sys.argv[1] if len(sys.argv) > 1 else "admin@ecommerce.com"
    pwd = sys.argv[2] if len(sys.argv) > 2 else "admin123"
    name = sys.argv[3] if len(sys.argv) > 3 else "Store Admin"
    make_admin(email, pwd, name)

