from database.database import Base
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String(50), nullable=False, unique=True)
    email = Column(String(100), nullable=False, unique=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False)


class Target(Base):
    __tablename__ = 'targets'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    ip_address = Column(String(100), nullable=False, unique=True)
    domain = Column(String(100), nullable=False, unique=True) # Виправлено орфографію
    description = Column(String(255))
    pentester_id = Column(Integer, ForeignKey('users.id'))

    pentester = relationship('User', backref="targets")
    vulnerabilities = relationship('TargetVulnerability', back_populates="target")


class Vulnerability(Base):
    __tablename__ = 'vulnerabilities'

    id = Column(Integer, primary_key=True, autoincrement=True, index=True)
    name_en = Column(Text, nullable=True)
    name_uk = Column(Text, nullable=True)
    description_en = Column(Text)
    description_uk = Column(Text)

    targets = relationship('TargetVulnerability', back_populates="vulnerability")


class TargetVulnerability(Base):
    __tablename__ = 'target_vulnerabilities'

    target_id = Column(Integer, ForeignKey("targets.id"), primary_key=True)
    vulnerability_id = Column(Integer, ForeignKey("vulnerabilities.id"), primary_key=True) # З маленької літери

    severity = Column(String(20), nullable=False)

    target = relationship("Target", back_populates="vulnerabilities")
    vulnerability = relationship("Vulnerability", back_populates="targets")