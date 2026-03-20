from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models.Usuario_Perfil_Acesso import UsuarioPerfilAcesso
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import verificar_senha, criar_token

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login")
async def login(
    form: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    # Agora busca por matrícula em vez de email
    result = await db.execute(
        select(UsuarioPerfilAcesso).where(UsuarioPerfilAcesso.matricula == form.username)
    )
    usuario = result.scalar_one_or_none()

    if not usuario or not verificar_senha(form.password, usuario.senha_hash):
        raise HTTPException(status_code=401, detail="Matrícula ou senha incorretos")

    token = criar_token({"sub": str(usuario.id), "perfil": usuario.perfil.value})
    return {"access_token": token, "token_type": "bearer"}
