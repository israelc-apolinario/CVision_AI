import os
import re
import requests
from typing import Dict, Any
import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CareerIntelligenceAgent:
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("Chave do Gemini não fornecida. Configure GOOGLE_API_KEY.")
        
        if not self._validate_api_key(self.api_key):
            raise ValueError("Formato de chave do Gemini inválido.")
        
        self.model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        self.api_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent"
        
        logger.info(f"Agente inicializado com sucesso (chave: {self.api_key[:10]}..., modelo: {self.model_name})")
    
    def _validate_api_key(self, api_key: str) -> bool:
        return len(api_key) > 20 and api_key.startswith('AIza')
    
    def _sanitize_input(self, text: str) -> str:
        if not text or not isinstance(text, str):
            raise ValueError("Texto do currículo inválido.")
        
        max_size = 50000
        if len(text) > max_size:
            raise ValueError(f"Texto muito grande. Máximo: {max_size} caracteres.")
        
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        return text.strip()
    
    def chat(self, message: str, context: str = "") -> str:
        prompt = f"""Consultor de carreira sênior especializado em tecnologia.

Orientações:
- Respostas objetivas e diretas
- Foco em desenvolvimento profissional e técnico
- Análise baseada em dados e experiência de mercado

{f"Contexto: {context}" if context else ""}

Pergunta: {message}

Resposta:"""

        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": 0.8,
                    "maxOutputTokens": 2048
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 429:
                fallback_models = ["gemini-1.5-flash-latest", "gemini-pro"]
                for model in fallback_models:
                    try:
                        fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                        response = requests.post(
                            f"{fallback_url}?key={self.api_key}",
                            headers=headers,
                            json=payload,
                            timeout=60
                        )
                        if response.status_code == 200:
                            break
                    except:
                        continue
            
            if response.status_code != 200:
                return "Desculpe, tive um problema ao processar sua pergunta. Pode reformular?"
            
            result_data = response.json()
            return result_data['candidates'][0]['content']['parts'][0]['text']
            
        except Exception as e:
            logger.error(f"Erro no chat: {e}")
            return "Ops! Algo deu errado. Pode tentar novamente?"
    
    def analyze_resume(self, resume_text: str) -> Dict[str, Any]:
        try:
            resume_text = self._sanitize_input(resume_text)
        except ValueError as e:
            logger.error(f"Erro na validação de entrada: {e}")
            raise
        
        logger.info(f"Analisando currículo: {len(resume_text)} caracteres")
        logger.info("Iniciando análise de currículo...")
        print("🔍 Analisando currículo...")
        
        prompt = f"""Analise este currículo profissionalmente e retorne um JSON estruturado.

Identifique:
- Profissão real baseada em experiências e responsabilidades
- Nível de senioridade atual
- Lacunas técnicas e comportamentais
- Próximo cargo lógico na carreira
- Plano de desenvolvimento profissional

CURRÍCULO:
{resume_text}

Retorne APENAS JSON (sem markdown):
{{
    "profissao_real": {{"titulo": "título claro", "descricao": "descrição prática", "nivel_confianca": "alto/médio/baixo"}},
    "nivel_senioridade": {{"nivel": "Júnior/Pleno/Sênior/Especialista", "anos_experiencia": número, "justificativa": "análise detalhada"}},
    "lacunas": {{
        "tecnicas": [{{"skill": "skill específica", "importancia": "alta/média/baixa", "como_desenvolver": "ação prática"}}],
        "comportamentais": [{{"competencia": "competência clara", "importancia": "alta/média/baixa", "como_desenvolver": "conselho prático"}}]
    }},
    "proximo_cargo": {{"cargo": "título realista", "prazo_estimado": "timeframe", "requisitos": ["item claro"], "probabilidade": "alta/média/baixa"}},
    "plano_crescimento": {{
        "objetivo": "objetivo inspirador mas alcançável",
        "prazo_total": "prazo realista",
        "etapas": [{{"numero": 1, "titulo": "fase clara", "prazo": "tempo", "acoes": ["ação específica"], "recursos": ["recurso útil"], "indicadores_sucesso": ["métrica clara"]}}],
        "certificacoes_sugeridas": ["certificação relevante"],
        "cursos_recomendados": ["curso específico"]
    }}
}}"""
        
        try:
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 8192
                }
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(
                f"{self.api_url}?key={self.api_key}",
                headers=headers,
                json=payload,
                timeout=120
            )
            
            if response.status_code == 429:
                logger.warning("Rate limit atingido. Tentando modelos alternativos...")
                print("⚠️ Limite de requisições atingido. Tentando modelo alternativo...")
                
                fallback_models = [
                    "gemini-1.5-flash-latest",
                    "gemini-1.5-pro-latest",
                    "gemini-pro"
                ]
                
                for model in fallback_models:
                    try:
                        fallback_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
                        response = requests.post(
                            f"{fallback_url}?key={self.api_key}",
                            headers=headers,
                            json=payload,
                            timeout=120
                        )
                        
                        if response.status_code == 200:
                            logger.info(f"Sucesso com modelo: {model}")
                            break
                    except:
                        continue
                
                if response.status_code != 200:
                    logger.error(f"Todos os modelos falharam. Status: {response.status_code}")
                    raise ValueError(f"Limite diário atingido. Aguarde algumas horas ou use outra API key.")
            
            elif response.status_code != 200:
                logger.error(f"Erro API: {response.status_code} - {response.text}")
                raise ValueError(f"Erro na API Gemini: {response.status_code}")
            
            result_data = response.json()
            result_text = result_data['candidates'][0]['content']['parts'][0]['text']
            
            # Limpar markdown e espaços
            result_text = result_text.strip()
            if result_text.startswith('```'):
                lines = result_text.split('\n')
                result_text = '\n'.join(lines[1:-1]) if len(lines) > 2 else result_text
            result_text = result_text.replace('```json', '').replace('```', '').strip()
            
            result = json.loads(result_text)
            logger.info("Análise concluída com sucesso")
            print("✅ Análise completa!")
            return result
            
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao decodificar resposta JSON: {str(e)}")
            logger.error(f"Texto recebido: {result_text[:200] if 'result_text' in locals() else 'N/A'}")
            raise ValueError("Erro ao processar resposta. Tente novamente.")
        except Exception as e:
            logger.error(f"Erro na análise: {type(e).__name__}")
            print(f"❌ Erro na análise: {type(e).__name__}")
            raise
    
    def identify_real_profession(self, resume_text: str) -> Dict[str, str]:
        result = self.analyze_resume(resume_text)
        return result.get('profissao_real', {})
    
    def classify_seniority(self, resume_text: str) -> Dict[str, Any]:
        result = self.analyze_resume(resume_text)
        return result.get('nivel_senioridade', {})
    
    def detect_gaps(self, resume_text: str) -> Dict[str, list]:
        result = self.analyze_resume(resume_text)
        return result.get('lacunas', {})
    
    def project_next_role(self, resume_text: str) -> Dict[str, Any]:
        result = self.analyze_resume(resume_text)
        return result.get('proximo_cargo', {})
    
    def create_growth_plan(self, resume_text: str) -> Dict[str, Any]:
        result = self.analyze_resume(resume_text)
        return result.get('plano_crescimento', {})
    
    def generate_report(self, analysis: Dict[str, Any]) -> str:
        report = []
        report.append("=" * 80)
        report.append("📊 RELATÓRIO DE INTELIGÊNCIA DE CARREIRA")
        report.append("=" * 80)
        report.append("")
        
        if 'profissao_real' in analysis:
            prof = analysis['profissao_real']
            report.append("🎯 1. PROFISSÃO REAL IDENTIFICADA")
            report.append(f"   Título: {prof.get('titulo', 'N/A')}")
            report.append(f"   Descrição: {prof.get('descricao', 'N/A')}")
            report.append(f"   Confiança: {prof.get('nivel_confianca', 'N/A')}")
            report.append("")
        
        if 'nivel_senioridade' in analysis:
            sen = analysis['nivel_senioridade']
            report.append("📈 2. NÍVEL DE SENIORIDADE")
            report.append(f"   Nível: {sen.get('nivel', 'N/A')}")
            report.append(f"   Anos de experiência: {sen.get('anos_experiencia', 'N/A')}")
            report.append(f"   Justificativa: {sen.get('justificativa', 'N/A')}")
            report.append("")
        
        if 'lacunas' in analysis:
            lacunas = analysis['lacunas']
            report.append("🔍 3. LACUNAS IDENTIFICADAS")
            report.append("")
            report.append("   Lacunas Técnicas:")
            for gap in lacunas.get('tecnicas', []):
                report.append(f"   • {gap.get('skill', 'N/A')} (Importância: {gap.get('importancia', 'N/A')})")
                report.append(f"     Como desenvolver: {gap.get('como_desenvolver', 'N/A')}")
            report.append("")
            report.append("   Lacunas Comportamentais:")
            for gap in lacunas.get('comportamentais', []):
                report.append(f"   • {gap.get('competencia', 'N/A')} (Importância: {gap.get('importancia', 'N/A')})")
                report.append(f"     Como desenvolver: {gap.get('como_desenvolver', 'N/A')}")
            report.append("")
        
        if 'proximo_cargo' in analysis:
            prox = analysis['proximo_cargo']
            report.append("🚀 4. PRÓXIMO CARGO PROVÁVEL")
            report.append(f"   Cargo: {prox.get('cargo', 'N/A')}")
            report.append(f"   Prazo estimado: {prox.get('prazo_estimado', 'N/A')}")
            report.append(f"   Probabilidade: {prox.get('probabilidade', 'N/A')}")
            report.append("   Requisitos:")
            for req in prox.get('requisitos', []):
                report.append(f"   • {req}")
            report.append("")
        
        if 'plano_crescimento' in analysis:
            plano = analysis['plano_crescimento']
            report.append("📋 5. PLANO PRÁTICO DE CRESCIMENTO")
            report.append(f"   Objetivo: {plano.get('objetivo', 'N/A')}")
            report.append(f"   Prazo total: {plano.get('prazo_total', 'N/A')}")
            report.append("")
            report.append("   Etapas:")
            for etapa in plano.get('etapas', []):
                report.append(f"   Etapa {etapa.get('numero', 'N/A')}: {etapa.get('titulo', 'N/A')} ({etapa.get('prazo', 'N/A')})")
                report.append("   Ações:")
                for acao in etapa.get('acoes', []):
                    report.append(f"     • {acao}")
                report.append("")
            
            if plano.get('certificacoes_sugeridas'):
                report.append("   Certificações Sugeridas:")
                for cert in plano['certificacoes_sugeridas']:
                    report.append(f"   • {cert}")
                report.append("")
            
            if plano.get('cursos_recomendados'):
                report.append("   Cursos Recomendados:")
                for curso in plano['cursos_recomendados']:
                    report.append(f"   • {curso}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


if __name__ == "__main__":
    print("Career Intelligence AI Agent")
    print("=" * 50)
    

    exemplo_curriculo = """
    JOÃO SILVA
    Desenvolvedor de Software
    
    EXPERIÊNCIA:
    - Desenvolvedor Full Stack na Tech Corp (2021-2023)
      * Desenvolvimento de aplicações web com React e Node.js
      * Implementação de APIs RESTful
      * Trabalho em equipe ágil com Scrum
    
    - Desenvolvedor Junior na StartupXYZ (2019-2021)
      * Manutenção de código legacy
      * Criação de testes unitários
      * Suporte ao cliente
    
    HABILIDADES:
    JavaScript, React, Node.js, SQL, Git
    
    FORMAÇÃO:
    Bacharelado em Ciência da Computação (2015-2019)
    """
    
    try:
        agent = CareerIntelligenceAgent()
        print("\n🔄 Iniciando análise completa...\n")
        
        analysis = agent.analyze_resume(exemplo_curriculo)
        report = agent.generate_report(analysis)
        
        print(report)
        
        with open('analise_carreira.json', 'w', encoding='utf-8') as f:
            json.dump(analysis, f, ensure_ascii=False, indent=2)
        
        with open('relatorio_carreira.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        print("\n✅ Arquivos salvos: analise_carreira.json e relatorio_carreira.txt")
        
    except ValueError as e:
        print(f"\n⚠️  {e}")
        print("Configure a variável de ambiente GOOGLE_API_KEY ou passe a chave no construtor.")
