# Guia do Desenvolvedor

## Visão Geral

Este projeto é um dashboard Streamlit para análise de ICP, segmentação de clientes e projeções de funil, com autenticação, upload de dados, insights de IA e exportação de resultados.

## Preparação do Ambiente

1. Clone o repositório e acesse a pasta do projeto
2. Crie e ative o ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```
3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```
4. (Opcional) Configure o Ollama para insights de IA:
   - Instale o Ollama: https://ollama.ai
   - Baixe o modelo neural-chat:
     ```bash
     ollama pull neural-chat
     ```
5. Execute o sistema:
   ```bash
   streamlit run scr/streamlit_app.py
   ```

## Estrutura dos Principais Módulos

- `scr/streamlit_app.py`: Ponto de entrada, autenticação, navegação e controle de sessão
- `scr/components/`: Componentes de interface (ICP, segmentação, metas)
- `scr/services/`: Serviços de autenticação, IA, regras de negócio
- `core/`: Lógica central e cálculos
- `adapters/`: Importação de dados (Excel)
- `tests/`: Arquivos de teste e exemplos

## Fluxo de Desenvolvimento

1. Crie uma branch para sua feature ou correção
2. Implemente as mudanças seguindo boas práticas (PEP8, tipagem, docstrings)
3. Teste localmente
4. Atualize a documentação se necessário
5. Faça o pull request para revisão

## Boas Práticas

- Use tipagem forte e docstrings em funções
- Separe lógica de interface e de negócio
- Utilize cache do Streamlit para otimizar performance
- Mantenha dados sensíveis fora do código (use `.env`)
- Faça commits pequenos e descritivos

## Testes

- Utilize os arquivos de exemplo em `/tests` para validar funcionalidades
- Teste autenticação, upload, análise ICP, segmentação e exportação

## Contribuição

- Siga o fluxo de branch: `feature/nome`, `fix/nome`
- Descreva claramente suas mudanças no PR
- Respeite o padrão de código e documentação

Dúvidas? Consulte os arquivos em `/docs` ou entre em contato com a equipe técnica. 