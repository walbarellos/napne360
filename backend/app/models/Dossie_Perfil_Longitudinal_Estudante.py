import uuid
from sqlalchemy import String, Text, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.app.database import Base

class DossiePerfilLongitudinalEstudante(Base):
    __tablename__ = "dossie_perfil_longitudinal_estudante"

    id                    : Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_estudante          : Mapped[uuid.UUID]   = mapped_column(ForeignKey("estudante_dados_cadastrais.id"), unique=True, nullable=False)
    estilo_aprendizagem   : Mapped[str | None]  = mapped_column(String(100), nullable=True)
    perfil_cognitivo      : Mapped[str | None]  = mapped_column(Text, nullable=True)
    perfil_comportamental : Mapped[str | None]  = mapped_column(Text, nullable=True)
    observacoes_gerais    : Mapped[str | None]  = mapped_column(Text, nullable=True)
    criado_em             : Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em         : Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    estudante = relationship("EstudanteDadosCadastrais", back_populates="dossie")
