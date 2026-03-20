from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.models.Regra_Motor_Hipoteses import RegraMotorHipoteses
from backend.app.models.Hipotese_Diagnostica_Gerada import HipoteseDiagnosticaGerada
from backend.app.models.Entrevista_Resposta_Por_Categoria import EntrevistaRespostaPorCategoria
import uuid

def _avaliar_condicao(condicao: dict, respostas_texto: list[str]) -> bool:
    """Avalia uma condição simples contra as respostas."""
    campo  = condicao.get("contem", "").lower()
    return any(campo in r.lower() for r in respostas_texto)

def _avaliar_regra(regra_json: dict, respostas_texto: list[str]) -> bool:
    op         = regra_json.get("op", "and")
    condicoes  = regra_json.get("condicoes", [])

    resultados = [_avaliar_condicao(c, respostas_texto) for c in condicoes]

    if op == "and":
        return all(resultados)
    if op == "or":
        return any(resultados)
    if op == "not":
        return not resultados[0] if resultados else True
    return False

async def processar_hipoteses(
    id_entrevista : uuid.UUID,
    db            : AsyncSession,
) -> list[HipoteseDiagnosticaGerada]:
    """
    Chamado após cada resposta salva.
    Reavalia TODAS as regras ativas e persiste hipóteses novas.
    Idempotente: não duplica hipótese já existente para a mesma regra.
    """
    # 1. busca todas as respostas da sessão
    res = await db.execute(
        select(EntrevistaRespostaPorCategoria)
        .where(EntrevistaRespostaPorCategoria.id_entrevista == id_entrevista)
    )
    respostas      = res.scalars().all()
    respostas_texto = [r.resposta for r in respostas]

    # 2. busca regras ativas ordenadas por prioridade
    res = await db.execute(
        select(RegraMotorHipoteses)
        .where(RegraMotorHipoteses.ativa == True)
        .order_by(RegraMotorHipoteses.prioridade.desc())
    )
    regras = res.scalars().all()

    # 3. hipóteses já geradas (evita duplicata)
    res = await db.execute(
        select(HipoteseDiagnosticaGerada)
        .where(HipoteseDiagnosticaGerada.id_entrevista == id_entrevista)
    )
    hipoteses_existentes = {h.descricao for h in res.scalars().all()}

    novas = []
    for regra in regras:
        if regra.hipotese_gerada in hipoteses_existentes:
            continue
        if _avaliar_regra(regra.condicoes_json, respostas_texto):
            h = HipoteseDiagnosticaGerada(
                id_entrevista = id_entrevista,
                descricao     = regra.hipotese_gerada,
                confianca     = regra.confianca_base,
            )
            db.add(h)
            novas.append(h)

    if novas:
        await db.flush()

    return novas
