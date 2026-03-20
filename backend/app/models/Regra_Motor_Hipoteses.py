import uuid
from sqlalchemy import Boolean, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from backend.app.database import Base

class RegraMotorHipoteses(Base):
    __tablename__ = "regra_motor_hipoteses"

    id              : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome            : Mapped[str]       = mapped_column(String(200), nullable=False)
    # ex: {"op": "and", "condicoes": [{"campo": "comportamento", "contem": "impulsividade"}]}
    condicoes_json  : Mapped[dict]      = mapped_column(JSONB, nullable=False)
    hipotese_gerada : Mapped[str]       = mapped_column(Text, nullable=False)
    confianca_base  : Mapped[int]       = mapped_column(Integer, default=70)
    prioridade      : Mapped[int]       = mapped_column(Integer, default=0)
    ativa           : Mapped[bool]      = mapped_column(Boolean, default=True)
