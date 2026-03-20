import uuid, enum
from sqlalchemy import Boolean, ForeignKey, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.app.database import Base

class CategoriaEntrevista(str, enum.Enum):
    desenvolvimento = "desenvolvimento"
    escolarizacao   = "escolarizacao"
    comportamento   = "comportamento"
    saude           = "saude"

class EntrevistaEstruturadaSessao(Base):
    __tablename__ = "entrevista_estruturada_sessao"

    id                 : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_dossie          : Mapped[uuid.UUID] = mapped_column(ForeignKey("dossie_perfil_longitudinal_estudante.id"), nullable=False)
    id_entrevistador   : Mapped[uuid.UUID] = mapped_column(ForeignKey("usuario_perfil_acesso.id"), nullable=False)
    concluida          : Mapped[bool]      = mapped_column(Boolean, default=False)
    observacoes_finais : Mapped[str|None]  = mapped_column(Text, nullable=True)
    criado_em          : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    respostas  = relationship("EntrevistaRespostaPorCategoria", backref="sessao", cascade="all, delete-orphan")
    hipoteses  = relationship("HipoteseDiagnosticaGerada", backref="sessao", cascade="all, delete-orphan")
