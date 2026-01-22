import streamlit as st
import os
from dotenv import load_dotenv
from career_agent import CareerIntelligenceAgent
import PyPDF2
import json
import logging
import plotly.graph_objects as go
from datetime import datetime, timedelta
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
load_dotenv()

st.set_page_config(
    page_title="CVision AI | Análise de Currículos",
    page_icon="👁️",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None
if "curriculo_text" not in st.session_state:
    st.session_state.curriculo_text = None
if "career_goal" not in st.session_state:
    st.session_state.career_goal = None
if "roadmap" not in st.session_state:
    st.session_state.roadmap = None

# CSS
st.markdown("""
<style>
    .main {
        background: #0d1117;
    }
    .stApp {
        background: #0d1117;
    }
    h1, h2, h3 {
        color: #c9d1d9 !important;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .metric-card {
        background: #161b22;
        border-left: 3px solid #58a6ff;
        border-radius: 6px;
        padding: 24px;
        margin: 12px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.4);
    }
    .stat-value {
        font-size: 36px;
        font-weight: 700;
        color: #58a6ff;
    }
    .stat-label {
        font-size: 12px;
        color: #8b949e;
        text-transform: uppercase;
        letter-spacing: 1.2px;
    }
    .stButton>button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%);
        color: white;
        border: none;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #2ea043 0%, #3fb950 100%);
        box-shadow: 0 0 10px rgba(46,160,67,0.4);
    }
    [data-testid="stSidebar"] {
        background: #161b22;
        border-right: 1px solid #30363d;
    }
</style>
""", unsafe_allow_html=True)

def create_skills_radar(lacunas_tecnicas):
    if not lacunas_tecnicas:
        return None
    
    skills = [l.get('skill', 'N/A') for l in lacunas_tecnicas[:8]]
    importance_map = {'alta': 3, 'média': 2, 'baixa': 1}
    values = [importance_map.get(l.get('importancia', 'média'), 2) for l in lacunas_tecnicas[:8]]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=skills,
        fill='toself',
        fillcolor='rgba(0, 212, 255, 0.3)',
        line=dict(color='#00d4ff', width=2)
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 3], showticklabels=False),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa', family='monospace'),
        height=500,
        title=dict(text="Top Skills Identificadas", font=dict(color='#00d4ff', size=16))
    )
    
    return fig

