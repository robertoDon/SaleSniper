# Guia Rápido do Usuário

## Requisitos
- Windows 10/11 ou macOS 10.15+
- Python 3.10 ou superior
- Navegador atualizado

## Instalação e Início Rápido

1. **Baixe o projeto**
   - Receba o link do projeto ou arquivo ZIP
   - Extraia para uma pasta de sua preferência
2. **Crie e ative o ambiente virtual**
   ```bash
   python -m venv venv
   source venv/bin/activate  # ou venv\Scripts\activate no Windows
   ```
3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
4. **(Opcional) Configure IA**
   - Instale o Ollama e baixe o modelo neural-chat, se desejar usar insights de IA
5. **Inicie o sistema**
   ```bash
   streamlit run scr/streamlit_app.py
   ```
6. **Acesse o sistema**
   - O navegador abrirá automaticamente em http://localhost:8501

## Login
- Use o usuário e senha fornecidos pela equipe
- Apenas administradores podem criar novos usuários

## Upload de Dados
- Na aba "Análise de ICP", faça upload do arquivo Excel de clientes
- Utilize o arquivo de exemplo disponível em `/tests/clientes_teste.xlsx` para testar

## Navegação
- **Análise de ICP:** Perfil ideal, insights e ações sugeridas
- **Segmentação:** Divida clientes por valor ou quantidade
- **Metas & Projeções:** Calcule metas e exporte resultados

## Dicas de Segurança
- Não compartilhe seu usuário e senha
- Mantenha o arquivo `usuarios.json` seguro
- Faça backup regular dos dados

## Problemas Comuns
- **Erro de autenticação:** Verifique usuário e senha
- **Erro ao subir arquivo:** Use o modelo de exemplo e confira o formato
- **Sistema não abre:** Confirme se o Python está instalado e o ambiente virtual ativado

Em caso de dúvidas, consulte a equipe de suporte ou a documentação detalhada em `/docs`.