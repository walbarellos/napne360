import uuid, enum
from sqlalchemy import ForeignKey, String, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime, timezone
from backend.app.database import Base

class TipoAlerta(str, enum.Enum):
    queda_rendimento        = "queda_rendimento"
    faltas_consecutivas     = "faltas_consecutivas"
    mudanca_comportamental  = "mudanca_comportamental"
    pei_sem_revisao         = "pei_sem_revisao"

class StatusAlerta(str, enum.Enum):
    ativo              = "ativo"
    em_acompanhamento  = "em_acompanhamento"
    resolvido          = "resolvido"

class AlertaMonitoramentoRiscoEstudante(Base):
    __tablename__ = "alerta_monitoramento_risco_estudante"

    id                   : Mapped[uuid.UUID]   = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_matricula         : Mapped[uuid.UUID]   = mapped_column(ForeignKey("matricula_entrada_sistema.id"), nullable=False)
    tipo                 : Mapped[TipoAlerta]  = mapped_column(SAEnum(TipoAlerta), nullable=False)
    descricao            : Mapped[str]         = mapped_column(Text, nullable=False)
    dados_contexto       : Mapped[dict|None]   = mapped_column(JSONB, nullable=True)
    status               : Mapped[StatusAlerta]= mapped_column(SAEnum(StatusAlerta), default=StatusAlerta.ativo)
    id_responsavel       : Mapped[uuid.UUID|None] = mapped_column(ForeignKey("usuario_perfil_acesso.id"), nullable=True)
    observacao_resolucao : Mapped[str|None]    = mapped_column(Text, nullable=True)
    criado_em            : Mapped[datetime]    = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    resolvido_em         : Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)

    matricula = relationship("MatriculaEntradaSistema", backref="alertas")
