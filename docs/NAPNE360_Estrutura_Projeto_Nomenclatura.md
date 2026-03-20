# NAPNE 360° — Estrutura do Projeto e Convenção de Nomenclatura
> Versão: 1.1 | Stack: Python/FastAPI + React/Next.js + PostgreSQL

---

## Princípio da Nomenclatura

```
<Domínio>_<O_Que_É>_<Contexto_Extra>.extensão

Correto:   PEI_Gerador_Automatico_Por_Perfil.py
Correto:   Alerta_Motor_Disparo_Regras_Risco.py
Correto:   Estudante_Lista_Ativos_PCD.jsx
Errado:    pei_modules.py       ← sem domínio claro
Errado:    utils.py             ← genérico demais
Errado:    helpers.js           ← não remete a nada
```

Cada nome de arquivo deve responder: "Qual domínio? O que faz? Para quem?"

---

## Estrutura Completa

```
napne360/
├── .env.example
├── .gitignore
├── docker-compose.yml
├── README_Visao_Geral_Projeto.md
│
├── docs/
│   ├── RF_RNF_Requisitos_Sistema_NAPNE360.md
│   ├── DER_Banco_de_Dados_NAPNE360.sql
│   ├── MER_Modelo_Entidade_Relacionamento.md
│   ├── Roadmap_Fases_Entrega_MVP.md
│   ├── Arquitetura_Sistema_Componentes_Visao_Geral.md
│   ├── LGPD_Politica_Tratamento_Dados_Sensiveis.md
│   └── API_Documentacao_Endpoints_OpenAPI.yaml
│
├── backend/                         (Python 3.12 + FastAPI)
│   ├── requirements.txt
│   ├── main.py
│   ├── Dockerfile_Backend
│   │
│   ├── alembic/                     (migrations versionadas)
│   │   └── versions/
│   │       ├── 001_Estudante_Dossie_Estrutura_Inicial.py
│   │       ├── 002_PEI_Tabelas_Gerador.py
│   │       ├── 003_Alerta_Monitoramento_Tabelas.py
│   │       └── 004_Regras_Motor_Hipoteses_Alertas.py
│   │
│   ├── app/
│   │   ├── database.py
│   │   │
│   │   ├── models/                  (SQLAlchemy ORM — 1 arquivo = 1 entidade)
│   │   │   ├── Usuario_Perfil_Acesso.py
│   │   │   ├── Log_Auditoria_Dados_Sensiveis.py
│   │   │   ├── CID_Classificacao_Tipo_Necessidade.py
│   │   │   ├── Funcao_Executiva_Catalogo.py
│   │   │   ├── Periodo_Letivo_Calendario.py
│   │   │   ├── Curso_Area_Conhecimento.py
│   │   │   ├── Disciplina_Grade_Curricular.py
│   │   │   ├── Docente_Perfil_Vinculo.py
│   │   │   ├── Turma_Disciplina_Periodo.py
│   │   │   ├── Estudante_Dados_Cadastrais.py
│   │   │   ├── Matricula_Entrada_Sistema.py
│   │   │   ├── Consentimento_LGPD_Estudante.py
│   │   │   ├── Estudante_CID_Diagnostico_Vinculo.py
│   │   │   ├── Estudante_Turma_Matricula_Disciplina.py
│   │   │   ├── Dossie_Perfil_Longitudinal_Estudante.py
│   │   │   ├── Dossie_Funcao_Executiva_Comprometida.py
│   │   │   ├── Potencialidade_Mapeada_Entrevista.py
│   │   │   ├── Documento_Laudo_Anexado.py
│   │   │   ├── Entrevista_Estruturada_Sessao.py
│   │   │   ├── Entrevista_Resposta_Por_Categoria.py
│   │   │   ├── Hipotese_Diagnostica_Gerada.py
│   │   │   ├── Regra_Motor_Hipoteses.py
│   │   │   ├── PEI_Plano_Educacional_Individual.py
│   │   │   ├── PEI_Objetivo_Pedagogico_Periodo.py
│   │   │   ├── PEI_Estrategia_Por_Area_Curso.py
│   │   │   ├── PEI_Adaptacao_Curricular.py
│   │   │   ├── PEI_Tecnologia_Assistiva_Sugerida.py
│   │   │   ├── PEI_Relatorio_Simplificado_Docente.py
│   │   │   ├── Formulario_Mensal_Docente_Resposta.py
│   │   │   ├── Regra_Alerta_Configuracao.py
│   │   │   ├── Alerta_Monitoramento_Risco_Estudante.py
│   │   │   └── Notificacao_Usuario_Sistema.py
│   │   │
│   │   ├── schemas/                 (Pydantic — validação I/O)
│   │   │   ├── Estudante_Schema_Cadastro_Resposta.py
│   │   │   ├── Matricula_Schema_Entrada_Triagem.py
│   │   │   ├── Entrevista_Schema_Sessao_Respostas.py
│   │   │   ├── PEI_Schema_Gerador_Visualizacao.py
│   │   │   ├── Formulario_Mensal_Schema_Docente.py
│   │   │   ├── Alerta_Schema_Monitoramento_Risco.py
│   │   │   └── Dashboard_Schema_Indicadores_Painel.py
│   │   │
│   │   ├── services/                (lógica de negócio — testável, sem HTTP)
│   │   │   ├── PEI_Gerador_Automatico_Por_Perfil.py        ★ core
│   │   │   ├── Entrevista_Motor_Hipoteses_Tempo_Real.py    ★ core
│   │   │   ├── Alerta_Motor_Disparo_Regras_Risco.py        ★ core
│   │   │   ├── Matricula_Triagem_CID_Automatica.py         ★ core
│   │   │   ├── Docente_Token_Link_Formulario_Mensal.py
│   │   │   ├── Notificacao_Docente_Primeiro_Dia_Aula.py
│   │   │   ├── Relatorio_PDF_Exportador_Auditoria.py
│   │   │   ├── PEI_Revisao_Alerta_60_Dias.py
│   │   │   └── LGPD_Consentimento_Anonimizacao_Dados.py
│   │   │
│   │   ├── routes/                  (FastAPI routers — apenas HTTP)
│   │   │   ├── Matricula_Rotas_Triagem_Entrada.py
│   │   │   ├── Estudante_Rotas_Dossie_CRUD.py
│   │   │   ├── Entrevista_Rotas_Formulario_Hipoteses.py
│   │   │   ├── PEI_Rotas_Gerador_Edicao_Export.py
│   │   │   ├── Docente_Rotas_Formulario_Mensal.py
│   │   │   ├── Alerta_Rotas_Dashboard_Monitoramento.py
│   │   │   ├── Dashboard_Rotas_Painel_Indicadores.py
│   │   │   └── Relatorio_Rotas_Auditoria_Exportacao.py
│   │   │
│   │   └── utils/
│   │       ├── Auth_JWT_Controle_Perfis_RBAC.py
│   │       ├── Auth_Token_Link_Docente_Sem_Login.py
│   │       ├── CID_Tabela_Triagem_Classificacao.py
│   │       ├── Criptografia_AES256_Campos_Sensiveis.py
│   │       └── Log_Auditoria_Decorator_LGPD.py
│   │
│   └── tests/
│       ├── PEI_Teste_Gerador_Perfis_Distintos.py           ★ 80%+ cobertura
│       ├── PEI_Teste_Gerador_Area_Exatas_Linguagens.py
│       ├── Alerta_Teste_Motor_Regras_Disparo.py            ★
│       ├── Entrevista_Teste_Motor_Hipoteses.py             ★
│       ├── Matricula_Teste_Triagem_CID_Categorias.py       ★
│       ├── Docente_Teste_Token_Link_Mensal.py
│       └── LGPD_Teste_Consentimento_Bloqueio.py
│
└── frontend/                        (React + Next.js 14 — App Router)
    ├── package.json
    ├── Dockerfile_Frontend
    │
    └── src/
        ├── app/                     (pages — Next.js App Router)
        │   ├── dashboard/
        │   │   └── Dashboard_Painel_Controle_NAPNE.tsx
        │   ├── estudantes/
        │   │   ├── Estudante_Lista_Ativos_PCD.tsx
        │   │   └── [id]/
        │   │       └── Estudante_Dossie_Perfil_Completo.tsx
        │   ├── matricula/
        │   │   └── Matricula_Formulario_Nova_Triagem.tsx
        │   ├── entrevista/
        │   │   └── Entrevista_Formulario_Estruturado.tsx
        │   ├── pei/
        │   │   └── PEI_Visualizacao_Edicao_Exportacao.tsx
        │   ├── docente/
        │   │   └── Docente_Formulario_Mensal_Rapido.tsx   ← público, token
        │   ├── alertas/
        │   │   └── Alerta_Lista_Monitoramento_Ativo.tsx
        │   └── relatorios/
        │       └── Relatorio_Exportacao_Auditoria.tsx
        │
        └── components/
            ├── Alerta_Card_Visual_Por_Tipo_Cor.tsx
            ├── PEI_Secao_Estrategias_Por_Area.tsx
            ├── PEI_Secao_Adaptacoes_Curriculares.tsx
            ├── Estudante_Linha_Tempo_Historico_Visual.tsx
            ├── Grafico_Evolucao_Rendimento_Semestre.tsx
            ├── Grafico_Evolucao_Frequencia_Mensal.tsx
            ├── Dashboard_Card_Indicador_Institucional.tsx
            ├── Formulario_Campo_Acessivel_Label_Visivel.tsx
            ├── Formulario_Selector_CID_Busca.tsx
            └── Modal_Confirmacao_Acao_Destrutiva.tsx
```

