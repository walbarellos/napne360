import uuid
from sqlalchemy import Boolean, ForeignKey, SmallInteger, Text, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.app.database import Base

class HipoteseDiagnosticaGerada(Base):
    __tablename__ = "hipotese_diagnostica_gerada"

    id                : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_entrevista     : Mapped[uuid.UUID] = mapped_column(ForeignKey("entrevista_estruturada_sessao.id"), nullable=False)
    descricao         : Mapped[str]       = mapped_column(Text, nullable=False)
    confianca         : Mapped[int]       = mapped_column(SmallInteger, default=0)  # 0-100
    confirmada        : Mapped[bool|None] = mapped_column(Boolean, nullable=True)   # None=pendente
    id_confirmado_por : Mapped[uuid.UUID|None] = mapped_column(ForeignKey("usuario_perfil_acesso.id"), nullable=True)
    criado_em         : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
