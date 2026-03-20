# NAPNE 360° — Requisitos do Sistema
> Versão: 1.1 (revisada) | Eng. Sistemas | IFAC

---

## Contexto

Sistema web integrado para digitalizar, integrar e automatizar todos os fluxos do NAPNE —
do ingresso do estudante PCD à conclusão do curso. Usuários primários: equipe NAPNE (baixo
letramento digital), docentes (acesso esporádico), gestão institucional (relatórios).

---

## Requisitos Funcionais (RF)

### RF01 — Módulo: Matricula_Triagem_CID_Automatica

| ID | Requisito |
|----|-----------|
| RF01.1 | Ao receber matrícula com declaração de necessidade, criar automaticamente dossiê digital vazio e agendar entrevista inicial |
| RF01.2 | Classificar CIDs em três categorias: (a) apenas cota — sem fluxo NAPNE, (b) suporte NAPNE, (c) ambos |
| RF01.3 | Registrar flag `suspeita_fraude` quando CID for declarado sem laudo anexado e pertencer à categoria suspeita (configurável pelo admin) |
| RF01.4 | Notificar todos os docentes das turmas do estudante **antes** do primeiro dia de aula com resumo de adaptações necessárias |
| RF01.5 | Disparar alerta quando estudante PCD for matriculado mas triagem não estiver concluída em até 5 dias úteis |
| RF01.6 | Registrar consentimento LGPD do estudante ou responsável no ato da matrícula; bloquear criação do dossiê sem consentimento |

### RF02 — Módulo: Entrevista_Estruturada_Motor_Hipoteses

| ID | Requisito |
|----|-----------|
| RF02.1 | Organizar entrevista em 4 categorias fixas: Desenvolvimento, Escolarização, Comportamento, Saúde |
| RF02.2 | Gerar hipóteses diagnósticas em tempo real conforme respostas são inseridas (motor data-driven, regras editáveis via painel admin) |
| RF02.3 | Ex de regra: dificuldade de concentração + impulsividade + baixo rendimento → hipótese: comprometimento de função executiva (controle inibitório) |
| RF02.4 | Mapear potencialidades do estudante durante a entrevista |
| RF02.5 | Identificar estilo de aprendizagem predominante (visual, auditivo, cinestésico, leitura/escrita) |
| RF02.6 | Salvar estado parcial da entrevista; permitir retomada em outra sessão |
| RF02.7 | Hipóteses geradas ficam pendentes de confirmação pelo entrevistador antes de alimentar o PEI |

### RF03 — Módulo: Dossie_Perfil_Longitudinal_Estudante

| ID | Requisito |
|----|-----------|
| RF03.1 | Preservar histórico completo entre períodos letivos, mudanças de modalidade, transferências e trocas de gestor NAPNE |
| RF03.2 | Suportar anexo de laudos, relatórios médicos e psicológicos (PDF/imagem, máx. 20MB por arquivo) |
| RF03.3 | Exibir linha do tempo visual do ingresso à conclusão com todos os eventos registrados |
| RF03.4 | Manter perfil cognitivo, comportamental e mapa de funções executivas comprometidas |
| RF03.5 | Registrar cada acesso a dados sensíveis no log de auditoria (LGPD) |

### RF04 — Módulo: PEI_Gerador_Automatico_Por_Perfil

| ID | Requisito |
|----|-----------|
| RF04.1 | Gerar PEI automaticamente cruzando: diagnóstico confirmado + potencialidades + área do curso + funções executivas + estilo de aprendizagem |
| RF04.2 | Para área Exatas: gerar estratégias específicas (checklists, timers, uso de régua, material em etapas) |
| RF04.3 | Para área Linguagens: gerar estratégias específicas (produção oral, mapas mentais, revisão em voz alta) |
| RF04.4 | Para área Tecnologia/Engenharia: gerar estratégias específicas (pair programming adaptado, tutoriais em vídeo) |
| RF04.5 | PEI deve conter obrigatoriamente: objetivos pedagógicos por período, estratégias por área, adaptações curriculares, tecnologias assistivas sugeridas |
| RF04.6 | Adaptações curriculares disponíveis: tempo extra, avaliação alternativa, assento preferencial, material adaptado, intérprete LIBRAS |
| RF04.7 | Alertar equipe NAPNE quando PEI ativo não for revisado há mais de 60 dias |
| RF04.8 | Gerar relatório simplificado por disciplina para cada docente (orientações práticas) |
| RF04.9 | Suportar assinatura digital do PEI para exportação com integridade (hash SHA-256) |
| RF04.10 | Regras de geração do PEI são data-driven (tabela `Regra_Motor_Hipoteses`), editáveis sem novo deploy |

