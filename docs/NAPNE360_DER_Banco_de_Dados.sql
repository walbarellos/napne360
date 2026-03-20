-- ============================================================
-- NAPNE 360° — DER — Banco de Dados (PostgreSQL 15+)
-- Versão: 1.1 (revisada)
-- Encoding: UTF-8
-- Convenção: snake_case, nomes de tabelas descritivos
-- ============================================================

-- ============================================================
-- TIPOS ENUMERADOS
-- ============================================================

CREATE TYPE perfil_usuario         AS ENUM ('napne', 'docente', 'gestao', 'admin');
CREATE TYPE status_alerta          AS ENUM ('ativo', 'em_acompanhamento', 'resolvido');
CREATE TYPE tipo_alerta            AS ENUM ('queda_rendimento', 'faltas_consecutivas', 'mudanca_comportamental', 'pei_sem_revisao');
CREATE TYPE categoria_cid          AS ENUM ('cota_apenas', 'napne_suporte', 'ambos');
CREATE TYPE categoria_entrevista   AS ENUM ('desenvolvimento', 'escolarizacao', 'comportamento', 'saude');
CREATE TYPE area_curso             AS ENUM ('exatas', 'linguagens', 'tecnologia', 'engenharia', 'saude', 'gestao', 'outros');
CREATE TYPE modalidade_ensino      AS ENUM ('medio_integrado', 'subsequente', 'superior');
CREATE TYPE status_pei             AS ENUM ('rascunho', 'ativo', 'revisao_pendente', 'arquivado');
CREATE TYPE nivel_comprometimento  AS ENUM ('leve', 'moderado', 'severo');
CREATE TYPE tipo_adaptacao         AS ENUM (
    'tempo_extra', 'avaliacao_alternativa', 'assento_preferencial',
    'material_adaptado', 'interprete_libras', 'outro'
);
CREATE TYPE origem_diagnostico     AS ENUM ('autodeclarado', 'laudo_medico', 'laudo_psicologico', 'relatorio_escolar');
CREATE TYPE status_matricula       AS ENUM ('ativo', 'concluido', 'evadido', 'transferido', 'trancado');

-- ============================================================
-- USUARIOS E CONTROLE DE ACESSO
-- ============================================================

CREATE TABLE Usuario_Perfil_Acesso (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            VARCHAR(200)    NOT NULL,
    cpf             CHAR(11)        UNIQUE NOT NULL,
    email           VARCHAR(150)    UNIQUE NOT NULL,
    senha_hash      VARCHAR(255)    NOT NULL,
    perfil          perfil_usuario  NOT NULL,
    ativo           BOOLEAN         DEFAULT TRUE,
    criado_em       TIMESTAMPTZ     DEFAULT NOW(),
    atualizado_em   TIMESTAMPTZ     DEFAULT NOW()
);

