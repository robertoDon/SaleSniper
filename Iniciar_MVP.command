#!/bin/bash
echo "Iniciando o MVP..."
echo "Por favor, aguarde..."

# Obtém o diretório do script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Verifica se o ambiente virtual existe e está configurado corretamente
if [ ! -d "venv" ] || [ ! -f "venv/bin/activate" ]; then
    echo "Criando ambiente virtual..."
    python3 -m venv venv
    
    # Ativa o ambiente virtual
    source venv/bin/activate
    
    # Atualiza o pip
    pip install --upgrade pip
    
    # Instala as dependências
    echo "Instalando dependências..."
    pip install "streamlit>=1.32.0" -r requirements.txt
else
    # Apenas ativa o ambiente virtual existente
    source venv/bin/activate
    
    # Verifica se o Streamlit precisa ser atualizado
    if ! pip show streamlit | grep -q "Version: 1.32.0"; then
        echo "Atualizando Streamlit..."
        pip install --upgrade "streamlit>=1.32.0"
    fi
fi

# Define o PYTHONPATH para o diretório do projeto
export PYTHONPATH="$SCRIPT_DIR"

# Inicia o aplicativo Streamlit
streamlit run scr/streamlit_app.py 