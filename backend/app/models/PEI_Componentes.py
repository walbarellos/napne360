import uuid, enum
from sqlalchemy import ForeignKey, String, Text, Boolean, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from backend.app.database import Base

class TipoAdaptacao(str, enum.Enum):
    tempo_extra          = "tempo_extra"
    avaliacao_alternativa= "avaliacao_alternativa"
    assento_preferencial = "assento_preferencial"
    material_adaptado    = "material_adaptado"
    interprete_libras    = "interprete_libras"
    outro                = "outro"

class PEIObjetivoPedagogico(Base):
    __tablename__ = "pei_objetivo_pedagogico"
    id       : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pei   : Mapped[uuid.UUID] = mapped_column(ForeignKey("pei_plano_educacional_individual.id"), nullable=False)
    descricao: Mapped[str]       = mapped_column(Text, nullable=False)
    prazo    : Mapped[str|None]  = mapped_column(String(50), nullable=True)
    alcancado: Mapped[bool|None] = mapped_column(Boolean, nullable=True)

class PEIEstrategiaAreaCurso(Base):
    __tablename__ = "pei_estrategia_area_curso"
    id              : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pei          : Mapped[uuid.UUID] = mapped_column(ForeignKey("pei_plano_educacional_individual.id"), nullable=False)
    area            : Mapped[str]       = mapped_column(String(50), nullable=False)
    descricao       : Mapped[str]       = mapped_column(Text, nullable=False)
    tipo_estrategia : Mapped[str|None]  = mapped_column(String(100), nullable=True)

class PEIAdaptacaoCurricular(Base):
    __tablename__ = "pei_adaptacao_curricular"
    id       : Mapped[uuid.UUID]     = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pei   : Mapped[uuid.UUID]     = mapped_column(ForeignKey("pei_plano_educacional_individual.id"), nullable=False)
    tipo     : Mapped[TipoAdaptacao] = mapped_column(SAEnum(TipoAdaptacao), nullable=False)
    descricao: Mapped[str]           = mapped_column(Text, nullable=False)

class PEITecnologiaAssistiva(Base):
    __tablename__ = "pei_tecnologia_assistiva"
    id          : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_pei      : Mapped[uuid.UUID] = mapped_column(ForeignKey("pei_plano_educacional_individual.id"), nullable=False)
    nome        : Mapped[str]       = mapped_column(String(200), nullable=False)
    descricao   : Mapped[str|None]  = mapped_column(Text, nullable=True)
    link_recurso: Mapped[str|None]  = mapped_column(Text, nullable=True)
    gratuita    : Mapped[bool]      = mapped_column(Boolean, default=True)
