# streamlit_dashbord
A streamlit dashboard from a CSV file

# 🍎 Dashboard Nutricional

Uma aplicação Streamlit completa para análise de dados nutricionais de pacientes, com visualizações interativas e geração de relatórios em PDF.

## 📋 Funcionalidades

-   ✅ **Dashboard Interativo**: Visualizações dinâmicas dos dados nutricionais
-   ✅ **Análise Antropométrica**: Peso, altura, IMC, composição corporal
-   ✅ **Exames Bioquímicos**: Comparação com valores de referência
-   ✅ **Avaliação MNA**: Mini Avaliação Nutricional para idosos
-   ✅ **Prescrição Dietética**: Metas vs consumo atual
-   ✅ **Relatórios PDF**: Geração automática de relatórios completos

## 🚀 Instalação

### 1. Clone ou baixe os arquivos

```bash
# Baixe os arquivos:
# - dashboard_nutricional.py
# - requirements.txt
```

### 2. Crie um ambiente virtual (recomendado)

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar no Windows
.venv\Scripts\activate

# Ativar no Linux/Mac
source .venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

## 🏃‍♂️ Como Executar

### 1. Execute a aplicação

```bash
streamlit run dashboard_nutricional.py
```

### 2. Acesse no navegador

-   A aplicação abrirá automaticamente em: `http://localhost:8501`
-   Ou acesse manualmente o endereço mostrado no terminal

## 📊 Como Usar

### 1. **Carregar Dados**

-   Use o sidebar para fazer upload do arquivo CSV
-   O arquivo deve seguir o formato do exemplo fornecido

### 2. **Explorar Dados**

-   **Antropometria**: Visualize dados corporais e composição
-   **Exames**: Compare resultados bioquímicos com referências
-   **Avaliação MNA**: Análise nutricional específica para idosos
-   **Nutrição**: Compare prescrição com consumo atual

### 3. **Gerar Relatório**

-   Clique em "Gerar Relatório PDF"
-   Baixe o arquivo gerado automaticamente

## 📁 Formato do Arquivo CSV

O arquivo CSV deve conter as seguintes seções:

-   ADOS DO PACIENTE (dados pessoais)
-   ANAMNESE (histórico médico)
-   ANTROPOMETRIA (medidas corporais)
-   AVALIAÇÃO MNA (avaliação nutricional)
-   EXAMES BIOQUÍMICOS (resultados laboratoriais)
-   PRESCRIÇÃO DIETÉTICA (plano nutricional)
-   HISTÓRICO ALIMENTAR (consumo atual)

## 🛠️ Estrutura do Projeto

```
dashboard-nutricional/
│
├── dashboard_nutricional.py    # Aplicação principal
├── requirements.txt           # Dependências
├── README.md                 # Este arquivo
└── exemplo_dados.csv         # Arquivo de exemplo (opcional)
```

## 🔧 Solução de Problemas

### Erro de instalação

```bash
# Atualize o pip primeiro
python -m pip install --upgrade pip

# Instale novamente
pip install -r requirements.txt
```

### Erro de porta ocupada

```bash
# Use uma porta diferente
streamlit run dashboard_nutricional.py --server.port 8502
```

### Problemas com PDF

-   Certifique-se de que o reportlab está instalado corretamente
-   Em sistemas Linux, pode ser necessário instalar: `sudo apt-get install python3-dev`

## 📈 Métricas Analisadas

### Antropometria

-   IMC e classificação
-   Composição corporal
-   Circunferências corporais
-   Dobras cutâneas

### Bioquímica

-   Glicose, colesterol, lipídios
-   Proteínas (albumina, hemoglobina)
-   Vitaminas e minerais
-   Marcadores nutricionais

### MNA (Mini Nutritional Assessment)

-   Score total e classificação
-   Análise por domínios
-   Gráfico radar interativo

## 🎨 Personalização

### Cores e Tema

-   Modifique as cores no CSS customizado na seção `st.markdown`
-   Altere os templates dos gráficos Plotly

### Novos Gráficos

-   Adicione novos métodos na classe `NutritionDashboard`
-   Inclua novas abas no layout principal

### Relatório PDF

-   Customize o layout no método `generate_pdf_report`
-   Adicione novos elementos usando ReportLab

## 📞 Suporte

Para problemas ou dúvidas:

1. Verifique se todas as dependências estão instaladas
2. Confirme que o arquivo CSV está no formato correto
3. Consulte os logs de erro no terminal

## 📄 Licença

Este projeto é fornecido como exemplo educacional. Adapte conforme suas necessidades específicas.
