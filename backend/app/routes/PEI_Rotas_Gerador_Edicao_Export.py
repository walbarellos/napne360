from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.PEI_Plano_Educacional_Individual import PEIPlanoEducacionalIndividual
from backend.app.models.Entrevista_Estruturada_Sessao import EntrevistaEstruturadaSessao
from backend.app.services.PEI_Gerador_Automatico_Por_Perfil import gerar_pei
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario, UsuarioPerfilAcesso

router = APIRouter(prefix="/pei", tags=["pei"])

class GerarPEIRequest(BaseModel):
    id_entrevista: UUID

@router.post("/gerar")
async def gerar(
    body    : GerarPEIRequest,
    db      : AsyncSession = Depends(get_db),
    usuario : UsuarioPerfilAcesso = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    # busca sessão
    res = await db.execute(
        select(EntrevistaEstruturadaSessao)
        .where(EntrevistaEstruturadaSessao.id == body.id_entrevista)
    )
    sessao = res.scalar_one_or_none()
    if not sessao:
        raise HTTPException(404, "Entrevista não encontrada")
    if not sessao.concluida:
        raise HTTPException(400, "Entrevista ainda não foi concluída")

    pei = await gerar_pei(
        id_entrevista = body.id_entrevista,
        id_dossie     = sessao.id_dossie,
        id_usuario    = usuario.id,
        db            = db,
    )
    return {
        "id_pei"          : pei.id,
        "status"          : pei.status,
        "hash_assinatura" : pei.hash_assinatura,
        "data_geracao"    : pei.data_geracao,
        "objetivos"       : [{"descricao": o.descricao, "prazo": o.prazo} for o in pei.objetivos],
        "estrategias"     : [{"area": e.area, "descricao": e.descricao} for e in pei.estrategias],
        "adaptacoes"      : [{"tipo": a.tipo, "descricao": a.descricao} for a in pei.adaptacoes],
        "tecnologias"     : [{"nome": t.nome, "link": t.link_recurso, "gratuita": t.gratuita} for t in pei.tecnologias],
    }
