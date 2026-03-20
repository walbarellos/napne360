from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from backend.app.database import get_db
from backend.app.schemas.Estudante_Schema_Cadastro_Resposta import EstudanteCriarRequest, EstudanteResponse
from backend.app.services.Matricula_Triagem_CID_Automatica import registrar_estudante_via_suap
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario
from backend.app.models.Matricula_Entrada_Sistema import TipoCotaPCD

router = APIRouter(prefix="/matriculas", tags=["matriculas"])

class RegistroRequest(EstudanteCriarRequest):
    suap_username: str
    suap_password: str

@router.post("/", response_model=EstudanteResponse)
async def registrar(
    body: RegistroRequest,
    db  : AsyncSession = Depends(get_db),
    _   = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    matricula = await registrar_estudante_via_suap(
        matricula_suap       = body.matricula_suap,
        declarou_necessidade = body.declarou_necessidade,
        modalidade           = body.modalidade,
        tipo_cota_pcd        = body.tipo_cota_pcd,
        suap_username        = body.suap_username,
        suap_password        = body.suap_password,
        db                   = db,
    )
    return EstudanteResponse.from_orm(matricula)
