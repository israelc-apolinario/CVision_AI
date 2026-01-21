# CVision AI

Análise profissional de currículos usando Google Gemini API.

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.29+-red.svg)](https://streamlit.io)

## Features

- Resume analysis with seniority detection
- Technical and behavioral gap identification
- Career progression prediction
- Personalized development roadmap
- Multi-model fallback system

## Tech Stack

- Python 3.11
- Streamlit
- Google Gemini 2.5
- Plotly
- PyPDF2

## Installation

```bash
git clone https://github.com/yourusername/cvision-ai.git
cd cvision-ai

python -m venv .venv
.venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
```

Configure `.env`:
```env
GOOGLE_API_KEY=your-api-key-here
GEMINI_MODEL=gemini-2.5-flash
```

Get API key at [Google AI Studio](https://makersuite.google.com/app/apikey)

## Usage

### Start Application

```bash
python -m streamlit run app.py
```

Access at `http://localhost:8501`

Programmatic use:
```python
from career_agent import CareerIntelligenceAgent

agent = CareerIntelligenceAgent()
analysis = agent.analyze_resume(resume_text)
report = agent.generate_report(analysis)
```

## Structure

```
cvision-ai/
├── app.py
├── career_agent.py
├── requirements.txt
├── .env.example
└── README.md
```

## License

MIT License
