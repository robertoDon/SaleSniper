# Estrutura do Projeto

Abaixo está a organização das principais pastas e arquivos do projeto, com uma breve descrição de cada item relevante.

```
MVP/
├── scr/                # Código fonte principal (Streamlit)
│   ├── components/     # Componentes de interface (ICP, segmentação, metas)
│   ├── services/       # Serviços e regras de negócio
│   ├── data/           # Arquivos de dados e configurações
│   └── streamlit_app.py# Ponto de entrada da aplicação
│
├── core/               # Lógica central do sistema
│   └── sistema.py      # Núcleo de processamento e cálculos
│
├── domain/             # Entidades e regras de domínio
│   └── servicos/       # Serviços de domínio
│
├── adapters/           # Adaptadores para importação de dados
│   └── importador.py   # Importação de clientes via Excel
│
├── docs/               # Documentação detalhada
│   ├── GUIA_DESENVOLVEDOR.md
│   ├── DOCUMENTACAO_TECNICA.md
│   └── exemplo_dados.md
│
├── tests/              # Arquivos de teste e exemplos
│   └── clientes_teste.xlsx
│
├── diagrams/           # Diagramas do sistema
│
├── README.md           # Documentação principal
├── GUIA_RAPIDO.md      # Guia rápido para usuários
├── ESTRUTURA.md        # Este arquivo
├── requirements.txt    # Dependências do projeto
```

## Descrição dos Diretórios

- **scr/**: Código principal da aplicação, incluindo interface, serviços e dados.
- **core/**: Lógica central e cálculos do sistema.
- **domain/**: Entidades e regras de negócio específicas do domínio.
- **adapters/**: Importação e integração de dados externos.
- **docs/**: Documentação detalhada para usuários e desenvolvedores.
- **tests/**: Arquivos de teste e exemplos de dados.
- **diagrams/**: Diagramas ilustrativos do sistema.

Consulte cada arquivo de documentação para detalhes sobre uso e desenvolvimento. 