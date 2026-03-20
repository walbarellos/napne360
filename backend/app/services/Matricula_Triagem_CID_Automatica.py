from datetime import date, timezone, datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from backend.app.models.Estudante_Dados_Cadastrais import EstudanteDadosCadastrais
from backend.app.models.Matricula_Entrada_Sistema import (
    MatriculaEntradaSistema, StatusMatricula, ModalidadeEnsino, TipoCotaPCD
)
from backend.app.models.Dossie_Perfil_Longitudinal_Estudante import DossiePerfilLongitudinalEstudante
from backend.app.utils.SUAP_Sincronizacao_Dados_Aluno import buscar_dados_suap

async def registrar_estudante_via_suap(
    matricula_suap       : str,
    declarou_necessidade : bool,
    modalidade           : ModalidadeEnsino,
    tipo_cota_pcd        : TipoCotaPCD,
    suap_username        : str,
    suap_password        : str,
    db                   : AsyncSession,
) -> MatriculaEntradaSistema:

    # 1. puxa dados do SUAP
    dados = await buscar_dados_suap(suap_username, suap_password)

    # 2. estudante já existe?
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
            data_nascimento= date(1900, 1, 1),
            email          = dados["email"],
            campus         = dados["campus"],
        )
        db.add(estudante)
        await db.flush()

    # 3. cria matrícula
    status_inicial = (
        StatusMatricula.aguardando_triagem
        if declarou_necessidade
        else StatusMatricula.dossie_ativo
    )
    matricula = MatriculaEntradaSistema(
        id_estudante         = estudante.id,
        curso                = dados["curso"],
        modalidade           = modalidade,
        tipo_cota_pcd        = tipo_cota_pcd,
        periodo_referencia   = dados["periodo"],
        declarou_necessidade = declarou_necessidade,
        status               = status_inicial,
        data_matricula       = date.today(),
    )
    db.add(matricula)
    await db.flush()

    # 4. cria dossiê vazio automaticamente
    result_dossie = await db.execute(
        select(DossiePerfilLongitudinalEstudante)
        .where(DossiePerfilLongitudinalEstudante.id_estudante == estudante.id)
    )
    if not result_dossie.scalar_one_or_none():
        dossie = DossiePerfilLongitudinalEstudante(id_estudante=estudante.id)
        db.add(dossie)

    await db.commit()
    
    stmt = (
        select(MatriculaEntradaSistema)
        .options(selectinload(MatriculaEntradaSistema.estudante))
        .where(MatriculaEntradaSistema.id == matricula.id)
    )
    result = await db.execute(stmt)
    return result.scalar_one()
