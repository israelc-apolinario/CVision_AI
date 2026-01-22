# CVision - Career Intelligence Platform

> Plataforma profissional de análise de carreira com inteligência artificial, especializada em identificação de competências, análise de senioridade e planejamento estratégico de desenvolvimento profissional.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)
[![Google Gemini](https://img.shields.io/badge/Gemini-2.5-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Funcionalidades

### Análise Inteligente
- **Detecção Automática de Senioridade**: Classificação precisa baseada em experiência e responsabilidades
- **Identificação de Lacunas**: Análise técnica e comportamental com recomendações práticas
- **Projeção de Carreira**: Próximo cargo provável com requisitos e probabilidade de transição
- **Visualização Interativa**: Gráficos radar de skills e evolução de senioridade

### Roadmap Personalizado
- **Consultoria Executiva**: Análise estratégica de viabilidade de objetivos de carreira
- **Planejamento Estruturado**: Etapas detalhadas com ações, recursos e indicadores de sucesso
- **Cargos Intermediários**: Sugestões de posições de transição quando necessário
- **Investimento Estimado**: Projeção de custos com cursos, certificações e desenvolvimento

### Sistema Robusto
- **Multi-Model Fallback**: Sistema automático de fallback entre modelos Gemini
- **Processamento PDF**: Upload e extração automática de texto
- **Interface Moderna**: Design profissional dark-mode com métricas visuais
- **Logging Detalhado**: Sistema completo de logs para debugging e monitoramento

## 🛠️ Stack Tecnológico

- **Backend**: Python 3.11+
- **Frontend**: Streamlit (Framework web interativo)
- **IA**: Google Gemini 2.5 (Flash & Pro)
- **Visualização**: Plotly (Gráficos interativos)
- **Processamento**: PyPDF2 (Extração de documentos)

## 📦 Instalação

### Pré-requisitos
- Python 3.11 ou superior
- Chave de API do Google Gemini ([Obtenha aqui](https://makersuite.google.com/app/apikey))

### Setup

```bash
# Clone o repositório
git clone https://github.com/yourusername/cvision-career-intelligence.git
cd cvision-career-intelligence

# Crie ambiente virtual
python -m venv .venv

# Ative o ambiente virtual
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua GOOGLE_API_KEY
```

### Configuração `.env`

```env
GOOGLE_API_KEY=sua-chave-api-aqui
GEMINI_MODEL=gemini-2.5-flash
```

## 🚀 Uso

### Interface Web

```bash
python -m streamlit run app.py
```

Acesse: `http://localhost:8501`

### Uso Programático

```python
from career_agent import CareerIntelligenceAgent

# Inicialize o agente
agent = CareerIntelligenceAgent()

# Analise um currículo
analysis = agent.analyze_resume(resume_text)

# Gere relatório formatado
report = agent.generate_report(analysis)
print(report)

# Ou acesse componentes específicos
seniority = agent.classify_seniority(resume_text)
gaps = agent.detect_gaps(resume_text)
next_role = agent.project_next_role(resume_text)
```

## 📁 Estrutura do Projeto

```
cvision-career-intelligence/
├── app.py                 # Interface Streamlit
├── career_agent.py        # Motor de análise principal
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── .gitignore            # Arquivos ignorados pelo Git
└── README.md             # Documentação
```

## 🎯 Casos de Uso

- **Profissionais**: Avaliar nível atual e planejar próximos passos na carreira
- **Recrutadores**: Análise rápida de perfil e fit para posições
- **Consultores de Carreira**: Ferramenta de apoio para consultoria profissional
- **Empresas**: Avaliação de necessidades de desenvolvimento de equipes

## 🔒 Segurança

- Chaves de API armazenadas em variáveis de ambiente
- `.gitignore` configurado para proteger credenciais
- Validação de entrada para prevenir injeção de código
- Sanitização de dados sensíveis nos logs

## 🤝 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para:

1. Fazer fork do projeto
2. Criar branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para o branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licença

MIT License - veja [LICENSE](LICENSE) para detalhes.

## 📧 Contato

Para dúvidas, sugestões ou colaborações, abra uma issue no repositório.

---

**Desenvolvido com** 🚀 **para transformar carreiras através da tecnologia**
