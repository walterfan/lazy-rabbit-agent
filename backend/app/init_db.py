#!/usr/bin/env python3
import os, sys
from dotenv import load_dotenv
load_dotenv()
import argparse
from sqlalchemy.orm import Session
from datetime import datetime
from passlib.context import CryptContext

from database import SessionLocal, engine, Base

# Import all models
from user.models import User, Customer, Role, Permission, role_permission_table
from prompt.models import Prompt, Tag, PromptTag

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
pwd_of_admin = os.getenv("DB_PWD")
def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def init_db():
    db: Session = SessionLocal()
    # create all tables
    Base.metadata.create_all(bind=engine)
    try:
        # Check if any customers exist
        if db.query(Customer).first() is None:
            # Add default customer
            default_customer = Customer(name="Default Customer", uuid="00917908-33e0-4cb1-9b8d-64e420213f7b", description="Lazy Rabbit Studio")
            db.add(default_customer)

        # Check if any roles exist
        if db.query(Role).first() is None:
            # Add default role (Admin)
            default_role = Role(name="Admin")
            db.add(default_role)

        # Check if any permissions exist
        if db.query(Permission).first() is None:
            # Add default permissions
            default_permissions = [
                Permission(name="read"),
                Permission(name="write"),
                Permission(name="delete"),
                Permission(name="update"),
            ]
            db.add_all(default_permissions)
            db.commit()  # Commit the permissions first so we can associate them with the role

            # Associate all permissions with the default role (Admin)
            for permission in default_permissions:
                db.execute(role_permission_table.insert().values(role_id=default_role.id, permission_id=permission.id))

        # Check if any users exist
        if db.query(User).first() is None:
            # Add default user (Admin)
            default_user = User(
                username="admin",
                email="admin@fanyamin.com",
                hashed_password=get_password_hash(pwd_of_admin),
                create_time=datetime.now(),
                update_time=datetime.now(),
                customer_id=default_customer.id,  # Associate user with default customer
                role_id=default_role.id  # Associate user with default role
            )
            db.add(default_user)

        # Commit changes
        db.commit()

    except Exception as e:
        print(f"Error initializing the database: {e}")
        db.rollback()

    finally:
        db.close()


def add_user(username, password):
    db: Session = SessionLocal()

    try:
        default_customer = db.query(Customer).first()
        default_role = db.query(Role).first()

        user = db.query(User).filter(User.username==username).first()
        if user:
            print("user existed")
        else:
            print(f"Add {username}/{password}")
            new_user = User(
                username=username,
                email=f"{username}@fanyamin.com",
                hashed_password=get_password_hash(password),
                create_time=datetime.now(),
                update_time=datetime.now(),
                customer_id=default_customer.id,  # Associate user with default customer
                role_id=default_role.id  # Associate user with default role
            )
            db.add(new_user)
            db.commit()
            print(f"Add successfully for user: {username}")


    except Exception as e:
        print(f"Error initializing the database: {e}")
        db.rollback()

    finally:
        db.close()
def change_password(username, password):
    db: Session = SessionLocal()

    try:
        user = db.query(User).filter(User.username==username).first()
        if user:
            print(f"update {user} to {username}/{password}")
            # update password of the user
            user.hashed_password = get_password_hash(password)
            user.update_time = datetime.now()
            db.commit()
            print(f"Password updated successfully for user: {username}")
        else:
            print(f"User not found: {username}")

    except Exception as e:
        print(f"Error initializing the database: {e}")
        db.rollback()

    finally:
        db.close()

# Run the function to initialize the database
if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--action','-a', action='store', dest='action', help='specify action: init|change_password|add_user')
    parser.add_argument('--host', '-i', dest='host', default="192.168.104.226", help='db host')
    parser.add_argument('--port', '-p', dest='port', default="3306", help='db port')
    parser.add_argument('--user', '-u', dest='username', default="admin", help='specify username')
    parser.add_argument('--pass', '-s', dest='password', help='specify password')


    args = parser.parse_args()

    if (args.action == "init"):
        init_db()
    elif (args.action == "change_password"):
        change_password(args.username, args.password)
    elif (args.action == "add_user"):
        add_user(args.username, args.password)
    else:
        print("usage: ./init_db.py -a <init|change_password|add_user>")

        print("example: ")
        print("\t ./init_db.py -a init")
        print("\t ./init_db.py -a change_password -u admin -s xxxx")
        print("\t ./init_db.py -a add_user -u walter -s xxxx")