-- Registro imutável: INSERT only, nunca UPDATE/DELETE (append-only audit)
CREATE TABLE Log_Auditoria_Acesso_Dados_Sensiveis (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario          UUID        NOT NULL REFERENCES Usuario_Perfil_Acesso(id),
    acao                VARCHAR(50) NOT NULL,       -- 'leitura', 'criacao', 'edicao', 'exclusao'
    tabela_alvo         VARCHAR(100) NOT NULL,
    id_registro_alvo    UUID,
    ip_origem           INET,
    detalhes            JSONB,
    criado_em           TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CATÁLOGOS: CID, FUNÇÕES EXECUTIVAS, PERÍODO, CURSO
-- ============================================================

CREATE TABLE CID_Classificacao_Tipo_Necessidade (
    id          UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    codigo      VARCHAR(10)     UNIQUE NOT NULL,    -- ex: F84.0, H54.0
    descricao   TEXT            NOT NULL,
    categoria   categoria_cid   NOT NULL,
    grupo       VARCHAR(100),                       -- ex: 'TEA', 'TDAH', 'Deficiência Visual'
    alto_risco_fraude BOOLEAN   DEFAULT FALSE,      -- marcado pelo admin para triagem extra
    ativo       BOOLEAN         DEFAULT TRUE
);

CREATE TABLE Funcao_Executiva_Catalogo (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nome                VARCHAR(100) UNIQUE NOT NULL,
    descricao           TEXT,
    exemplos_impacto    TEXT        -- ex: "dificuldade de iniciar tarefas, perda de material"
);

CREATE TABLE Periodo_Letivo_Calendario (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    ano         SMALLINT    NOT NULL,
    semestre    SMALLINT    NOT NULL    CHECK (semestre IN (1, 2)),
    data_inicio DATE        NOT NULL,
    data_fim    DATE        NOT NULL,
    ativo       BOOLEAN     DEFAULT FALSE,
    UNIQUE(ano, semestre)
);

CREATE TABLE Curso_Area_Conhecimento (
    id          UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    nome        VARCHAR(200)        NOT NULL,
    codigo      VARCHAR(20)         UNIQUE NOT NULL,
    area        area_curso          NOT NULL,
    modalidade  modalidade_ensino   NOT NULL,
    ativo       BOOLEAN             DEFAULT TRUE
);

CREATE TABLE Disciplina_Grade_Curricular (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            VARCHAR(200) NOT NULL,
    codigo          VARCHAR(20)  UNIQUE NOT NULL,
    id_curso        UUID         NOT NULL REFERENCES Curso_Area_Conhecimento(id),
    carga_horaria   SMALLINT     NOT NULL,
    ativo           BOOLEAN      DEFAULT TRUE
);

CREATE TABLE Docente_Perfil_Vinculo (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario      UUID        NOT NULL UNIQUE REFERENCES Usuario_Perfil_Acesso(id),
    siape           VARCHAR(20) UNIQUE,
    matricula_inst  VARCHAR(20),
    especialidade   VARCHAR(200),
    ativo           BOOLEAN     DEFAULT TRUE
);

CREATE TABLE Turma_Disciplina_Periodo (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_disciplina   UUID        NOT NULL REFERENCES Disciplina_Grade_Curricular(id),
    id_docente      UUID        NOT NULL REFERENCES Docente_Perfil_Vinculo(id),
    id_periodo      UUID        NOT NULL REFERENCES Periodo_Letivo_Calendario(id),
    codigo_turma    VARCHAR(20) NOT NULL,
    horario         VARCHAR(100),
    UNIQUE(id_disciplina, id_periodo, codigo_turma)
);

-- ============================================================
-- ESTUDANTE, MATRÍCULA E LGPD
-- ============================================================

CREATE TABLE Estudante_Dados_Cadastrais (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nome                VARCHAR(200) NOT NULL,
    cpf                 CHAR(11)    UNIQUE NOT NULL,
    data_nascimento     DATE        NOT NULL,
    email               VARCHAR(150),
    telefone            VARCHAR(20),
    responsavel_nome    VARCHAR(200),   -- para menores de 18 anos
    responsavel_tel     VARCHAR(20),
    criado_em           TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em       TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE Matricula_Entrada_Sistema (
    id                      UUID                PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudante            UUID                NOT NULL REFERENCES Estudante_Dados_Cadastrais(id),
    id_curso                UUID                NOT NULL REFERENCES Curso_Area_Conhecimento(id),
    id_periodo_inicio       UUID                NOT NULL REFERENCES Periodo_Letivo_Calendario(id),
    numero_matricula        VARCHAR(30)         UNIQUE NOT NULL,
    status                  status_matricula    NOT NULL DEFAULT 'ativo',
    data_matricula          DATE                NOT NULL,
    declarou_necessidade    BOOLEAN             DEFAULT FALSE,
    triagem_concluida       BOOLEAN             DEFAULT FALSE,
    criado_em               TIMESTAMPTZ         DEFAULT NOW()
);

CREATE TABLE Consentimento_LGPD_Estudante (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_matricula        UUID        NOT NULL REFERENCES Matricula_Entrada_Sistema(id),
    versao_termo        VARCHAR(20) NOT NULL,       -- ex: '2025.1'
    consentido          BOOLEAN     NOT NULL,
    data_consentimento  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_origem           INET,
    hash_documento      TEXT        -- SHA-256 do PDF do termo assinado
);

CREATE TABLE Estudante_CID_Diagnostico_Vinculo (
    id                  UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
    id_matricula        UUID                    NOT NULL REFERENCES Matricula_Entrada_Sistema(id),
    id_cid              UUID                    NOT NULL REFERENCES CID_Classificacao_Tipo_Necessidade(id),
    origem              origem_diagnostico      NOT NULL,
    data_diagnostico    DATE,
    suspeita_fraude     BOOLEAN                 DEFAULT FALSE,
    observacao_fraude   TEXT,
    criado_em           TIMESTAMPTZ             DEFAULT NOW(),
    UNIQUE(id_matricula, id_cid)
);

CREATE TABLE Estudante_Turma_Matricula_Disciplina (
    id              UUID    PRIMARY KEY DEFAULT gen_random_uuid(),
    id_matricula    UUID    NOT NULL REFERENCES Matricula_Entrada_Sistema(id),
    id_turma        UUID    NOT NULL REFERENCES Turma_Disciplina_Periodo(id),
    UNIQUE(id_matricula, id_turma)
);

-- ============================================================
-- DOSSIÊ LONGITUDINAL
-- ============================================================

CREATE TABLE Dossie_Perfil_Longitudinal_Estudante (
    id                      UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_estudante            UUID        NOT NULL UNIQUE REFERENCES Estudante_Dados_Cadastrais(id),
    estilo_aprendizagem     VARCHAR(100),   -- visual | auditivo | cinestesico | leitura_escrita
    perfil_cognitivo        TEXT,
    perfil_comportamental   TEXT,
    observacoes_gerais      TEXT,
    criado_em               TIMESTAMPTZ DEFAULT NOW(),
    atualizado_em           TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE Dossie_Funcao_Executiva_Comprometida (
    id          UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
    id_dossie   UUID                    NOT NULL REFERENCES Dossie_Perfil_Longitudinal_Estudante(id),
    id_funcao   UUID                    NOT NULL REFERENCES Funcao_Executiva_Catalogo(id),
    nivel       nivel_comprometimento   NOT NULL,
    observacao  TEXT,
    UNIQUE(id_dossie, id_funcao)
);

CREATE TABLE Potencialidade_Mapeada_Entrevista (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_dossie   UUID        NOT NULL REFERENCES Dossie_Perfil_Longitudinal_Estudante(id),
    descricao   TEXT        NOT NULL,
    categoria   VARCHAR(100),
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE Documento_Laudo_Anexado (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_dossie           UUID        NOT NULL REFERENCES Dossie_Perfil_Longitudinal_Estudante(id),
    tipo                VARCHAR(50) NOT NULL,   -- laudo_medico | laudo_psicologico | relatorio_escolar | outro
    nome_arquivo        VARCHAR(255) NOT NULL,
    caminho_storage     TEXT        NOT NULL,   -- caminho no object storage (S3-compatible)
    tamanho_bytes       INTEGER,
    mime_type           VARCHAR(100),
    id_usuario_upload   UUID        NOT NULL REFERENCES Usuario_Perfil_Acesso(id),
    criado_em           TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ENTREVISTA ESTRUTURADA
-- ============================================================

CREATE TABLE Entrevista_Estruturada_Sessao (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_dossie           UUID        NOT NULL REFERENCES Dossie_Perfil_Longitudinal_Estudante(id),
    id_entrevistador    UUID        NOT NULL REFERENCES Usuario_Perfil_Acesso(id),
    id_periodo          UUID        REFERENCES Periodo_Letivo_Calendario(id),
    data_entrevista     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    concluida           BOOLEAN     DEFAULT FALSE,
    observacoes_finais  TEXT
);

CREATE TABLE Entrevista_Resposta_Por_Categoria (
    id                  UUID                    PRIMARY KEY DEFAULT gen_random_uuid(),
    id_entrevista       UUID                    NOT NULL REFERENCES Entrevista_Estruturada_Sessao(id),
    categoria           categoria_entrevista    NOT NULL,
    pergunta_codigo     VARCHAR(50)             NOT NULL,   -- código da pergunta no banco de perguntas
    resposta            TEXT                    NOT NULL,
    indicador_risco     BOOLEAN                 DEFAULT FALSE
);

-- Hipóteses geradas pelo motor em tempo real
CREATE TABLE Hipotese_Diagnostica_Gerada (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_entrevista       UUID        NOT NULL REFERENCES Entrevista_Estruturada_Sessao(id),
    descricao           TEXT        NOT NULL,
    confianca           SMALLINT    CHECK (confianca BETWEEN 0 AND 100),
    confirmada          BOOLEAN,                -- NULL=pendente | TRUE=confirmada | FALSE=descartada
    id_confirmado_por   UUID        REFERENCES Usuario_Perfil_Acesso(id),
    criado_em           TIMESTAMPTZ DEFAULT NOW()
);

-- Regras data-driven do motor de hipóteses (editáveis pelo admin sem deploy)
CREATE TABLE Regra_Motor_Hipoteses (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    nome            VARCHAR(200) NOT NULL,
    -- ex: [{"campo": "categoria", "valor": "comportamento"}, {"campo": "resposta_contem", "valor": "impulsividade"}]
    condicoes_json  JSONB       NOT NULL,
    hipotese_gerada TEXT        NOT NULL,
    prioridade      SMALLINT    DEFAULT 0,
    ativa           BOOLEAN     DEFAULT TRUE
);

-- ============================================================
-- PEI — PLANO EDUCACIONAL INDIVIDUALIZADO
-- ============================================================

CREATE TABLE PEI_Plano_Educacional_Individual (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_dossie           UUID        NOT NULL REFERENCES Dossie_Perfil_Longitudinal_Estudante(id),
    id_periodo          UUID        NOT NULL REFERENCES Periodo_Letivo_Calendario(id),
    id_gerado_por       UUID        REFERENCES Usuario_Perfil_Acesso(id),
    status              status_pei  NOT NULL DEFAULT 'rascunho',
    gerado_automatico   BOOLEAN     DEFAULT TRUE,
    data_geracao        TIMESTAMPTZ DEFAULT NOW(),
    data_ultima_revisao TIMESTAMPTZ,
    id_revisor          UUID        REFERENCES Usuario_Perfil_Acesso(id),
    hash_assinatura     TEXT,       -- SHA-256 para exportação com integridade
    UNIQUE(id_dossie, id_periodo)
);

CREATE TABLE PEI_Objetivo_Pedagogico_Periodo (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_pei      UUID        NOT NULL REFERENCES PEI_Plano_Educacional_Individual(id),
    descricao   TEXT        NOT NULL,
    prazo       VARCHAR(50),        -- ex: '1 bimestre', '1 semestre'
    alcancado   BOOLEAN,
    observacao  TEXT
);

CREATE TABLE PEI_Estrategia_Por_Area_Curso (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_pei          UUID        NOT NULL REFERENCES PEI_Plano_Educacional_Individual(id),
    area            area_curso  NOT NULL,
    descricao       TEXT        NOT NULL,
    tipo_estrategia VARCHAR(100)    -- checklist | timer | mapa_mental | producao_oral | etc.
);

CREATE TABLE PEI_Adaptacao_Curricular (
    id                  UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    id_pei              UUID            NOT NULL REFERENCES PEI_Plano_Educacional_Individual(id),
    tipo                tipo_adaptacao  NOT NULL,
    descricao           TEXT            NOT NULL,
    requer_espaco_fisico BOOLEAN        DEFAULT FALSE
);

CREATE TABLE PEI_Tecnologia_Assistiva_Sugerida (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_pei      UUID        NOT NULL REFERENCES PEI_Plano_Educacional_Individual(id),
    nome        VARCHAR(200) NOT NULL,
    descricao   TEXT,
    link_recurso TEXT,
    gratuita    BOOLEAN     DEFAULT TRUE
);

-- Relatório simplificado que o docente recebe (por disciplina)
CREATE TABLE PEI_Relatorio_Simplificado_Docente (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_pei              UUID        NOT NULL REFERENCES PEI_Plano_Educacional_Individual(id),
    id_turma            UUID        NOT NULL REFERENCES Turma_Disciplina_Periodo(id),
    id_docente          UUID        NOT NULL REFERENCES Docente_Perfil_Vinculo(id),
    conteudo_resumido   TEXT        NOT NULL,   -- orientações práticas para aquela disciplina
    data_envio          TIMESTAMPTZ DEFAULT NOW(),
    data_leitura        TIMESTAMPTZ,            -- confirmação de leitura pelo docente
    UNIQUE(id_pei, id_turma)
);

-- ============================================================
-- MONITORAMENTO MENSAL
-- ============================================================

CREATE TABLE Formulario_Mensal_Docente_Resposta (
    id                          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_matricula                UUID        NOT NULL REFERENCES Matricula_Entrada_Sistema(id),
    id_turma                    UUID        NOT NULL REFERENCES Turma_Disciplina_Periodo(id),
    id_docente                  UUID        NOT NULL REFERENCES Docente_Perfil_Vinculo(id),
    mes_referencia              DATE        NOT NULL,   -- primeiro dia do mês de referência
    nota_atual                  DECIMAL(4,2),
    frequencia_pct              DECIMAL(5,2),           -- percentual de presença no mês
    engajamento                 SMALLINT    CHECK (engajamento BETWEEN 1 AND 5),
    comportamento_alterado      BOOLEAN     DEFAULT FALSE,
    descricao_comportamento     TEXT,
    token_acesso                UUID        UNIQUE,     -- UUID v4 para link sem login
    token_expira_em             TIMESTAMPTZ,
    preenchido_em               TIMESTAMPTZ,
    UNIQUE(id_matricula, id_turma, mes_referencia)
);

-- ============================================================
-- ALERTAS INTELIGENTES
-- ============================================================

-- Regras data-driven (editáveis pelo admin sem deploy)
CREATE TABLE Regra_Alerta_Configuracao (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    tipo            tipo_alerta NOT NULL,
    nome            VARCHAR(200) NOT NULL,
    descricao       TEXT,
    -- ex: {"campo": "queda_rendimento", "operador": ">", "valor": 2}
    condicao_json   JSONB       NOT NULL,
    cor_visual      VARCHAR(10) NOT NULL,   -- 'vermelho' | 'laranja' | 'azul'
    ativa           BOOLEAN     DEFAULT TRUE
);

CREATE TABLE Alerta_Monitoramento_Risco_Estudante (
    id                      UUID            PRIMARY KEY DEFAULT gen_random_uuid(),
    id_matricula            UUID            NOT NULL REFERENCES Matricula_Entrada_Sistema(id),
    id_regra                UUID            REFERENCES Regra_Alerta_Configuracao(id),
    tipo                    tipo_alerta     NOT NULL,
    descricao               TEXT            NOT NULL,
    dados_contexto          JSONB,          -- snapshot dos dados que dispararam o alerta
    status                  status_alerta   NOT NULL DEFAULT 'ativo',
    id_responsavel          UUID            REFERENCES Usuario_Perfil_Acesso(id),
    observacao_resolucao    TEXT,
    criado_em               TIMESTAMPTZ     DEFAULT NOW(),
    resolvido_em            TIMESTAMPTZ
);

CREATE TABLE Notificacao_Usuario_Sistema (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    id_usuario  UUID        NOT NULL REFERENCES Usuario_Perfil_Acesso(id),
    id_alerta   UUID        REFERENCES Alerta_Monitoramento_Risco_Estudante(id),
    titulo      VARCHAR(200) NOT NULL,
    corpo       TEXT,
    lida        BOOLEAN     DEFAULT FALSE,
    criado_em   TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- ÍNDICES PRINCIPAIS
-- ============================================================

CREATE INDEX idx_estudante_cpf
    ON Estudante_Dados_Cadastrais(cpf);

CREATE INDEX idx_matricula_estudante
    ON Matricula_Entrada_Sistema(id_estudante);

CREATE INDEX idx_matricula_status
    ON Matricula_Entrada_Sistema(status);

CREATE INDEX idx_matricula_triagem_pendente
    ON Matricula_Entrada_Sistema(triagem_concluida, criado_em)
    WHERE triagem_concluida = FALSE AND declarou_necessidade = TRUE;

CREATE INDEX idx_dossie_estudante
    ON Dossie_Perfil_Longitudinal_Estudante(id_estudante);

CREATE INDEX idx_pei_dossie_periodo
    ON PEI_Plano_Educacional_Individual(id_dossie, id_periodo);

CREATE INDEX idx_pei_revisao_pendente
    ON PEI_Plano_Educacional_Individual(data_ultima_revisao)
    WHERE status = 'ativo';

CREATE INDEX idx_alerta_ativo
    ON Alerta_Monitoramento_Risco_Estudante(id_matricula, criado_em)
    WHERE status = 'ativo';

CREATE INDEX idx_formulario_token
    ON Formulario_Mensal_Docente_Resposta(token_acesso)
    WHERE preenchido_em IS NULL;

CREATE INDEX idx_log_usuario_data
    ON Log_Auditoria_Acesso_Dados_Sensiveis(id_usuario, criado_em);

CREATE INDEX idx_cid_vinculo_matricula
    ON Estudante_CID_Diagnostico_Vinculo(id_matricula);

CREATE INDEX idx_entrevista_dossie
    ON Entrevista_Estruturada_Sessao(id_dossie);

CREATE INDEX idx_formulario_mensal_nao_preenchido
    ON Formulario_Mensal_Docente_Resposta(id_docente, mes_referencia)
    WHERE preenchido_em IS NULL;

-- ============================================================
-- COMENTÁRIOS (documentação inline)
-- ============================================================

COMMENT ON TABLE Regra_Motor_Hipoteses IS
    'Regras data-driven para geração de hipóteses diagnósticas. Editáveis pelo admin sem deploy.';

COMMENT ON TABLE Regra_Alerta_Configuracao IS
    'Regras data-driven para disparo de alertas. Editáveis pelo admin sem deploy.';

COMMENT ON TABLE Log_Auditoria_Acesso_Dados_Sensiveis IS
    'Append-only. Nunca fazer UPDATE ou DELETE nesta tabela. Exigência LGPD.';

COMMENT ON COLUMN Estudante_CID_Diagnostico_Vinculo.suspeita_fraude IS
    'Flag manual ou automático para CIDs de alto risco. Não bloqueia o fluxo, apenas sinaliza para revisão.';

COMMENT ON COLUMN Formulario_Mensal_Docente_Resposta.token_acesso IS
    'UUID v4 gerado mensalmente. Docente acessa formulário sem login completo via link com este token.';

COMMENT ON COLUMN PEI_Plano_Educacional_Individual.hash_assinatura IS
    'SHA-256 do conteúdo exportado. Permite verificar integridade em auditorias.';
