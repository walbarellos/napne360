import uuid
from sqlalchemy import Boolean, Integer, String, Text, Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.app.database import Base
from backend.app.models.Alerta_Monitoramento_Risco_Estudante import TipoAlerta

class RegraAlertaConfiguracao(Base):
    __tablename__ = "regra_alerta_configuracao"

    id            : Mapped[uuid.UUID]  = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tipo          : Mapped[TipoAlerta] = mapped_column(SAEnum(TipoAlerta), nullable=False)
    nome          : Mapped[str]        = mapped_column(String(200), nullable=False)
    # ex: {"campo": "queda_rendimento", "operador": ">", "valor": 2}
    condicao_json : Mapped[dict]       = mapped_column(JSONB, nullable=False)
    cor_visual    : Mapped[str]        = mapped_column(String(10), nullable=False)  # vermelho|laranja|azul
    descricao     : Mapped[str|None]   = mapped_column(Text, nullable=True)
    ativa         : Mapped[bool]       = mapped_column(Boolean, default=True)