---

## Regras de Ouro da Nomenclatura

1. **Domínio primeiro**: PEI_, Alerta_, Matricula_, Estudante_, Docente_, Dashboard_
2. **O que é depois**: _Gerador, _Motor, _Lista, _Formulario, _Schema, _Rotas, _Teste
3. **Contexto no final**: _Por_Perfil, _Tempo_Real, _Ativos_PCD, _Sem_Login
4. **Nunca abreviar domínio**: `Estudante_` não vira `Est_`
5. **PascalCase por segmento separado por `_`**: cada segmento é uma palavra ou frase curta
6. **Migrations incluem número de sequência**: `001_`, `002_` — facilita rollback e ordenação

---

## Regras de Arquitetura

```
routes/  →  só HTTP (request/response, auth, serialização)
services/ → só lógica de negócio (sem request, sem response)
models/  →  só mapeamento ORM
utils/   →  só funções puras sem estado de domínio

Proibido: lógica de negócio em routes/
Proibido: consulta SQL direta em routes/ (use services/)
Proibido: import de models em routes/ (passe por services/)
```

---

## Serviços Core (★) — Prioridade de Desenvolvimento

| Serviço | Por quê é core |
|---------|----------------|
| `PEI_Gerador_Automatico_Por_Perfil` | Principal diferencial do sistema |
| `Entrevista_Motor_Hipoteses_Tempo_Real` | Alimenta o PEI; complexidade alta |
| `Alerta_Motor_Disparo_Regras_Risco` | Segurança do estudante; zero tolerância a falsos negativos |
| `Matricula_Triagem_CID_Automatica` | Portão de entrada; erro aqui contamina todo o fluxo |

Estes quatro devem ter cobertura de testes ≥ 80% **antes** de qualquer deploy em produção.
