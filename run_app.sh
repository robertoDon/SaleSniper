#!/bin/bash

# Inicia o Ollama em background
(ollama serve > /dev/null 2>&1 &)

# Aguarda 3 segundos para o Ollama iniciar completamente
sleep 3

# Inicia a aplicação Streamlit usando o Python do usuário
python3 -m streamlit run scr/streamlit_app.py 