### RF05 — Módulo: Relatorio_Docente_Mensal_Rapido

| ID | Requisito |
|----|-----------|
| RF05.1 | Docente recebe link com token único mensal; abre formulário sem necessidade de login completo |
| RF05.2 | Formulário deve ser completável em até 1 minuto; campos: nota atual, % frequência, engajamento (1–5), mudança comportamental (sim/não + campo opcional) |
| RF05.3 | Token expira em 15 dias; após expiração, gerar novo token e notificar docente |
| RF05.4 | Gerar gráficos de evolução de rendimento, frequência e engajamento ao longo do semestre |
| RF05.5 | Sistema deve marcar como "sem retorno" quando docente não preencher em 2 meses consecutivos e alertar equipe NAPNE |

### RF06 — Módulo: Alerta_Motor_Disparo_Regras_Risco

| ID | Requisito |
|----|-----------|
| RF06.1 | Alerta VERMELHO: queda de rendimento > 2 pontos em relação ao mês anterior |
| RF06.2 | Alerta LARANJA: 3 ou mais faltas consecutivas reportadas |
| RF06.3 | Alerta LARANJA: docente reportar mudança comportamental |
| RF06.4 | Alerta AZUL: PEI ativo sem revisão há mais de 60 dias |
| RF06.5 | Regras de alerta são data-driven (tabela `Regra_Alerta_Configuracao`), editáveis pelo admin sem deploy |
| RF06.6 | Alertas têm ciclo de vida: ativo → em acompanhamento → resolvido; com responsável e observação de resolução |
| RF06.7 | Dashboard mostrando alertas pendentes agrupados por tipo, turma e modalidade |

### RF07 — Módulo: Dashboard_Painel_Controle_NAPNE

| ID | Requisito |
|----|-----------|
| RF07.1 | Visão geral: total de estudantes ativos, alertas por tipo, distribuição por modalidade e curso |
| RF07.2 | Acesso rápido (máx. 2 cliques) a: nova triagem, lista de alertas, PEI pendente |
| RF07.3 | Indicadores institucionais prontos para auditoria: % PEIs gerados, % docentes com formulário em dia, estudantes por tipo de necessidade |

### RF08 — Módulo: Relatorio_Auditoria_Exportacao_Institucional

| ID | Requisito |
|----|-----------|
| RF08.1 | Exportar histórico completo do estudante em PDF pronto para auditoria de órgãos de controle |
| RF08.2 | Exportar PEI com hash de integridade e data/hora de geração |
| RF08.3 | Gerar relatório agregado por período (indicadores institucionais, anônimo para fins estatísticos) |
| RF08.4 | Linha do tempo exportável: ingresso → entrevista → PEI → monitoramento → conclusão |

### RF09 — Módulo: Usuario_Controle_Acesso_RBAC

| ID | Requisito |
|----|-----------|
| RF09.1 | Perfis: NAPNE (acesso pleno), Docente (apenas seus estudantes), Gestão (relatórios/indicadores, sem PII), Admin (configuração de regras/CIDs) |
| RF09.2 | Docente não acessa dossiê completo — apenas relatório simplificado por disciplina e formulário mensal |
| RF09.3 | Log de auditoria obrigatório para CREATE/UPDATE/DELETE em dados sensíveis (diagnóstico, laudo, PEI) |
| RF09.4 | Sessão expira em 8 horas de inatividade; re-autenticação obrigatória para ações destrutivas |

### RF10 — Módulo: Integracao_NAES_UFAC (Fase 2)

