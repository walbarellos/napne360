from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException
from backend.app.models.Consentimento_LGPD_Estudante import ConsentimentoLGPDEstudante
import uuid

async def registrar_consentimento(
    id_matricula : uuid.UUID,
    consentido   : bool,
    ip_origem    : str,
    db           : AsyncSession,
) -> ConsentimentoLGPDEstudante:
    c = ConsentimentoLGPDEstudante(
        id_matricula = id_matricula,
        consentido   = consentido,
        ip_origem    = ip_origem,
    )
    db.add(c)
    await db.commit()
    await db.refresh(c)
    return c

async def exigir_consentimento_ativo(
    id_matricula : uuid.UUID,
    db           : AsyncSession,
) -> None:
    """Chama isso antes de qualquer operação que salva dado sensível."""
    result = await db.execute(
        select(ConsentimentoLGPDEstudante)
        .where(
            ConsentimentoLGPDEstudante.id_matricula == id_matricula,
            ConsentimentoLGPDEstudante.consentido   == True,
        )
        .order_by(ConsentimentoLGPDEstudante.data_consentimento.desc())
        .limit(1)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(
            status_code=403,
            detail="Consentimento LGPD não registrado. O estudante deve consentir antes de prosseguir."
        )
