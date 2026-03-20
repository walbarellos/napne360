from pydantic import BaseModel
from datetime import date, datetime
from uuid import UUID
from backend.app.models.Matricula_Entrada_Sistema import StatusMatricula, ModalidadeEnsino, TipoCotaPCD

class EstudanteCriarRequest(BaseModel):
    matricula_suap       : str
    declarou_necessidade : bool
    modalidade           : ModalidadeEnsino
    tipo_cota_pcd        : TipoCotaPCD = TipoCotaPCD.nenhuma

class EstudanteResponse(BaseModel):
    id             : UUID
    nome_exibicao  : str
    matricula_suap : str
    curso          : str
    modalidade     : ModalidadeEnsino
    tipo_cota_pcd  : TipoCotaPCD
    status         : StatusMatricula
    criado_em      : datetime

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            nome_exibicao=obj.estudante.nome_exibicao,
            matricula_suap=obj.estudante.matricula_suap,
            curso=obj.curso,
            modalidade=obj.modalidade,
            tipo_cota_pcd=obj.tipo_cota_pcd,
            status=obj.status,
            criado_em=obj.criado_em
        )
