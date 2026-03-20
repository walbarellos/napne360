import uuid
from sqlalchemy import String, Date, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, date, timezone
from typing import List
from backend.app.database import Base

class EstudanteDadosCadastrais(Base):
    __tablename__ = "estudante_dados_cadastrais"

    id                : Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nome_registro     : Mapped[str]       = mapped_column(String(200), nullable=False)
    nome_social       : Mapped[str | None]= mapped_column(String(200), nullable=True)
    cpf               : Mapped[str]       = mapped_column(String(11), unique=True, nullable=False)
    matricula_suap    : Mapped[str]       = mapped_column(String(30), unique=True, nullable=False)
    data_nascimento   : Mapped[date]      = mapped_column(Date, nullable=False)
    email             : Mapped[str | None]= mapped_column(String(150), nullable=True)
    campus            : Mapped[str | None]= mapped_column(String(10), nullable=True)
    criado_em         : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    atualizado_em     : Mapped[datetime]  = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))

    # Relacionamentos
    matriculas: Mapped[List["MatriculaEntradaSistema"]] = relationship("MatriculaEntradaSistema", back_populates="estudante")
    dossie: Mapped["DossiePerfilLongitudinalEstudante"] = relationship("DossiePerfilLongitudinalEstudante", back_populates="estudante", uselist=False)

    @property
    def nome_exibicao(self) -> str:
        return self.nome_social or self.nome_registro
