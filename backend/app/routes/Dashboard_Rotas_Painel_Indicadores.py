from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from backend.app.database import get_db
from backend.app.models.Matricula_Entrada_Sistema import MatriculaEntradaSistema, StatusMatricula
from backend.app.models.Alerta_Monitoramento_Risco_Estudante import AlertaMonitoramentoRiscoEstudante, StatusAlerta, TipoAlerta
from backend.app.models.PEI_Plano_Educacional_Individual import PEIPlanoEducacionalIndividual, StatusPEI
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import exigir_perfil
from backend.app.models.Usuario_Perfil_Acesso import PerfilUsuario

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/")
async def painel(
    db : AsyncSession = Depends(get_db),
    _  = Depends(exigir_perfil(PerfilUsuario.napne, PerfilUsuario.admin, PerfilUsuario.gestao))
):
    # estudantes ativos
    res = await db.execute(
        select(func.count()).where(MatriculaEntradaSistema.status.notin_([
            StatusMatricula.concluido, StatusMatricula.evadido, StatusMatricula.transferido
        ]))
    )
    total_ativos = res.scalar()

    # aguardando triagem
    res = await db.execute(
        select(func.count()).where(
            MatriculaEntradaSistema.status == StatusMatricula.aguardando_triagem
        )
    )
    aguardando_triagem = res.scalar()

    # alertas por tipo
    res = await db.execute(
        select(AlertaMonitoramentoRiscoEstudante.tipo, func.count())
        .where(AlertaMonitoramentoRiscoEstudante.status == StatusAlerta.ativo)
        .group_by(AlertaMonitoramentoRiscoEstudante.tipo)
    )
    alertas_por_tipo = {row[0]: row[1] for row in res.all()}

    # total alertas ativos
    total_alertas = sum(alertas_por_tipo.values())

    # PEIs ativos
    res = await db.execute(
        select(func.count()).where(PEIPlanoEducacionalIndividual.status == StatusPEI.ativo)
    )
    peis_ativos = res.scalar()

    # PEIs rascunho (gerados mas não ativados)
    res = await db.execute(
        select(func.count()).where(PEIPlanoEducacionalIndividual.status == StatusPEI.rascunho)
    )
    peis_rascunho = res.scalar()

    return {
        "estudantes": {
            "total_ativos"      : total_ativos,
            "aguardando_triagem": aguardando_triagem,
        },
        "alertas": {
            "total_ativos"  : total_alertas,
            "por_tipo"      : alertas_por_tipo,
        },
        "pei": {
            "ativos"   : peis_ativos,
            "rascunho" : peis_rascunho,
        },
    }
