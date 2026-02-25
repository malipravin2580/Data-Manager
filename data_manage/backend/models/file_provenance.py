from sqlalchemy import JSON, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


class FileProvenance(Base):
    __tablename__ = "file_provenance"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1000), nullable=False, index=True)
    source_file_path = Column(String(1000), nullable=True, index=True)
    transformation_type = Column(String(50), nullable=False)
    transformation_details = Column(JSON, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    creator = relationship("User", foreign_keys=[created_by])


class FileAccessLog(Base):
    __tablename__ = "file_access_logs"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1000), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    action = Column(String(50), nullable=False)
    ip_address = Column(String(50), nullable=True)
    user_agent = Column(String(500), nullable=True)
    details = Column(JSON, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")


class PermissionAuditLog(Base):
    __tablename__ = "permission_audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String(1000), nullable=False, index=True)
    action = Column(String(50), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    old_permission = Column(String(20), nullable=True)
    new_permission = Column(String(20), nullable=True)
    performed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    performer = relationship("User", foreign_keys=[performed_by])
    target_user = relationship("User", foreign_keys=[target_user_id])
