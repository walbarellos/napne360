import uuid, enum
from sqlalchemy import Boolean, ForeignKey, Text, DateTime, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone
from backend.app.database import Base

class StatusPEI(str, enum.Enum):
    rascunho         = "rascunho"
    ativo            = "ativo"
    revisao_pendente = "revisao_pendente"
    arquivado        = "arquivado"

class PEIPlanoEducacionalIndividual(Base):
    __tablename__ = "pei_plano_educacional_individual"

    id                  : Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_dossie           : Mapped[uuid.UUID]  = mapped_column(ForeignKey("dossie_perfil_longitudinal_estudante.id"), nullable=False)
    id_entrevista       : Mapped[uuid.UUID]  = mapped_column(ForeignKey("entrevista_estruturada_sessao.id"), nullable=False)
    id_gerado_por       : Mapped[uuid.UUID]  = mapped_column(ForeignKey("usuario_perfil_acesso.id"), nullable=False)
    status              : Mapped[StatusPEI]  = mapped_column(SAEnum(StatusPEI), default=StatusPEI.rascunho)
    gerado_automatico   : Mapped[bool]       = mapped_column(Boolean, default=True)
    hash_assinatura     : Mapped[str|None]   = mapped_column(Text, nullable=True)
    data_geracao        : Mapped[datetime]   = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    data_ultima_revisao : Mapped[datetime|None] = mapped_column(DateTime(timezone=True), nullable=True)

    objetivos    = relationship("PEIObjetivoPedagogico",  backref="pei", cascade="all, delete-orphan")
    estrategias  = relationship("PEIEstrategiaAreaCurso", backref="pei", cascade="all, delete-orphan")
    adaptacoes   = relationship("PEIAdaptacaoCurricular", backref="pei", cascade="all, delete-orphan")
    tecnologias  = relationship("PEITecnologiaAssistiva", backref="pei", cascade="all, delete-orphan")
