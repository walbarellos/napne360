import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Adiciona o caminho do projeto
import sys, os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from backend.app.database import Base
from backend.app.models import Usuario_Perfil_Acesso
from backend.app.models import Estudante_Dados_Cadastrais
from backend.app.models import Matricula_Entrada_Sistema
from backend.app.models import Dossie_Perfil_Longitudinal_Estudante
from backend.app.models import Consentimento_LGPD_Estudante
from backend.app.models import Entrevista_Estruturada_Sessao
from backend.app.models import Entrevista_Resposta_Por_Categoria
from backend.app.models import Hipotese_Diagnostica_Gerada
from backend.app.models import Regra_Motor_Hipoteses
from backend.app.models import PEI_Plano_Educacional_Individual
from backend.app.models import PEI_Componentes
from backend.app.models import Alerta_Monitoramento_Risco_Estudante
from backend.app.models import Formulario_Mensal_Docente_Resposta
from backend.app.models import Regra_Alerta_Configuracao

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()

async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine"""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
