from datetime import date, timezone, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.Estudante_Dados_Cadastrais import EstudanteDadosCadastrais
from backend.app.models.Matricula_Entrada_Sistema import (
    MatriculaEntradaSistema, StatusMatricula, ModalidadeEnsino
)
from backend.app.models.Dossie_Perfil_Longitudinal_Estudante import DossiePerfilLongitudinalEstudante
from backend.app.utils.SUAP_Sincronizacao_Dados_Aluno import buscar_dados_suap

async def registrar_estudante_via_suap(
    matricula_suap       : str,
    declarou_necessidade : bool,
    modalidade           : ModalidadeEnsino,
    suap_username        : str,
    suap_password        : str,
    db                   : AsyncSession,
) -> MatriculaEntradaSistema:

    # 1. Puxa dados do SUAP (faz o login na hora com as credenciais fornecidas)
    dados = await buscar_dados_suap(suap_username, suap_password)

    # 2. Verifica se o estudante já existe por matrícula
    result = await db.execute(
        select(EstudanteDadosCadastrais)
        .where(EstudanteDadosCadastrais.matricula_suap == matricula_suap)
    )
    estudante = result.scalar_one_or_none()

    if not estudante:
        estudante = EstudanteDadosCadastrais(
            nome_registro  = dados["nome"],
            matricula_suap = dados["matricula"],
            cpf            = dados["cpf"],
            data_nascimento= date(1900, 1, 1),  # Placeholder pois o SUAP não retornou no teste inicial
            email          = dados["email"],
            campus         = dados["campus"],
        )
        db.add(estudante)
        await db.flush()  # Gera o ID para as FKs

    # 3. Cria a matrícula no NAPNE 360
    status_inicial = (
        StatusMatricula.aguardando_triagem
        if declarou_necessidade
        else StatusMatricula.dossie_ativo
    )
    
    matricula = MatriculaEntradaSistema(
        id_estudante         = estudante.id,
        curso                = dados["curso"],
        modalidade           = modalidade,
        periodo_referencia   = dados["periodo"],
        declarou_necessidade = declarou_necessidade,
        status               = status_inicial,
        data_matricula       = date.today(),
    )
    db.add(matricula)
    await db.flush()

    # 4. Cria dossiê se não existir
    result_dossie = await db.execute(
        select(DossiePerfilLongitudinalEstudante)
        .where(DossiePerfilLongitudinalEstudante.id_estudante == estudante.id)
    )
    if not result_dossie.scalar_one_or_none():
        dossie = DossiePerfilLongitudinalEstudante(id_estudante=estudante.id)
        db.add(dossie)

    await db.commit()
    
    # Refresh com eager loading dos dados do estudante para o schema de resposta
    stmt = (
        select(MatriculaEntradaSistema)
        .options(selectinload(MatriculaEntradaSistema.estudante))
        .where(MatriculaEntradaSistema.id == matricula.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()
