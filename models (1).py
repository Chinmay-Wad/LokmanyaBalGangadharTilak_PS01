from sqlalchemy import Column, Integer, String, Text, ForeignKey
from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)  # doctor / patient


class Prescription(Base):
    __tablename__ = "prescriptions"

    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey("users.id"))
    raw_text = Column(Text)
    extracted = Column(Text)