| ID | Requisito |
|----|-----------|
| RF10.1 | Arquitetura deve prever integração futura com NAES da UFAC via API REST |
| RF10.2 | Endpoints documentados via OpenAPI/Swagger; autenticação OAuth2 client_credentials |
| RF10.3 | Exportar/importar dossiê de estudante transferido entre instituições com consentimento registrado |

---

## Requisitos Não-Funcionais (RNF)

### RNF01 — Usabilidade (Público: baixo letramento digital)

| ID | Requisito |
|----|-----------|
| RNF01.1 | Nenhuma ação crítica exige mais de 3 cliques a partir do dashboard |
| RNF01.2 | Formulário do docente deve funcionar em celular sem instalação de app |
| RNF01.3 | Mensagens de erro em português claro, sem termos técnicos; com sugestão de ação |
| RNF01.4 | Ícones sempre acompanhados de rótulo textual (não depender só de ícone) |
| RNF01.5 | Fonte mínima de 16px; botões com área de toque mínima de 44×44px |
| RNF01.6 | Campos de formulário com label visível acima do campo (não placeholder como label) |

### RNF02 — Acessibilidade

| ID | Requisito |
|----|-----------|
| RNF02.1 | Conformidade WCAG 2.1 nível AA |
| RNF02.2 | Compatível com NVDA e JAWS (leitores de tela) |
| RNF02.3 | Contraste mínimo 4.5:1 para texto normal, 3:1 para texto grande |
| RNF02.4 | Navegação completa por teclado |

### RNF03 — Performance

| ID | Requisito |
|----|-----------|
| RNF03.1 | Tempo de resposta < 3s para 95% das requisições em conexão de 1 Mbps |
| RNF03.2 | Geração do PEI (operação pesada) < 8s com feedback visual de progresso |
| RNF03.3 | Suportar até 200 usuários simultâneos sem degradação perceptível |

### RNF04 — Segurança e LGPD

| ID | Requisito |
|----|-----------|
| RNF04.1 | Dados de saúde e diagnóstico classificados como dados sensíveis (LGPD Art. 11) |
| RNF04.2 | Criptografia AES-256 em repouso para campos de diagnóstico, laudos e PEI |
| RNF04.3 | HTTPS obrigatório (TLS 1.2+); HSTS habilitado |
| RNF04.4 | Consentimento LGPD registrado com timestamp, versão do termo e IP de origem |
| RNF04.5 | Relatórios agregados/estatísticos devem anonimizar dados antes de exibir |
| RNF04.6 | Tokens de link direto (docentes) são UUID v4 de uso único por mês |

### RNF05 — Disponibilidade e Confiabilidade

| ID | Requisito |
|----|-----------|
| RNF05.1 | Disponibilidade mínima 99,5% (≈ 43h downtime/ano) |
| RNF05.2 | Backup automático diário com retenção de 90 dias |
| RNF05.3 | RTO (Recovery Time Objective) ≤ 4h; RPO ≤ 24h |
| RNF05.4 | Falha no envio de notificação deve ser enfileirada e re-tentada até 3 vezes |

### RNF06 — Manutenibilidade

| ID | Requisito |
|----|-----------|
| RNF06.1 | Arquitetura em camadas: routes → services → repositories → models |
| RNF06.2 | Cobertura de testes ≥ 80% para: PEI_Gerador, Alerta_Motor, Entrevista_Motor_Hipoteses, Matricula_Triagem |
| RNF06.3 | Regras de negócio (PEI e alertas) data-driven — editáveis pelo admin sem deploy |
| RNF06.4 | Migrations versionadas com Alembic (Python) ou similar |
| RNF06.5 | API documentada via OpenAPI/Swagger, mantida junto ao código |

### RNF07 — Portabilidade

| ID | Requisito |
|----|-----------|
| RNF07.1 | Compatível com Chrome, Firefox, Edge (últimas 2 versões) |
| RNF07.2 | Responsivo a partir de 360px (mobile-first) |
| RNF07.3 | Funcional em conexões de 1 Mbps (imagens lazy-loaded, sem assets pesados críticos) |
| RNF07.4 | Deploy em container Docker; independente de SO do servidor |
