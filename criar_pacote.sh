#!/bin/bash

echo "Criando pacote do MVP..."

# Nome do arquivo ZIP
NOME_PACOTE="MVP.zip"

# Remove o arquivo ZIP se já existir
if [ -f "$NOME_PACOTE" ]; then
    rm "$NOME_PACOTE"
fi

# Lista de arquivos e diretórios para incluir
echo "Adicionando arquivos ao pacote..."

# Adiciona todos os arquivos do projeto
zip -r "$NOME_PACOTE" . \
    -x "*.git*" \
    -x "*.DS_Store" \
    -x "criar_pacote.sh" \
    -x "$NOME_PACOTE"

echo "Pacote criado com sucesso: $NOME_PACOTE"
echo "Tamanho do pacote: $(du -h "$NOME_PACOTE" | cut -f1)" 