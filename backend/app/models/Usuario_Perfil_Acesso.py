import uuid
from sqlalchemy import String, Boolean, Enum as SAEnum, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
import enum
from backend.app.database import Base

class PerfilUsuario(str, enum.Enum):
    napne    = "napne"
    docente  = "docente"
    gestao   = "gestao"
    admin    = "admin"

class UsuarioPerfilAcesso(Base):
    __tablename__ = "usuario_perfil_acesso"

    id            : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matricula     : Mapped[str]       = mapped_column(String(20), unique=True, nullable=False)
    nome          : Mapped[str]       = mapped_column(String(200), nullable=False)
    cpf           : Mapped[str]       = mapped_column(String(11), unique=True, nullable=False)
    email         : Mapped[str]       = mapped_column(String(150), unique=True, nullable=False)
    senha_hash    : Mapped[str]       = mapped_column(String(255), nullable=False)
    perfil        : Mapped[PerfilUsuario] = mapped_column(SAEnum(PerfilUsuario), nullable=False)
    ativo         : Mapped[bool]      = mapped_column(Boolean, default=True)
    criado_em     : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
