import uuid
from sqlalchemy import Boolean, ForeignKey, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from backend.app.database import Base
from backend.app.models.Entrevista_Estruturada_Sessao import CategoriaEntrevista

class EntrevistaRespostaPorCategoria(Base):
    __tablename__ = "entrevista_resposta_por_categoria"

    id              : Mapped[uuid.UUID]          = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    id_entrevista   : Mapped[uuid.UUID]          = mapped_column(ForeignKey("entrevista_estruturada_sessao.id"), nullable=False)
    categoria       : Mapped[CategoriaEntrevista]= mapped_column(SAEnum(CategoriaEntrevista), nullable=False)
    pergunta_codigo : Mapped[str]                = mapped_column(String(50), nullable=False)
    resposta        : Mapped[str]                = mapped_column(Text, nullable=False)
    indicador_risco : Mapped[bool]               = mapped_column(Boolean, default=False)
