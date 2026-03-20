import os
from datetime import datetime, timedelta, timezone
from typing import Annotated
import jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.app.database import get_db
from backend.app.models.Usuario_Perfil_Acesso import UsuarioPerfilAcesso, PerfilUsuario

SECRET_KEY   = os.getenv("SECRET_KEY", "troca-em-producao")
ALGORITHM    = "HS256"
EXPIRE_HORAS = 8

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def hash_senha(senha: str) -> str:
    return pwd_context.hash(senha)

def verificar_senha(senha: str, hash: str) -> bool:
    return pwd_context.verify(senha, hash)

def criar_token(data: dict) -> str:
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=EXPIRE_HORAS)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

async def get_usuario_atual(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: AsyncSession = Depends(get_db)
) -> UsuarioPerfilAcesso:
    erro = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não autorizado")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise erro
    except jwt.InvalidTokenError:
        raise erro

    result = await db.execute(select(UsuarioPerfilAcesso).where(UsuarioPerfilAcesso.id == user_id))
    usuario = result.scalar_one_or_none()
    if not usuario or not usuario.ativo:
        raise erro
    return usuario

def exigir_perfil(*perfis: PerfilUsuario):
    async def verificar(usuario: UsuarioPerfilAcesso = Depends(get_usuario_atual)):
        if usuario.perfil not in perfis:
            raise HTTPException(status_code=403, detail="Permissão insuficiente")
        return usuario
    return verificar
