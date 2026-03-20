import asyncio, uuid
from backend.app.database import SessionLocal
from backend.app.models.Regra_Motor_Hipoteses import RegraMotorHipoteses

REGRAS = [
    {
        "nome": "Comprometimento de função executiva",
        "condicoes_json": {
            "op": "and",
            "condicoes": [
                {"contem": "concentração"},
                {"contem": "impulsividade"},
            ]
        },
        "hipotese_gerada": "Possível comprometimento de função executiva (controle inibitório). Avaliar TDAH.",
        "confianca_base": 75,
        "prioridade": 10,
    },
    {
        "nome": "Dificuldade de leitura e escrita",
        "condicoes_json": {
            "op": "or",
            "condicoes": [
                {"contem": "dislexia"},
                {"contem": "dificuldade de leitura"},
                {"contem": "dificuldade de escrita"},
            ]
        },
        "hipotese_gerada": "Possível transtorno específico de aprendizagem (leitura/escrita). Avaliar dislexia.",
        "confianca_base": 70,
        "prioridade": 9,
    },
    {
        "nome": "Indicadores de TEA",
        "condicoes_json": {
            "op": "and",
            "condicoes": [
                {"contem": "comunicação"},
                {"contem": "interação social"},
            ]
        },
        "hipotese_gerada": "Indicadores de dificuldade em comunicação e interação social. Avaliar TEA.",
        "confianca_base": 65,
        "prioridade": 8,
    },
]

async def seed():
    async with SessionLocal() as db:
        for r in REGRAS:
            db.add(RegraMotorHipoteses(id=uuid.uuid4(), **r))
        await db.commit()
        print(f"{len(REGRAS)} regras inseridas.")

if __name__ == "__main__":
    asyncio.run(seed())
