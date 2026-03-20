from fastapi import FastAPI
from backend.app.routes.Auth_Rotas_Login_Token import router as auth_router
from backend.app.routes.Matricula_Rotas_Triagem_Entrada import router as matricula_router
from backend.app.routes.LGPD_Rotas_Consentimento_Estudante import router as lgpd_router
from backend.app.routes.Entrevista_Rotas_Formulario_Hipoteses import router as entrevista_router
from backend.app.routes.PEI_Rotas_Gerador_Edicao_Export import router as pei_router
from backend.app.routes.Alerta_Rotas_Dashboard_Monitoramento import router as alerta_router
from backend.app.routes.Dashboard_Rotas_Painel_Indicadores import router as dashboard_router

app = FastAPI(
    title="NAPNE 360°",
    description="Sistema integrado de gestão de estudantes PCD",
    version="0.1.0"
)

app.include_router(auth_router)
app.include_router(matricula_router)
app.include_router(lgpd_router)
app.include_router(entrevista_router)
app.include_router(pei_router)
app.include_router(alerta_router)
app.include_router(dashboard_router)

@app.get("/health")
async def health():
    return {"status": "ok", "sistema": "NAPNE 360°"}
