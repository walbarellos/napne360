from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from uuid import UUID
from datetime import date, timezone, datetime
from backend.app.database import get_db
from backend.app.models.Alerta_Monitoramento_Risco_Estudante import AlertaMonitoramentoRiscoEstudante, StatusAlerta
from backend.app.models.Formulario_Mensal_Docente_Resposta import FormularioMensalDocenteResposta
from backend.app.services.Alerta_Motor_Disparo_Regras_Risco import processar_alertas_formulario
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import get_usuario_atual, exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario, UsuarioPerfilAcesso

router = APIRouter(prefix="/alertas", tags=["alertas"])

class FormularioMensalRequest(BaseModel):
    id_matricula           : UUID
    mes_referencia         : date
    nota_atual             : float | None = None
    frequencia_pct         : float | None = None
    engajamento            : int   | None = None
    comportamento_alterado : bool         = False
    descricao_comportamento: str   | None = None

class ResolverAlertaRequest(BaseModel):
    observacao: str

@router.post("/formulario")
async def receber_formulario(
    body    : FormularioMensalRequest,
    db      : AsyncSession = Depends(get_db),
    usuario : UsuarioPerfilAcesso = Depends(get_usuario_atual)
):
    formulario = FormularioMensalDocenteResposta(
        id_matricula           = body.id_matricula,
        id_docente             = usuario.id,
        mes_referencia         = body.mes_referencia,
        nota_atual             = body.nota_atual,
        frequencia_pct         = body.frequencia_pct,
        engajamento            = body.engajamento,
        comportamento_alterado = body.comportamento_alterado,
        descricao_comportamento= body.descricao_comportamento,
        preenchido_em          = datetime.now(timezone.utc),
    )
    db.add(formulario)
    await db.flush()

    alertas = await processar_alertas_formulario(formulario, db)
    await db.commit()

    return {
        "formulario_salvo": True,
        "alertas_gerados" : [{"tipo": a.tipo, "descricao": a.descricao} for a in alertas]
    }

@router.get("/")
async def listar_alertas(
    db : AsyncSession = Depends(get_db),
    _  = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    res = await db.execute(
        select(AlertaMonitoramentoRiscoEstudante)
        .where(AlertaMonitoramentoRiscoEstudante.status == StatusAlerta.ativo)
        .order_by(AlertaMonitoramentoRiscoEstudante.criado_em.desc())
    )
    alertas = res.scalars().all()
    return [{"id": a.id, "tipo": a.tipo, "descricao": a.descricao, "criado_em": a.criado_em} for a in alertas]

@router.patch("/{id_alerta}/resolver")
async def resolver_alerta(
    id_alerta : UUID,
    body      : ResolverAlertaRequest,
    db        : AsyncSession = Depends(get_db),
    usuario   : UsuarioPerfilAcesso = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin))
):
    res = await db.execute(
        select(AlertaMonitoramentoRiscoEstudante)
        .where(AlertaMonitoramentoRiscoEstudante.id == id_alerta)
    )
    alerta = res.scalar_one_or_none()
    if not alerta:
        raise HTTPException(404, "Alerta não encontrado")

    alerta.status               = StatusAlerta.resolvido
    alerta.id_responsavel       = usuario.id
    alerta.observacao_resolucao = body.observacao
    alerta.resolvido_em         = datetime.now(timezone.utc)
    await db.commit()
    return {"status": "resolvido", "id": alerta.id}
