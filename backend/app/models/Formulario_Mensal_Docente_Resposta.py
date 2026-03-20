import uuid
from sqlalchemy import Boolean, ForeignKey, Text, DateTime, Numeric, SmallInteger, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone, date
from backend.app.database import Base

class FormularioMensalDocenteResposta(Base):
    __tablename__ = "formulario_mensal_docente_resposta"

    id                      : Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_matricula            : Mapped[uuid.UUID]  = mapped_column(ForeignKey("matricula_entrada_sistema.id"), nullable=False)
    id_docente              : Mapped[uuid.UUID]  = mapped_column(ForeignKey("usuario_perfil_acesso.id"), nullable=False)
    mes_referencia          : Mapped[date]       = mapped_column(Date, nullable=False)
    nota_atual              : Mapped[float|None] = mapped_column(Numeric(4, 2), nullable=True)
    frequencia_pct          : Mapped[float|None] = mapped_column(Numeric(5, 2), nullable=True)
    engajamento             : Mapped[int|None]   = mapped_column(SmallInteger, nullable=True)  # 1-5
    comportamento_alterado  : Mapped[bool]       = mapped_column(Boolean, default=False)
    descricao_comportamento : Mapped[str|None]   = mapped_column(Text, nullable=True)
    token_acesso            : Mapped[uuid.UUID|None] = mapped_column(UUID(as_uuid=True), unique=True, nullable=True)
    token_expira_em         : Mapped[datetime|None]  = mapped_column(DateTime(timezone=True), nullable=True)
    preenchido_em           : Mapped[datetime|None]  = mapped_column(DateTime(timezone=True), nullable=True)
    criado_em               : Mapped[datetime]       = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
