# Dashboard Cliente Ideal

Dashboard interativo para análise do Perfil de Cliente Ideal (ICP), segmentação de clientes e projeções de funil de vendas, com autenticação e insights de IA.

## 🚀 Instalação e Execução

1. **Clone o repositório:**
   ```bash
   git clone [URL_DO_REPOSITORIO]
   cd [NOME_DO_DIRETORIO]
   ```
2. **Crie e ative o ambiente virtual:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```
3. **Instale as dependências:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Configure o Ollama para IA (opcional):**
   - Instale o Ollama: https://ollama.ai
   - Baixe o modelo neural-chat:
     ```bash
     ollama pull neural-chat
     ```
5. **Execute o aplicativo:**
   ```bash
   streamlit run scr/streamlit_app.py
   ```

## 🧑‍💻 Como Usar

1. Faça login com seu usuário e senha.
2. Na aba "Análise de ICP", faça upload do arquivo Excel de clientes.
3. Navegue pelas abas para acessar:
   - Análise de ICP (perfil ideal, insights e ações sugeridas)
   - Segmentação de clientes (por valor ou quantidade)
   - Metas & Projeções (funil de vendas, metas, exportação de resultados)
4. Exporte resultados em CSV, XLSX ou PDF.

## 📊 Funcionalidades

- **Autenticação de usuários** (admin pode gerenciar usuários)
- **Upload de dados de clientes via Excel**
- **Análise automática do perfil de cliente ideal (ICP)**
- **Geração de insights e ações sugeridas com IA**
- **Segmentação customizável de clientes**
- **Projeção de metas e funil de vendas**
- **Exportação de resultados (CSV, XLSX, PDF)**
- **Interface responsiva e intuitiva**

## ⚙️ Requisitos

- Python 3.10+
- Streamlit
- Pandas, Numpy, Scipy, Openpyxl
- Ollama (opcional, para insights de IA)

## 📁 Estrutura Básica

- `scr/` — Código fonte principal
- `core/` — Lógica central do sistema
- `domain/` — Entidades e regras de negócio
- `adapters/` — Importação de dados
- `docs/` — Documentação detalhada
- `tests/` — Arquivos de teste

## 📝 Suporte

Dúvidas ou problemas? Entre em contato com a equipe de TI ou consulte a documentação na pasta `docs/`.