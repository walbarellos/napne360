from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.Alerta_Monitoramento_Risco_Estudante import (
    AlertaMonitoramentoRiscoEstudante, TipoAlerta, StatusAlerta
)
from backend.app.models.Formulario_Mensal_Docente_Resposta import FormularioMensalDocenteResposta
from backend.app.models.PEI_Plano_Educacional_Individual import PEIPlanoEducacionalIndividual, StatusPEI
from datetime import datetime, timezone, timedelta
import uuid

async def _alerta_ja_existe(
    id_matricula : uuid.UUID,
    tipo         : TipoAlerta,
    db           : AsyncSession,
) -> bool:
    """Idempotência — não duplica alerta ativo do mesmo tipo."""
    res = await db.execute(
        select(AlertaMonitoramentoRiscoEstudante).where(
            AlertaMonitoramentoRiscoEstudante.id_matricula == id_matricula,
            AlertaMonitoramentoRiscoEstudante.tipo         == tipo,
            AlertaMonitoramentoRiscoEstudante.status       == StatusAlerta.ativo,
        )
    )
    return res.scalar_one_or_none() is not None

async def _criar_alerta(
    id_matricula  : uuid.UUID,
    tipo          : TipoAlerta,
    descricao     : str,
    dados_contexto: dict,
    db            : AsyncSession,
) -> AlertaMonitoramentoRiscoEstudante | None:
    if await _alerta_ja_existe(id_matricula, tipo, db):
        return None
    a = AlertaMonitoramentoRiscoEstudante(
        id_matricula   = id_matricula,
        tipo           = tipo,
        descricao      = descricao,
        dados_contexto = dados_contexto,
    )
    db.add(a)
    return a

async def processar_alertas_formulario(
    formulario : FormularioMensalDocenteResposta,
    db         : AsyncSession,
) -> list[AlertaMonitoramentoRiscoEstudante]:
    """
    Chamado após cada formulário mensal preenchido.
    Avalia 3 regras: queda de nota, faltas, comportamento.
    """
    gerados = []

    # busca formulário anterior para comparar nota
    res = await db.execute(
        select(FormularioMensalDocenteResposta)
        .where(
            FormularioMensalDocenteResposta.id_matricula == formulario.id_matricula,
            FormularioMensalDocenteResposta.id           != formulario.id,
            FormularioMensalDocenteResposta.preenchido_em != None,
        )
        .order_by(FormularioMensalDocenteResposta.mes_referencia.desc())
        .limit(1)
    )
    anterior = res.scalar_one_or_none()

    # regra 1 — queda de rendimento > 2 pontos
    if (
        formulario.nota_atual is not None
        and anterior is not None
        and anterior.nota_atual is not None
        and (float(anterior.nota_atual) - float(formulario.nota_atual)) > 2
    ):
        a = await _criar_alerta(
            id_matricula   = formulario.id_matricula,
            tipo           = TipoAlerta.queda_rendimento,
            descricao      = f"Queda de {float(anterior.nota_atual) - float(formulario.nota_atual):.1f} pontos em relação ao mês anterior.",
            dados_contexto = {"nota_anterior": float(anterior.nota_atual), "nota_atual": float(formulario.nota_atual)},
            db             = db,
        )
        if a: gerados.append(a)

    # regra 2 — frequência abaixo de 75%
    if formulario.frequencia_pct is not None and float(formulario.frequencia_pct) < 75:
        a = await _criar_alerta(
            id_matricula   = formulario.id_matricula,
            tipo           = TipoAlerta.faltas_consecutivas,
            descricao      = f"Frequência de {float(formulario.frequencia_pct):.1f}% — abaixo do mínimo de 75%.",
            dados_contexto = {"frequencia_pct": float(formulario.frequencia_pct)},
            db             = db,
        )
        if a: gerados.append(a)

    # regra 3 — mudança comportamental reportada
    if formulario.comportamento_alterado:
        a = await _criar_alerta(
            id_matricula   = formulario.id_matricula,
            tipo           = TipoAlerta.mudanca_comportamental,
            descricao      = f"Docente reportou mudança comportamental: {formulario.descricao_comportamento or 'sem descrição'}",
            dados_contexto = {"descricao": formulario.descricao_comportamento},
            db             = db,
        )
        if a: gerados.append(a)

    if gerados:
        await db.flush()
    return gerados

async def processar_alerta_pei_sem_revisao(db: AsyncSession) -> list[AlertaMonitoramentoRiscoEstudante]:
    """Job diário — verifica PEIs ativos sem revisão há 60+ dias."""
    limite = datetime.now(timezone.utc) - timedelta(days=60)
    res = await db.execute(
        select(PEIPlanoEducacionalIndividual).where(
            PEIPlanoEducacionalIndividual.status == StatusPEI.ativo,
            PEIPlanoEducacionalIndividual.data_ultima_revisao < limite,
        )
    )
    peis = res.scalars().all()
    gerados = []
    for pei in peis:
        # Nota: pei.id_dossie != id_matricula. Em um sistema real, faria o join.
        # Aqui, como id_matricula é o que o alerta usa, precisaríamos buscar a matrícula ativa.
        # Por simplicidade neste MVP, usamos o id_dossie como proxy ou buscamos a matrícula.
        from backend.app.models.Matricula_Entrada_Sistema import MatriculaEntradaSistema
        mat_res = await db.execute(
            select(MatriculaEntradaSistema).where(MatriculaEntradaSistema.id_estudante == pei.dossie.id_estudante).limit(1)
        )
        matricula = mat_res.scalar_one_or_none()
        if matricula:
            a = await _criar_alerta(
                id_matricula   = matricula.id,
                tipo           = TipoAlerta.pei_sem_revisao,
                descricao      = "PEI ativo sem revisão há mais de 60 dias.",
                dados_contexto = {"id_pei": str(pei.id), "ultima_revisao": str(pei.data_ultima_revisao)},
                db             = db,
            )
            if a: gerados.append(a)
    if gerados:
        await db.flush()
    return gerados
