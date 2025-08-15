from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func, Table, Enum
from database import Base
from sqlalchemy.orm import relationship
import uuid
import enum

# Association table for the many-to-many relationship between Role and Permission
role_permission_table = Table(
    'role_permission',
    Base.metadata,
    Column('role_id', String(256), ForeignKey('role.id'), primary_key=True),
    Column('permission_id', String(256), ForeignKey('permission.id'), primary_key=True)
)

class BaseObject(Base):
    __abstract__ = True
    """Base object with UUID primary key"""
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    created_by = Column(String(256), index=True)
    updated_by = Column(String(256), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

    def __repr__(self):
        return f"{self.__class__.__name__}(id={self.id}, created_at={self.created_at})"


class Realm(BaseObject):
    __tablename__ = "realm"

    name = Column(String(256), unique=True, index=True)
    description = Column(String(2048))
    users = relationship("User", back_populates="realm")

# Define the models that mapping the DB tables
class Task(BaseObject):
    __tablename__ = "task"

    title = Column(String(256), index=True)
    description = Column(String(2048))
    realm_id = Column(String(36), ForeignKey("realm.id"))

    deadline = Column(DateTime)
    schedule_time = Column(DateTime)
    start_time = Column(DateTime)
    end_time = Column(DateTime)


class UserStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class User(BaseObject):
    __tablename__ = "user"

    username = Column(String(256), unique=True, index=True)
    email = Column(String(256), unique=True, index=True)
    hashed_password = Column(String(256))
    status = Column(Enum(UserStatus), default=UserStatus.PENDING)

    role_id = Column(String(36), ForeignKey("role.id"))
    role = relationship("Role", back_populates="users")

    realm_id = Column(String(36), ForeignKey("realm.id"))
    realm = relationship("Realm", back_populates="users")

    customer_id = Column(String(36), ForeignKey("customer.id"))
    customer = relationship("Customer", back_populates="users")

    def __repr__(self):
        return f"{self.username}, {self.email}, {self.hashed_password}"

class Customer(BaseObject):
    __tablename__ = "customer"

    name = Column(String(256), unique=True, index=True)
    description = Column(String(2048))
    uuid = Column(String(36), default=uuid.uuid4())
    users = relationship("User", back_populates="customer")

    realm_id = Column(String(36), ForeignKey("realm.id"))


class Role(BaseObject):
    __tablename__ = "role"

    name = Column(String(256), unique=True, index=True)

    users = relationship("User", back_populates="role")

    # Relationship to permissions
    permissions = relationship(
        "Permission",
        secondary=role_permission_table,
        back_populates="roles"
    )

    realm_id = Column(String(36), ForeignKey("realm.id"))



class Permission(BaseObject):
    __tablename__ = "permission"

    name = Column(String(256), unique=True, index=True)  # e.g., 'read', 'write', 'delete'
    
    # Relationship to roles
    roles = relationship(
        "Role",
        secondary=role_permission_table,
        back_populates="permissions"
    )

    realm_id = Column(String(36), ForeignKey("realm.id"))

