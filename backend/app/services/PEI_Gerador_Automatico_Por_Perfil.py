from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.PEI_Plano_Educacional_Individual import PEIPlanoEducacionalIndividual
from backend.app.models.PEI_Componentes import (
    PEIObjetivoPedagogico, PEIEstrategiaAreaCurso,
    PEIAdaptacaoCurricular, PEITecnologiaAssistiva, TipoAdaptacao
)
from backend.app.models.Hipotese_Diagnostica_Gerada import HipoteseDiagnosticaGerada
import uuid, hashlib, json
from datetime import datetime, timezone

CONTEUDO_POR_HIPOTESE: dict[str, dict] = {
    "tdah": {
        "objetivos": [
            ("Desenvolver estratégias de autorregulação e foco durante atividades acadêmicas", "1 semestre"),
            ("Reduzir impacto da impulsividade em avaliações formais", "1 bimestre"),
        ],
        "estrategias": [
            ("tecnologia", "Uso de timers visuais para segmentar tarefas longas", "timer"),
            ("tecnologia", "Checklists de passos para resolução de problemas", "checklist"),
            ("exatas",     "Provas segmentadas em etapas menores com intervalos", "avaliacao_adaptada"),
            ("linguagens", "Produção oral como alternativa à escrita extensa", "producao_oral"),
        ],
        "adaptacoes": [
            (TipoAdaptacao.tempo_extra,           "Acréscimo de 25% no tempo de provas"),
            (TipoAdaptacao.assento_preferencial,  "Assento próximo ao professor, longe de janelas"),
            (TipoAdaptacao.avaliacao_alternativa, "Possibilidade de avaliação oral"),
        ],
        "tecnologias": [
            ("Forest App", "App de foco com técnica Pomodoro", "https://www.forestapp.cc", True),
            ("Motion",     "Planejador de tarefas com IA", None, False),
        ],
    },
    "dislexia": {
        "objetivos": [
            ("Desenvolver fluência de leitura com apoio de tecnologia assistiva", "1 semestre"),
            ("Reduzir barreiras na produção textual escrita", "1 bimestre"),
        ],
        "estrategias": [
            ("linguagens", "Uso de texto-para-fala para leitura de enunciados", "tts"),
            ("linguagens", "Mapas mentais como substituto de resumos lineares", "mapa_mental"),
            ("exatas",     "Enunciados em fonte OpenDyslexic ou Arial espaçada", "material_adaptado"),
        ],
        "adaptacoes": [
            (TipoAdaptacao.tempo_extra,           "Acréscimo de 25% no tempo de provas"),
            (TipoAdaptacao.material_adaptado,     "Materiais em fonte acessível (OpenDyslexic)"),
            (TipoAdaptacao.avaliacao_alternativa, "Avaliação oral ou gravada em áudio"),
        ],
        "tecnologias": [
            ("Natural Reader", "Leitor de texto em voz alta", "https://www.naturalreaders.com", True),
            ("OpenDyslexic",   "Fonte gratuita para dislexia", "https://opendyslexic.org", True),
        ],
    },
    "tea": {
        "objetivos": [
            ("Estruturar rotina acadêmica previsível para reduzir ansiedade", "1 semestre"),
            ("Desenvolver estratégias de comunicação em contexto acadêmico", "1 bimestre"),
        ],
        "estrategias": [
            ("tecnologia", "Uso de agendas visuais com antecipação de atividades", "agenda_visual"),
            ("linguagens", "Instruções escritas e visuais além das orais", "multimodal"),
            ("exatas",     "Exemplos concretos antes de conceitos abstratos", "concreto_abstrato"),
        ],
        "adaptacoes": [
            (TipoAdaptacao.assento_preferencial,  "Assento em local com menor estímulo sensorial"),
            (TipoAdaptacao.tempo_extra,           "Acréscimo de 25% no tempo de provas"),
            (TipoAdaptacao.material_adaptado,     "Instruções passo a passo por escrito"),
        ],
        "tecnologias": [
            ("Todoist",   "Organizador de tarefas com rotina visual", "https://todoist.com", True),
            ("Boardmaker","Comunicação aumentativa e alternativa", None, False),
        ],
    },
}

def _detectar_perfil(hipoteses: list[str]) -> list[str]:
    perfis = []
    texto  = " ".join(hipoteses).lower()
    if "tdah" in texto or "função executiva" in texto:
        perfis.append("tdah")
    if "dislexia" in texto or "leitura" in texto:
        perfis.append("dislexia")
    if "tea" in texto or "interação social" in texto:
        perfis.append("tea")
    return perfis or ["tdah"]

async def gerar_pei(
    id_entrevista : uuid.UUID,
    id_dossie     : uuid.UUID,
    id_usuario    : uuid.UUID,
    db            : AsyncSession,
) -> PEIPlanoEducacionalIndividual:
    res = await db.execute(
        select(HipoteseDiagnosticaGerada)
        .where(
            HipoteseDiagnosticaGerada.id_entrevista == id_entrevista,
            HipoteseDiagnosticaGerada.confirmada    != False,
        )
    )
    hipoteses      = res.scalars().all()
    textos_hipot   = [h.descricao for h in hipoteses]
    perfis         = _detectar_perfil(textos_hipot)

    pei = PEIPlanoEducacionalIndividual(
        id_dossie     = id_dossie,
        id_entrevista = id_entrevista,
        id_gerado_por = id_usuario,
    )
    db.add(pei)
    await db.flush()

    for perfil in perfis:
        conteudo = CONTEUDO_POR_HIPOTESE.get(perfil, {})
        for desc, prazo in conteudo.get("objetivos", []):
            db.add(PEIObjetivoPedagogico(id_pei=pei.id, descricao=desc, prazo=prazo))
        for area, desc, tipo in conteudo.get("estrategias", []):
            db.add(PEIEstrategiaAreaCurso(id_pei=pei.id, area=area, descricao=desc, tipo_estrategia=tipo))
        for tipo, desc in conteudo.get("adaptacoes", []):
            db.add(PEIAdaptacaoCurricular(id_pei=pei.id, tipo=tipo, descricao=desc))
        for nome, desc, link, gratuita in conteudo.get("tecnologias", []):
            db.add(PEITecnologiaAssistiva(id_pei=pei.id, nome=nome, descricao=desc, link_recurso=link, gratuita=gratuita))

    snapshot = {"perfis": perfis, "hipoteses": textos_hipot, "gerado_em": datetime.now(timezone.utc).isoformat()}
    pei.hash_assinatura = hashlib.sha256(json.dumps(snapshot, sort_keys=True).encode()).hexdigest()

    await db.commit()
    
    # Busca PEI com relacionamentos carregados
    stmt = (
        select(PEIPlanoEducacionalIndividual)
        .options(
            selectinload(PEIPlanoEducacionalIndividual.objetivos),
            selectinload(PEIPlanoEducacionalIndividual.estrategias),
            selectinload(PEIPlanoEducacionalIndividual.adaptacoes),
            selectinload(PEIPlanoEducacionalIndividual.tecnologias),
        )
        .where(PEIPlanoEducacionalIndividual.id == pei.id)
    )
    res = await db.execute(stmt)
    return res.scalar_one()
