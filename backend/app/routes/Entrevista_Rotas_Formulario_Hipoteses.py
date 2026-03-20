from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from backend.app.database import get_db
from backend.app.models.Entrevista_Estruturada_Sessao import EntrevistaEstruturadaSessao, CategoriaEntrevista
from backend.app.models.Entrevista_Resposta_Por_Categoria import EntrevistaRespostaPorCategoria
from backend.app.models.Hipotese_Diagnostica_Gerada import HipoteseDiagnosticaGerada
from backend.app.services.Entrevista_Motor_Hipoteses_Tempo_Real import processar_hipoteses
from backend.app.services.LGPD_Consentimento_Validacao_Bloqueio import exigir_consentimento_ativo
from backend.app.models.Dossie_Perfil_Longitudinal_Estudante import DossiePerfilLongitudinalEstudante
from backend.app.models.Matricula_Entrada_Sistema import MatriculaEntradaSistema
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario, UsuarioPerfilAcesso

router = APIRouter(prefix="/entrevistas", tags=["entrevistas"])

class IniciarEntrevistaRequest(BaseModel):
    id_matricula: UUID

class RespostaRequest(BaseModel):
    categoria       : CategoriaEntrevista
    pergunta_codigo : str
    resposta        : str
    indicador_risco : bool = False

class ConcluirRequest(BaseModel):
    observacoes_finais: str | None = None

# ── POST /entrevistas/ — inicia sessão
@router.post("/")
async def iniciar_entrevista(
    body    : IniciarEntrevistaRequest,
    db      : AsyncSession = Depends(get_db),
    usuario : UsuarioPerfilAcesso = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    # 1. verifica consentimento
    await exigir_consentimento_ativo(body.id_matricula, db)

    # 2. busca dossiê pelo id_matricula → estudante → dossie
    res = await db.execute(
        select(MatriculaEntradaSistema).where(MatriculaEntradaSistema.id == body.id_matricula)
    )
    matricula = res.scalar_one_or_none()
    if not matricula:
        raise HTTPException(404, "Matrícula não encontrada")

    res = await db.execute(
        select(DossiePerfilLongitudinalEstudante)
        .where(DossiePerfilLongitudinalEstudante.id_estudante == matricula.id_estudante)
    )
    dossie = res.scalar_one_or_none()
    if not dossie:
        raise HTTPException(404, "Dossiê não encontrado")

    sessao = EntrevistaEstruturadaSessao(
        id_dossie        = dossie.id,
        id_entrevistador = usuario.id,
    )
    db.add(sessao)
    await db.commit()
    await db.refresh(sessao)
    return {"id_entrevista": sessao.id, "status": "iniciada"}


# ── POST /entrevistas/{id}/resposta — adiciona resposta e reavalia motor
@router.post("/{id_entrevista}/resposta")
async def adicionar_resposta(
    id_entrevista : UUID,
    body          : RespostaRequest,
    db            : AsyncSession = Depends(get_db),
    _             = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    resposta = EntrevistaRespostaPorCategoria(
        id_entrevista   = id_entrevista,
        categoria       = body.categoria,
        pergunta_codigo = body.pergunta_codigo,
        resposta        = body.resposta,
        indicador_risco = body.indicador_risco,
    )
    db.add(resposta)
    await db.flush()

    # motor roda a cada resposta
    novas_hipoteses = await processar_hipoteses(id_entrevista, db)
    await db.commit()

    return {
        "resposta_salva"  : True,
        "hipoteses_novas" : [{"descricao": h.descricao, "confianca": h.confianca} for h in novas_hipoteses]
    }


# ── POST /entrevistas/{id}/concluir
@router.post("/{id_entrevista}/concluir")
async def concluir_entrevista(
    id_entrevista : UUID,
    body          : ConcluirRequest,
    db            : AsyncSession = Depends(get_db),
    _             = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    res = await db.execute(
        select(EntrevistaEstruturadaSessao)
        .where(EntrevistaEstruturadaSessao.id == id_entrevista)
    )
    sessao = res.scalar_one_or_none()
    if not sessao:
        raise HTTPException(404, "Entrevista não encontrada")

    sessao.concluida          = True
    sessao.observacoes_finais = body.observacoes_finais
    await db.commit()

    # busca hipóteses geradas
    res = await db.execute(
        select(HipoteseDiagnosticaGerada)
        .where(HipoteseDiagnosticaGerada.id_entrevista == id_entrevista)
    )
    hipoteses = res.scalars().all()

    return {
        "status"    : "concluida",
        "hipoteses" : [
            {"descricao": h.descricao, "confianca": h.confianca, "confirmada": h.confirmada}
            for h in hipoteses
        ]
    }
