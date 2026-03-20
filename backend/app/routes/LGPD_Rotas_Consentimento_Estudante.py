from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from uuid import UUID
from backend.app.database import get_db
from backend.app.services.LGPD_Consentimento_Validacao_Bloqueio import registrar_consentimento
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario

router = APIRouter(prefix="/consentimento", tags=["lgpd"])

class ConsentimentoRequest(BaseModel):
    id_matricula : UUID
    consentido   : bool

@router.post("/")
async def registrar(
    body    : ConsentimentoRequest,
    request : Request,
    db      : AsyncSession = Depends(get_db),
    _       = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    ip = request.client.host
    c  = await registrar_consentimento(body.id_matricula, body.consentido, ip, db)
    return {"id": c.id, "consentido": c.consentido, "data": c.data_consentimento}
