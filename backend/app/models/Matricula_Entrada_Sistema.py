import uuid, enum
from sqlalchemy import String, Boolean, Date, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date, timezone
from backend.app.database import Base

class StatusMatricula(str, enum.Enum):
    aguardando_triagem    = "aguardando_triagem"
    entrevista_agendada   = "entrevista_agendada"
    dossie_ativo          = "dossie_ativo"
    pendente_laudo        = "pendente_laudo"
    pendente_revisao      = "pendente_revisao"
    monitoramento         = "monitoramento"
    concluido             = "concluido"
    evadido               = "evadido"
    transferido           = "transferido"
    trancado              = "trancado"

class ModalidadeEnsino(str, enum.Enum):
    medio_integrado = "medio_integrado"
    subsequente     = "subsequente"
    superior        = "superior"

class TipoCotaPCD(str, enum.Enum):
    nenhuma = "nenhuma"   # ampla concorrência
    pcd     = "pcd"       # deficiência — independe de renda/escola
    ppi_pcd = "ppi_pcd"   # deficiência + racial + renda + escola pública

class MatriculaEntradaSistema(Base):
    __tablename__ = "matricula_entrada_sistema"

    id                   : Mapped[uuid.UUID]        = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_estudante         : Mapped[uuid.UUID]        = mapped_column(ForeignKey("estudante_dados_cadastrais.id"), nullable=False)
    curso                : Mapped[str]              = mapped_column(String(300), nullable=False)
    modalidade           : Mapped[ModalidadeEnsino] = mapped_column(SAEnum(ModalidadeEnsino), nullable=False)
    tipo_cota_pcd        : Mapped[TipoCotaPCD]      = mapped_column(SAEnum(TipoCotaPCD), default=TipoCotaPCD.nenhuma)
    periodo_referencia   : Mapped[int]              = mapped_column(nullable=False)
    status               : Mapped[StatusMatricula]  = mapped_column(SAEnum(StatusMatricula), default=StatusMatricula.aguardando_triagem)
    declarou_necessidade : Mapped[bool]             = mapped_column(Boolean, default=False)
    triagem_concluida    : Mapped[bool]             = mapped_column(Boolean, default=False)
    data_matricula       : Mapped[date]             = mapped_column(Date, nullable=False)
    criado_em            : Mapped[datetime]         = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    estudante = relationship("EstudanteDadosCadastrais", back_populates="matriculas")
