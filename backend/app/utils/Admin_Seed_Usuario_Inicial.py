import asyncio, uuid
from backend.app.database import engine, SessionLocal, Base
from backend.app.models.Usuario_Perfil_Acesso import UsuarioPerfilAcesso, PerfilUsuario
from backend.app.utils.Auth_JWT_Controle_Perfis_RBAC import hash_senha

async def seed():
    async with SessionLocal() as db:
        # Verifica se já existe
        result = await db.execute(
            select(UsuarioPerfilAcesso).where(UsuarioPerfilAcesso.matricula == "admin")
        )
        if result.scalar_one_or_none():
            print("Admin já existe.")
            return

        admin = UsuarioPerfilAcesso(
            id         = uuid.uuid4(),
            matricula  = "admin",
            nome       = "Admin NAPNE",
            cpf        = "00000000000",
            email      = "admin@napne.local",
            senha_hash = hash_senha("admin123"),
            perfil     = PerfilUsuario.admin,
        )
        db.add(admin)
        await db.commit()
        print("Admin criado: matrícula: admin / senha: admin123")

from sqlalchemy import select # Import necessário para o select acima

if __name__ == "__main__":
    asyncio.run(seed())
