import uuid
from sqlalchemy import Boolean, ForeignKey, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.app.database import Base

class ConsentimentoLGPDEstudante(Base):
    __tablename__ = "consentimento_lgpd_estudante"

    id                 : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_matricula       : Mapped[uuid.UUID] = mapped_column(ForeignKey("matricula_entrada_sistema.id"), nullable=False)
    versao_termo       : Mapped[str]       = mapped_column(String(20), nullable=False, default="2025.1")
    consentido         : Mapped[bool]      = mapped_column(Boolean, nullable=False)
    ip_origem          : Mapped[str|None]  = mapped_column(String(45), nullable=True)  # IPv4/IPv6
    hash_documento     : Mapped[str|None]  = mapped_column(String(64), nullable=True)  # SHA-256 do termo
    data_consentimento : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    matricula = relationship("MatriculaEntradaSistema", backref="consentimentos")
