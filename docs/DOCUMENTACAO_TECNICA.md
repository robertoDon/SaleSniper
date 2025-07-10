# Documentação Técnica - Dashboard Cliente Ideal

## Visão Geral

O sistema é um dashboard desenvolvido em Streamlit para análise do Perfil de Cliente Ideal (ICP), segmentação de clientes e projeções de funil de vendas, com autenticação, upload de dados, insights de IA e exportação de resultados.

## Arquitetura e Fluxo Principal

- **Frontend e Backend:** Streamlit (Python)
- **Autenticação:** Usuários e senhas com hash SHA-256, controle de sessão via `st.session_state`
- **Upload de Dados:** Excel (.xlsx) com estrutura padronizada
- **Processamento:** Cálculos de ICP, segmentação, projeções e geração de insights
- **Exportação:** Resultados em CSV, XLSX e PDF
- **IA:** Integração opcional com Ollama para geração de insights

## Principais Módulos

- `scr/streamlit_app.py`: Ponto de entrada, autenticação, navegação, controle de sessão
- `scr/components/dashboard.py`: Análise de ICP, exibição de perfil ideal, insights e ações sugeridas
- `scr/components/segmentacao.py`: Segmentação de clientes por valor ou quantidade
- `scr/components/metas_funil.py`: Projeção de metas, funil de vendas, exportação de resultados
- `scr/services/`: Autenticação, integração com IA, regras de negócio
- `core/`: Lógica central e cálculos
- `adapters/importador.py`: Importação de dados do Excel

## Autenticação e Segurança

- Usuários armazenados em `usuarios.json` (hash SHA-256)
- Apenas administradores podem criar/editar usuários
- Controle de sessão via Streamlit
- Dados sensíveis devem ser mantidos em variáveis de ambiente

## Upload e Processamento de Dados

- Upload de arquivo Excel na aba "Análise de ICP"
- Estrutura obrigatória: nome_cliente, porte, dores, localizacao, segmento, faturamento, ticket_medio, meses_ativo, ltv
- Dados são carregados, validados e processados para análise

## Análise ICP

- Identificação do perfil de cliente ideal com base em métricas do dataset
- Cálculo de ticket médio, LTV, meses ativo, principais segmentos e dores
- Geração de insights e ações sugeridas (com IA, se disponível)

## Segmentação de Clientes

- Segmentação customizável por valor acumulado (80/20) ou quantidade (20/30/30/20)
- Exibição de top clientes por métricas selecionadas
- Resultados apresentados em tabelas dinâmicas

## Metas e Projeções

- Cálculo de metas anuais/mensais, funil de vendas e projeções
- Ajuste por número de vendedores, dias úteis e taxas de conversão
- Exportação dos resultados em CSV, XLSX e PDF

## Integração com IA (Ollama)

- Insights e ações sugeridas gerados via modelo neural-chat (opcional)
- Configuração via variáveis de ambiente:
  - `OLLAMA_HOST`, `OLLAMA_PORT`, `OLLAMA_MODEL`

## Exportação de Resultados

- Botões para exportar tabelas e projeções em CSV, XLSX e PDF
- Utilização de `xlsxwriter` e `reportlab` para geração de arquivos

## Logs e Monitoramento

- Logs de eventos relevantes (login, upload, análise, exportação)
- Mensagens de erro amigáveis para o usuário

## Variáveis de Ambiente

- `.env` para configuração de integrações e parâmetros sensíveis

## Dicas para Manutenção

- Utilize tipagem forte e docstrings
- Separe lógica de interface e de negócio
- Mantenha dependências atualizadas
- Faça backup regular dos dados e usuários
- Teste autenticação, upload, análise, segmentação e exportação após alterações

Para detalhes de uso e exemplos, consulte os demais arquivos em `/docs`. 