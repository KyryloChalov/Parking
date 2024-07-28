from datetime import datetime, date
import enum
from typing import Optional
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import (
    Integer,
    String,
    func,
    Enum,
    ForeignKey,
    Boolean,
    Date
)

from sqlalchemy.sql.sqltypes import DateTime
from sqlalchemy_utils import EmailType

from sqlalchemy.orm import DeclarativeBase

from src.conf.constants import (
    USERNAME_MAX_LENGTH,
    NAME_MAX_LENGTH,
    EMAIL_MAX_LENGTH,
    PASSWORD_MAX_LENGTH,
    TOKEN_MAX_LENGTH,
    LICENSE_PLATE_MAX_LENGTH,
    RATE_NAME_MAX_LENGHT,
    COMMENT_MAX_LENGTH,
    MESSAGE_MAX_LENGTH
)


class Base(DeclarativeBase): ...

class Setting (Base):
    __tablename__ = "settings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    capacity: Mapped[int] = mapped_column(Integer, nullable = False) # ємкість стоянки 
    num_days_reminder: Mapped[int] = mapped_column(Integer, nullable = True) # перевіряти чи є оплата, і відсилати листа з нагадуванням
    num_days_benefit: Mapped[int] = mapped_column(Integer, nullable = True) # кількість днів, коли ми ще пускаємо на стоянку користувача, якщо не оплачено

class Role(enum.Enum):
    admin: str = "admin"
    user: str = "user"
    operator: str = "operator"

class Datefield:
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    updated_at: Mapped[date] = mapped_column(
        "updated_at", DateTime, onupdate=func.now(), nullable=True
    )

class Rate(Base, Datefield):
    __tablename__ = "rates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    rate_name: Mapped[str] = mapped_column(String(RATE_NAME_MAX_LENGHT), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)

class User(Base, Datefield):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(NAME_MAX_LENGTH), nullable=True)
    username: Mapped[str] = mapped_column(
        String(USERNAME_MAX_LENGTH), nullable=False, unique=True
    )
    email: Mapped[str] = mapped_column(
        String(EMAIL_MAX_LENGTH), nullable=False, unique=True
    )
    password: Mapped[str] = mapped_column(String(PASSWORD_MAX_LENGTH), nullable=False)
    refresh_token: Mapped[str] = mapped_column(String(TOKEN_MAX_LENGTH), nullable=True)
    role: Mapped[Enum] = mapped_column(
        "role", Enum(Role), default=Role.user, nullable=False
    )
    confirmed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=True)
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle", backref="users"
    )
    blacklist: Mapped["Blacklist"] = relationship(
        "Blacklist", backref="users")


class Vehicle(Base, Datefield):
    __tablename__ = "vehicles"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    license_plate: Mapped[str] = mapped_column(
        String(LICENSE_PLATE_MAX_LENGTH), nullable=False, unique=True
    )
    ended_at: Mapped[date] = mapped_column(Date, nullable=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=True)
    rate_id:  Mapped[int] = mapped_column(
        ForeignKey("rates.id"), nullable=False
    )


class Blacklist(Base, Datefield):
    __tablename__ = "blacklists"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False
    )
    reason: Mapped[str] = mapped_column(String(COMMENT_MAX_LENGTH), nullable=False)
    vehicle: Mapped["Vehicle"] = relationship(
        "Vehicle", backref="blacklists"
    )
    # user: Mapped["User"] = relationship(
    #     "User", backref="blacklists"
    # )
    
class Notification(Base, Datefield):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False
    )
    message: Mapped[str] = mapped_column(String(MESSAGE_MAX_LENGTH), nullable=False)

class Parking_session(Base, Datefield):
    __tablename__ = "sessions"
    id:  Mapped[int] = mapped_column(Integer, primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False
    )

class Payment(Base):
    __tablename__ = "payments"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False
    )
    vehicle_id: Mapped[int] = mapped_column(
        ForeignKey("vehicles.id"), nullable=False
    )
    session_id: Mapped[int] = mapped_column(
        ForeignKey("sessions.id"), nullable=True
        #  може бути оплата за місяць
    )
    created_at: Mapped[date] = mapped_column("created_at", DateTime, default=func.now())
    amount: Mapped[int] = mapped_column(Integer, nullable=False)