# Roadmap do Projeto SaleSniper – Analytics SaaS com IA

Este roadmap apresenta o plano de evolução do SaleSniper, detalhando as etapas de validação, expansão e sugestões de novas funcionalidades avançadas. O texto é pensado para quem é da área de tecnologia, mas não é desenvolvedor, explicando conceitos e tecnologias de forma acessível.

---

## 1. Etapas de Evolução do Produto

### 1.1. Testes Internos (Período Fechado)
- **Objetivo:** Garantir estabilidade, usabilidade e performance do MVP.
- **Ações:**
  - Testes intensivos pela equipe interna.
  - Ajustes rápidos em bugs e melhorias de interface.
  - Validação dos fluxos principais: upload de dados, geração de insights, dashboards e exportação de resultados.
  - Teste do fluxo de autenticação e permissões de acesso.
- **Tecnologias:**
  - **Streamlit Cloud:** Plataforma para rodar o app na nuvem, facilitando acesso e compartilhamento.
  - **Hugging Face (Inference API):** Serviço de IA para geração de textos e insights, sem necessidade de rodar modelos pesados localmente.

### 1.2. Testes Internos com Dados Reais de Clientes e Beta Tester
- **Objetivo:** Validar o produto com dados reais, garantindo privacidade e consenso dos clientes.
- **Ações:**
  - Equipe interna utiliza dados reais de clientes (com consentimento) para testar o sistema em situações reais.
  - Ajustes baseados em problemas e oportunidades identificadas com dados reais.
  - Após validação interna, liberar para um cliente atuar como beta tester exclusivo.
  - Coleta de feedback detalhado desse cliente beta tester.
- **Explicação:**
  - **Testes Internos com Dados Reais:** Permite identificar problemas que só aparecem com dados do mundo real, sem expor o sistema a múltiplos clientes ainda.
  - **Beta Tester:** Um cliente parceiro testa o sistema antes da abertura para outros, permitindo ajustes finos.

### 1.3. Testes Ampliados (Early Adopters)
- **Objetivo:** Ampliar o uso para mais clientes, validando escalabilidade e robustez.
- **Ações:**
  - Liberação para um grupo maior de clientes interessados.
  - Suporte dedicado para dúvidas e problemas.
  - Coleta de métricas de uso e satisfação.
  - Início da documentação pública e treinamento de usuários.

### 1.4. Liberação Geral (Go Live)
- **Objetivo:** Disponibilizar o SaleSniper para o mercado.
- **Ações:**
  - Liberação para todos os clientes.
  - Suporte e monitoramento contínuo.
  - Início de campanhas de divulgação e onboarding.
  - Evolução contínua baseada em feedback e análise de uso.

---

## 2. Melhorias Funcionais e Novas Features Avançadas

### 2.1. Projeção de Churn (Previsão de Cancelamento)
- **Descrição:** Ferramenta que prevê quais clientes têm maior risco de sair, usando modelos matemáticos e IA.
- **Valor:** Ajuda equipes de vendas e sucesso a agir antes da perda do cliente.
- **Tecnologia:** Modelos de Machine Learning (ex: regressão, árvores de decisão, redes neurais).
- **Status Atual:**
  - Já em uso: Modelos de sobrevivência (Weibull), Random Forest, e métricas de avaliação como ROC-AUC e recall.
  - O sistema já realiza análise de churn com base em dados históricos dos clientes, utilizando essas técnicas para prever o risco de saída.

### 2.2. Detecção de Anomalias
- **Descrição:** Identifica comportamentos fora do padrão nos dados (ex: picos de cancelamento, vendas atípicas).
- **Valor:** Permite ação rápida em situações inesperadas.
- **Tecnologia:** Algoritmos de detecção de outliers e séries temporais.

### 2.3. Segmentação Automática de Clientes
- **Descrição:** Agrupa clientes automaticamente por perfil, comportamento ou potencial de receita.
- **Valor:** Facilita campanhas personalizadas e estratégias de retenção.
- **Tecnologia:** Algoritmos de clusterização (ex: K-means, DBSCAN).

### 2.4. Projeção de Receita e Cenários
- **Descrição:** Simula diferentes cenários de crescimento, churn e vendas futuras.
- **Valor:** Ajuda no planejamento estratégico e definição de metas.
- **Tecnologia:** Modelos estatísticos e simulações Monte Carlo.

### 2.5. Explicabilidade dos Modelos (Explainable AI)
- **Descrição:** Mostra de forma simples por que a IA tomou determinada decisão ou sugeriu uma ação.
- **Valor:** Aumenta a confiança dos usuários e facilita a adoção.
- **Tecnologia:** Ferramentas como SHAP, LIME.

### 2.6. Integração com CRMs e ERPs
- **Descrição:** Permite importar/exportar dados automaticamente de sistemas já usados pelos clientes.
- **Valor:** Reduz trabalho manual e aumenta a utilidade do SaleSniper.
- **Tecnologia:** APIs REST, conectores prontos.

### 2.7. Alertas Inteligentes e Notificações
- **Descrição:** Envia alertas automáticos sobre riscos, oportunidades ou anomalias detectadas.
- **Valor:** Proatividade para equipes de vendas e sucesso.
- **Tecnologia:** Regras de negócio e triggers baseados em IA.

---

## 3. Explicação de Tecnologias e Frameworks

- **Streamlit:** Framework Python para criar interfaces web de forma rápida, sem precisar ser especialista em front-end.
- **Hugging Face:** Plataforma de IA que oferece modelos prontos para uso, acessíveis via API.
- **Machine Learning:** Área da computação que cria "modelos" capazes de aprender padrões a partir de dados e fazer previsões.
- **APIs:** "Portas digitais" que permitem que diferentes sistemas conversem entre si.
- **Clusterização:** Técnica de agrupar dados semelhantes automaticamente.
- **Explainable AI:** Conjunto de métodos para explicar decisões de modelos de IA de forma compreensível.
- **Monte Carlo:** Método de simulação que usa sorteios aleatórios para prever cenários futuros.

---

## 4. Resumo Visual

O diagrama `roadmap.png` pode ser atualizado para refletir as novas etapas e features sugeridas.

---

Se quiser detalhar algum item, é só pedir! 