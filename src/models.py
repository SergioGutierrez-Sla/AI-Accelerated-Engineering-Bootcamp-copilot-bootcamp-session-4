from sqlalchemy import Column, ForeignKey, Integer, JSON, String, UniqueConstraint
from sqlalchemy.orm import relationship

from database import Base


class Capability(Base):
    __tablename__ = "capabilities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String, nullable=False)
    practice_area = Column(String, nullable=False)
    skill_levels = Column(JSON, nullable=False)
    certifications = Column(JSON, nullable=False)
    industry_verticals = Column(JSON, nullable=False)
    capacity = Column(Integer, nullable=False)

    consultants = relationship(
        "CapabilityConsultant",
        back_populates="capability",
        cascade="all, delete-orphan",
    )


class CapabilityConsultant(Base):
    __tablename__ = "capability_consultants"
    __table_args__ = (
        UniqueConstraint("capability_id", "email", name="uq_capability_consultant"),
    )

    id = Column(Integer, primary_key=True, index=True)
    capability_id = Column(Integer, ForeignKey("capabilities.id", ondelete="CASCADE"), nullable=False, index=True)
    email = Column(String, nullable=False)

    capability = relationship("Capability", back_populates="consultants")