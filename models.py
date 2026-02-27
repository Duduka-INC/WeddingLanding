from datetime import datetime
from typing import Optional, List

from sqlalchemy import String, Integer, Text, DateTime, Boolean, func, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from db import Base


class Rsvp(Base):
    __tablename__ = "rsvp"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    attending: Mapped[bool] = mapped_column(Boolean, nullable=False)  # True = да, False = нет
    hot_dish: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "fish" | "meat"
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    drinks: Mapped[List["RsvpDrink"]] = relationship("RsvpDrink", back_populates="rsvp", cascade="all, delete-orphan")


class RsvpDrink(Base):
    __tablename__ = "rsvp_drinks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    rsvp_id: Mapped[int] = mapped_column(ForeignKey("rsvp.id", ondelete="CASCADE"), nullable=False, index=True)
    drink: Mapped[str] = mapped_column(String(100), nullable=False)  # например "Шампанское", "Вино красное"

    rsvp: Mapped["Rsvp"] = relationship("Rsvp", back_populates="drinks")


class Event(Base):
    __tablename__ = "event"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    event_name: Mapped[str] = mapped_column(String(100), index=True)
    element_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    page: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    session_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