def create_senioridade_bar(nivel, anos):
    niveis = ['Júnior', 'Pleno', 'Sênior', 'Especialista']
    if nivel not in niveis:
        nivel_idx = 1
    else:
        nivel_idx = niveis.index(nivel)
    
    colors = ['#555555' if i != nivel_idx else '#00d4ff' for i in range(len(niveis))]
    
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=niveis,
        y=[25, 50, 75, 100],
        marker=dict(color=colors, line=dict(color='#00d4ff', width=2)),
        text=[f"{anos} anos" if i == nivel_idx else "" for i in range(len(niveis))],
        textposition='outside',
        textfont=dict(color='#00d4ff', size=14)
    ))
    
    fig.update_layout(
        xaxis=dict(title="", color='#fafafa'),
        yaxis=dict(title="Maturidade Profissional (%)", color='#fafafa', range=[0, 110]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#fafafa', family='monospace'),
        height=400,
        title=dict(text="Nível de Senioridade", font=dict(color='#00d4ff', size=16))
    )
    
    return fig

def generate_career_roadmap(curriculo, career_goal, api_key):
    try:
        agent = CareerIntelligenceAgent(api_key=api_key)
        logger.info(f"Gerando roadmap para objetivo: {career_goal}")
        
        prompt = f"""Você é um consultor executivo de carreira altamente experiente, especializado em transições profissionais estratégicas e desenvolvimento de liderança.

ANÁLISE SOLICITADA:
Avalie a viabilidade de transição do perfil profissional abaixo para o objetivo de carreira definido. Crie um roadmap estratégico, realista e acionável.

CURRÍCULO DO PROFISSIONAL:
{curriculo[:3000]}

OBJETIVO DE CARREIRA DESEJADO: {career_goal}

DIRETRIZES PARA ANÁLISE PROFISSIONAL:
1. Seja honesto sobre a viabilidade do objetivo considerando o perfil atual
2. Defina prazos realistas baseados em transições de mercado
3. Priorize ações de alto impacto que acelerem a transição
4. Sugira certificações e cursos reconhecidos pelo mercado
5. Inclua desenvolvimento de soft skills críticas para o cargo alvo
6. Considere networking estratégico e visibilidade profissional
7. Identifique possíveis cargos intermediários se necessário

Retorne APENAS JSON válido (sem markdown, sem comentários):
{{
    "objetivo_viavel": true,
    "prazo_estimado": "18-24 meses",
    "nivel_desafio": "médio",
    "etapas": [
        {{
            "ordem": 1,
            "titulo": "Fundação Técnica e Posicionamento",
            "prazo": "4-6 meses",
            "acoes": [
                "Completar certificação X reconhecida no mercado",
                "Desenvolver projeto demonstrativo em Y",
                "Iniciar networking estratégico com profissionais da área"
            ],
            "skills_desenvolver": [
                "Skill técnica específica 1",
                "Skill técnica específica 2", 
                "Soft skill relevante"
            ],
            "recursos": [
                "Certificação profissional reconhecida (ex: AWS, Azure, PMP)",
                "Curso estruturado de plataforma respeitada",
                "Comunidade ou grupo profissional específico"
            ],
            "indicadores_sucesso": [
                "Certificação obtida",
                "Portfolio com 3+ projetos relevantes",
                "Rede de 50+ conexões estratégicas"
            ]
        }}
    ],
    "cargos_intermediarios": ["Cargo de transição 1", "Cargo de transição 2"],
    "investimento_estimado": "R$ X.XXX - investimento em cursos, certificações e networking",
    "probabilidade_sucesso": "alta",
    "fatores_criticos": [
        "Dedicação de X horas semanais para desenvolvimento",
        "Investimento em certificações chave",
        "Networking ativo e consistente"
    ],
    "observacoes": "Análise estratégica considerando tendências de mercado, demanda por perfil e competitividade. Inclua insights sobre o momento ideal para transição e possíveis desafios."
}}"""

        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 4096
            }
        }
        
        headers = {"Content-Type": "application/json"}
        import requests
        
        logger.info("Fazendo requisição para API do Gemini...")
        response = requests.post(
            f"{agent.api_url}?key={api_key}",
            headers=headers,
            json=payload,
            timeout=120
        )
        
        if response.status_code == 429:
            logger.warning("Rate limit atingido, tentando modelos alternativos...")
            fallback_models = ["gemini-1.5-flash-latest", "gemini-pro"]
            for model in fallback_models:
                try:
                    fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                    logger.info(f"Tentando modelo: {model}")
                    response = requests.post(
                        f"{fallback_url}?key={api_key}",
                        headers=headers,
                        json=payload,
                        timeout=120
                    )
                    if response.status_code == 200:
                        logger.info(f"Sucesso com modelo: {model}")
                        break
                except Exception as fallback_error:
                    logger.error(f"Erro no modelo {model}: {fallback_error}")
                    continue
        
        if response.status_code == 200:
            result = response.json()
            logger.info("Resposta recebida com sucesso")
            
            text = result['candidates'][0]['content']['parts'][0]['text']
            logger.info(f"Texto recebido (primeiros 200 chars): {text[:200]}")
            
            # Limpar markdown se houver
            text = text.strip()
            if text.startswith('```'):
                lines = text.split('\n')
                text = '\n'.join(lines[1:-1]) if len(lines) > 2 else text
            text = text.replace('```json', '').replace('```', '').strip()
            
            try:
                roadmap_data = json.loads(text)
                logger.info("JSON parseado com sucesso")
                return roadmap_data
            except json.JSONDecodeError as json_error:
                logger.error(f"Erro ao decodificar JSON do roadmap: {json_error}")
                logger.error(f"Texto que causou erro: {text[:500]}")
                st.error(f"❌ Erro ao processar resposta da API. JSON inválido.")
                return None
        else:
            error_msg = f"Erro na API ao gerar roadmap: {response.status_code}"
            if response.text:
                error_msg += f" - {response.text[:200]}"
            logger.error(error_msg)
            st.error(f"❌ Erro na API: Status {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Erro ao gerar roadmap: {type(e).__name__} - {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        st.error(f"❌ Erro: {str(e)}")
        return None

st.markdown("""
<div style='text-align: center; padding: 30px 0; border-bottom: 1px solid #30363d;'>
    <h1 style='font-size: 42px; margin: 0; color: #58a6ff; letter-spacing: 2px;'>CVision AI</h1>
    <p style='color: #8b949e; font-size: 14px; margin: 10px 0; letter-spacing: 1px;'>Análise Inteligente de Currículos</p>
</div>
""", unsafe_allow_html=True)

st.markdown("---")

with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    
    st.markdown("---")
    
    if st.button("🔌 Verificar Conexão", width="stretch"):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("❌ API key não encontrada")
        else:
            try:
                with st.spinner("Testando..."):
                    agent = CareerIntelligenceAgent(api_key=api_key)
                    st.success("✅ Conectado ao Gemini")
            except Exception as e:
                st.error(f"❌ Erro: {str(e)[:50]}")
    
    # Marca d'água no final da sidebar
    st.markdown("""
    <div style='position: fixed; bottom: 20px; left: 20px; width: 240px; opacity: 0.4; transition: opacity 0.3s;'>
        <div style='text-align: center; padding: 8px 0; border-top: 1px solid #30363d;'>
            <div style='font-family: "Courier New", monospace; color: #6e7681; font-size: 9px; margin-top: 8px;'>v1.0.0 • Build 2026.01.20</div>
            <div style='font-family: "Courier New", monospace; color: #484f58; font-size: 8px; margin-top: 2px;'>Powered by Gemini 2.5</div>
            <div style='color: #3fb950; font-size: 10px; margin-top: 6px;'>● ONLINE</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if st.session_state.analysis_data is None:
    
    # Feature cards antes do upload
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div style='background: #161b22; padding: 24px; border-radius: 8px; border: 1px solid #30363d; text-align: center; transition: all 0.3s;'>
            <div style='font-family: "Courier New", monospace; font-size: 36px; margin-bottom: 12px; color: #58a6ff;'>{ }</div>
            <div style='color: #58a6ff; font-weight: 600; margin-bottom: 8px; font-family: monospace;'>parse()</div>
            <div style='color: #8b949e; font-size: 12px; font-family: monospace;'>// intelligent analysis</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: #161b22; padding: 24px; border-radius: 8px; border: 1px solid #30363d; text-align: center; transition: all 0.3s;'>
            <div style='font-family: "Courier New", monospace; font-size: 36px; margin-bottom: 12px; color: #f85149;'>!</div>
            <div style='color: #58a6ff; font-weight: 600; margin-bottom: 8px; font-family: monospace;'>detect()</div>
            <div style='color: #8b949e; font-size: 12px; font-family: monospace;'>// gaps & missing skills</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style='background: #161b22; padding: 24px; border-radius: 8px; border: 1px solid #30363d; text-align: center; transition: all 0.3s;'>
            <div style='font-family: "Courier New", monospace; font-size: 36px; margin-bottom: 12px; color: #3fb950;'>↑</div>
            <div style='color: #58a6ff; font-weight: 600; margin-bottom: 8px; font-family: monospace;'>upgrade()</div>
            <div style='color: #8b949e; font-size: 12px; font-family: monospace;'>// level up path</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div style='background: #161b22; padding: 24px; border-radius: 8px; border: 1px solid #30363d; text-align: center; transition: all 0.3s;'>
            <div style='font-family: "Courier New", monospace; font-size: 36px; margin-bottom: 12px; color: #a371f7;'>→</div>
            <div style='color: #58a6ff; font-weight: 600; margin-bottom: 8px; font-family: monospace;'>map()</div>
            <div style='color: #8b949e; font-size: 12px; font-family: monospace;'>// personalized roadmap</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown("## 📤 Upload do Currículo")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        uploaded_file = st.file_uploader(
            "Arraste ou selecione seu arquivo",
            type=['pdf', 'txt'],
            help="Formatos aceitos: PDF ou TXT"
        )
        
        if uploaded_file:
            resume_text = None
            
            try:
                if uploaded_file.type == "application/pdf":
                    with st.spinner("📄 Processando PDF..."):
                        pdf_reader = PyPDF2.PdfReader(uploaded_file)
                        resume_text = ""
                        for page in pdf_reader.pages:
                            text = page.extract_text()
                            if text:
                                resume_text += text + "\n"
                        
                        if not resume_text.strip():
                            st.error("❌ Não foi possível extrair texto do PDF")
                            st.stop()
                else:
                    resume_text = uploaded_file.read().decode('utf-8')
                
                if resume_text and len(resume_text.strip()) > 50:
                    api_key = os.getenv('GOOGLE_API_KEY')
                    
                    if not api_key:
                        st.error("❌ API key não configurada no arquivo .env")
                        st.stop()
                    
                    with st.spinner("🔍 Analisando seu currículo..."):
                        try:
                            agent = CareerIntelligenceAgent(api_key=api_key)
                            analysis = agent.analyze_resume(resume_text)
                            
                            st.session_state.analysis_data = analysis
                            st.session_state.curriculo_text = resume_text
                            st.success("✅ Análise concluída!")
                            st.rerun()
                            
                        except Exception as e:
                            st.error(f"❌ Erro na análise: {str(e)}")
                            logger.error(f"Erro: {e}", exc_info=True)
                else:
                    st.warning("⚠️ Arquivo muito curto ou vazio")
                    
            except Exception as e:
                st.error(f"❌ Erro ao processar arquivo: {str(e)}")
                logger.error(f"Erro: {e}", exc_info=True)

else:
    analysis = st.session_state.analysis_data
    prof = analysis.get('profissao_real', {})
    sen = analysis.get('nivel_senioridade', {})
    lac = analysis.get('lacunas', {})
    prox = analysis.get('proximo_cargo', {})
    plano = analysis.get('plano_crescimento', {})
    
    st.markdown("## 📊 Dashboard de Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-label'>Profissão Identificada</div>
            <div class='stat-value' style='font-size: 24px;'>{prof.get('titulo', 'N/A')}</div>
            <div style='color: #8b92a7; margin-top: 8px;'>Confiança: {prof.get('nivel_confianca', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-label'>Senioridade</div>
            <div class='stat-value'>{sen.get('nivel', 'N/A')}</div>
            <div style='color: #8b92a7; margin-top: 8px;'>{sen.get('anos_experiencia', 0)} anos</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        lacunas_count = len(lac.get('tecnicas', [])) + len(lac.get('comportamentais', []))
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-label'>Áreas de Melhoria</div>
            <div class='stat-value'>{lacunas_count}</div>
            <div style='color: #8b92a7; margin-top: 8px;'>Identificadas</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class='metric-card'>
            <div class='stat-label'>Projeção Natural</div>
            <div class='stat-value' style='font-size: 20px;'>{prox.get('cargo', 'N/A')}</div>
            <div style='color: #8b92a7; margin-top: 8px;'>Em {prox.get('prazo_estimado', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col_graph1, col_graph2 = st.columns(2)
    
    with col_graph1:
        lacunas_tec = lac.get('tecnicas', [])
        if lacunas_tec:
            fig_skills = create_skills_radar(lacunas_tec)
            if fig_skills:
                st.plotly_chart(fig_skills, use_container_width=True)
    
    with col_graph2:
        nivel = sen.get('nivel', 'Pleno')
        anos = sen.get('anos_experiencia', 0)
        fig_sen = create_senioridade_bar(nivel, anos)
        if fig_sen:
            st.plotly_chart(fig_sen, use_container_width=True)
    
    st.markdown("---")
    st.markdown("## 🎯 Defina seu Objetivo de Carreira")
    
    if st.session_state.career_goal is None:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("""
            <div style='text-align: center; padding: 20px; background: rgba(0, 212, 255, 0.05); border-radius: 10px; border: 1px solid #00d4ff;'>
                <p style='color: #8b92a7; margin-bottom: 15px;'>Para onde você quer ir na sua carreira?</p>
            </div>
            """, unsafe_allow_html=True)
            
            career_input = st.text_input(
                "Digite o cargo ou área que deseja alcançar:",
                placeholder="Ex: Gerente de Projetos, Arquiteto de Software, Diretor de TI...",
                label_visibility="collapsed"
            )
            
            if st.button("🚀 Gerar Roadmap Personalizado", use_container_width=True, type="primary"):
                if career_input:
                    st.session_state.career_goal = career_input
                    st.rerun()
                else:
                    st.warning("⚠️ Digite um objetivo de carreira")
    else:
        st.markdown(f"### 🎯 Objetivo: **{st.session_state.career_goal}**")
        
        if st.session_state.roadmap is None:
            with st.spinner("🔮 Gerando seu roadmap personalizado..."):
                api_key = os.getenv('GOOGLE_API_KEY')
                roadmap = generate_career_roadmap(
                    st.session_state.curriculo_text,
                    st.session_state.career_goal,
                    api_key
                )
                
                if roadmap:
                    st.session_state.roadmap = roadmap
                    st.rerun()
                else:
                    st.error("❌ Erro ao gerar roadmap. Tente novamente ou mude o objetivo.")
                    if st.button("🔄 Tentar Novamente"):
                        st.rerun()
                    if st.button("⬅️ Voltar"):
                        st.session_state.career_goal = None
                        st.rerun()
        else:
            roadmap = st.session_state.roadmap
            
            # Métricas principais
            col1, col2, col3 = st.columns(3)
            
            with col1:
                viavel = roadmap.get('objetivo_viavel', True)
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='stat-label'>Viabilidade</div>
                    <div class='stat-value' style='font-size: 24px;'>{'✓ VIÁVEL' if viavel else '⚠ DESAFIADOR'}</div>
                    <div style='color: #8b92a7; margin-top: 8px;'>{roadmap.get('prazo_estimado', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                prob = roadmap.get('probabilidade_sucesso', 'média')
                prob_percent = {'alta': '75-90%', 'média': '50-70%', 'baixa': '20-40%'}
                color = '#00ffaa' if prob == 'alta' else '#ffaa00' if prob == 'média' else '#ff6b6b'
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='stat-label'>Probabilidade de Sucesso</div>
                    <div class='stat-value' style='font-size: 24px; color: {color};'>{prob.upper()}</div>
                    <div style='color: #8b92a7; margin-top: 8px;'>{prob_percent.get(prob, 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                nivel = roadmap.get('nivel_desafio', 'médio')
                nivel_color = '#ffaa00' if nivel == 'médio' else '#ff6b6b' if nivel == 'alto' else '#00ffaa'
                st.markdown(f"""
                <div class='metric-card'>
                    <div class='stat-label'>Nível de Desafio</div>
                    <div class='stat-value' style='font-size: 24px; color: {nivel_color};'>{nivel.upper()}</div>
                    <div style='color: #8b92a7; margin-top: 8px;'>{roadmap.get('investimento_estimado', 'Consulte detalhes')}</div>
                </div>
                """, unsafe_allow_html=True)
            
            # Botão de mudança de objetivo
            col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
            with col_btn2:
                if st.button("🔄 Mudar Objetivo", use_container_width=True):
                    st.session_state.career_goal = None
                    st.session_state.roadmap = None
                    st.rerun()
            
            st.markdown("---")
            
            # Cargos intermediários se existirem
            cargos_inter = roadmap.get('cargos_intermediarios', [])
            if cargos_inter:
                st.markdown("#### 🎯 Cargos Intermediários Recomendados")
                st.markdown("Para facilitar a transição, considere estas posições estratégicas:")
                for i, cargo in enumerate(cargos_inter, 1):
                    st.markdown(f"{i}. **{cargo}**")
                st.markdown("---")
            
            st.markdown("### 🗺️ Roadmap Estratégico de Desenvolvimento")
            
            etapas = roadmap.get('etapas', [])
            if not etapas:
                st.warning("⚠️ Nenhuma etapa foi gerada no roadmap")
            else:
                for etapa in etapas:
                    ordem = etapa.get('ordem', '?')
                    titulo = etapa.get('titulo', 'Etapa sem título')
                    prazo = etapa.get('prazo', 'Prazo não definido')
                    
                    with st.expander(f"**Etapa {ordem}:** {titulo} ({prazo})", expanded=(ordem == 1)):
                        acoes = etapa.get('acoes', [])
                        if acoes:
                            st.markdown("**🎯 Ações Estratégicas:**")
                            for acao in acoes:
                                st.markdown(f"• {acao}")
                            st.markdown("")
                        
                        skills = etapa.get('skills_desenvolver', [])
                        if skills:
                            st.markdown("**💡 Skills a Desenvolver:**")
                            cols = st.columns(min(len(skills), 3))
                            for i, skill in enumerate(skills):
                                with cols[i % len(cols)]:
                                    st.markdown(f"`{skill}`")
                            st.markdown("")
                        
                        recursos = etapa.get('recursos', [])
                        if recursos:
                            st.markdown("**📚 Recursos Recomendados:**")
                            for recurso in recursos:
                                st.markdown(f"• {recurso}")
                            st.markdown("")
                        
                        indicadores = etapa.get('indicadores_sucesso', [])
                        if indicadores:
                            st.markdown("**✅ Indicadores de Sucesso:**")
                            for indicador in indicadores:
                                st.markdown(f"☑️ {indicador}")
            
            # Fatores críticos
            fatores = roadmap.get('fatores_criticos', [])
            if fatores:
                st.markdown("---")
                st.markdown("### ⚡ Fatores Críticos de Sucesso")
                for fator in fatores:
                    st.warning(f"🔑 {fator}")
            
            # Observações estratégicas
            if roadmap.get('observacoes'):
                st.markdown("---")
                st.markdown("### 💼 Análise Estratégica")
                st.info(roadmap.get('observacoes'))
