from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table, Enum
from database import Base
from sqlalchemy.orm import relationship
import uuid
import enum

# Association table for the many-to-many relationship between Role and Permission
role_permission_table = Table(
    'role_permissions',
    Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id'), primary_key=True),
    Column('permission_id', Integer, ForeignKey('permissions.id'), primary_key=True)
)


# Define the models that mapping the DB tables
class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(256), index=True)
    description = Column(String(2048))

    create_time = Column(DateTime, server_default=func.now())  
    update_time = Column(DateTime, onupdate=func.now())  

class UserStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(256), unique=True, index=True)
    email = Column(String(256), unique=True, index=True)
    hashed_password = Column(String(256))
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)

    customer_id = Column(Integer, ForeignKey("customers.id"))
    customer = relationship("Customer", back_populates="users")

    role_id = Column(Integer, ForeignKey("roles.id"))
    role = relationship("Role", back_populates="users")

    create_time = Column(DateTime, server_default=func.now())  
    update_time = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"{self.username}, {self.email}, {self.hashed_password}"

class Customer(Base):
    __tablename__ = "customers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True)
    description = Column(String(2048))
    uuid = Column(String(36), default=uuid.uuid4())
    users = relationship("User", back_populates="customer")

    create_time = Column(DateTime, server_default=func.now())  
    update_time = Column(DateTime, onupdate=func.now())  


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True)

    users = relationship("User", back_populates="role")

    # Relationship to permissions
    permissions = relationship(
        "Permission",
        secondary=role_permission_table,
        back_populates="roles"
    )

    create_time = Column(DateTime, server_default=func.now())
    update_time = Column(DateTime, onupdate=func.now())



class Permission(Base):
    __tablename__ = "permissions"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(256), unique=True, index=True)  # e.g., 'read', 'write', 'delete'
    
    # Relationship to roles
    roles = relationship(
        "Role", 
        secondary=role_permission_table, 
        back_populates="permissions"
    )

    create_time = Column(DateTime, server_default=func.now())  
    update_time = Column(DateTime, onupdate=func.now())  

