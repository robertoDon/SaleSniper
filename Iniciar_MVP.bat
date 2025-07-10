@echo off
echo Iniciando o MVP...
echo Por favor, aguarde...

:: Obtém o diretório do script
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

:: Verifica se o ambiente virtual existe e está configurado corretamente
if not exist venv\Scripts\activate.bat (
    echo Criando ambiente virtual...
    python -m venv venv
    
    :: Ativa o ambiente virtual
    call venv\Scripts\activate
    
    :: Atualiza o pip
    python -m pip install --upgrade pip
    
    :: Instala as dependências
    echo Instalando dependencias...
    pip install "streamlit>=1.32.0" -r requirements.txt
) else (
    :: Apenas ativa o ambiente virtual existente
    call venv\Scripts\activate
    
    :: Verifica se o Streamlit precisa ser atualizado
    pip show streamlit | findstr "Version: 1.32.0" >nul
    if errorlevel 1 (
        echo Atualizando Streamlit...
        pip install --upgrade "streamlit>=1.32.0"
    )
)

:: Define o PYTHONPATH para o diretório do projeto
set PYTHONPATH=%SCRIPT_DIR%

:: Inicia o aplicativo Streamlit
streamlit run scr/streamlit_app.py

pause 