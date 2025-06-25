import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import base64
from io import BytesIO
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Dashboard Nutricional",
    page_icon="🍎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E8B57;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem;
    }
    .status-normal { color: #28a745; }
    .status-risk { color: #fd7e14; }
    .status-alert { color: #dc3545; }
</style>
""", unsafe_allow_html=True)

class NutritionDashboard:
    def __init__(self):
        self.data = {}
        
    def load_csv_data(self, file):
        """Carrega e processa os dados do CSV"""
        try:
            # Lê o arquivo CSV
            content = file.read().decode('utf-8')
            lines = content.strip().split('\n')
            
            current_section = None
            section_data = {}
            
            for line in lines:
                line = line.strip()
                if not line or line.startswith('""'):
                    if current_section and section_data:
                        self.data[current_section] = section_data
                        section_data = {}
                    continue
                
                if ',' not in line:
                    current_section = line
                    section_data = {}
                    continue
                
                parts = line.split(',', 1)
                if len(parts) == 2:
                    key, value = parts[0].strip(), parts[1].strip().strip('"')
                    if value and value != '':
                        try:
                            # Tenta converter para número
                            if '.' in value:
                                section_data[key] = float(value)
                            else:
                                section_data[key] = int(value) if value.isdigit() else value
                        except:
                            section_data[key] = value
            
            # Adiciona a última seção
            if current_section and section_data:
                self.data[current_section] = section_data
                
            return True
        except Exception as e:
            st.error(f"Erro ao carregar arquivo: {str(e)}")
            return False
    
    def get_patient_info(self):
        """Extrai informações básicas do paciente"""
        if 'ADOS DO PACIENTE' in self.data:
            return self.data['ADOS DO PACIENTE']
        return {}
    
    def get_anthropometry_data(self):
        """Extrai dados antropométricos"""
        if 'ANTROPOMETRIA' in self.data:
            return self.data['ANTROPOMETRIA']
        return {}
    
    def get_biochemical_data(self):
        """Extrai dados de exames bioquímicos"""
        if 'EXAMES BIOQUÍMICOS' in self.data:
            return self.data['EXAMES BIOQUÍMICOS']
        return {}
    
    def get_mna_data(self):
        """Extrai dados da avaliação MNA"""
        if 'AVALIAÇÃO MNA' in self.data:
            return self.data['AVALIAÇÃO MNA']
        return {}
    
    def calculate_imc(self):
        """Calcula o IMC"""
        anthro = self.get_anthropometry_data()
        if 'Peso Atual (kg)' in anthro and 'Altura (cm)' in anthro:
            peso = anthro['Peso Atual (kg)']
            altura = anthro['Altura (cm)'] / 100
            return peso / (altura ** 2)
        return None
    
    def classify_imc(self, imc):
        """Classifica o IMC"""
        if imc < 18.5:
            return "Baixo peso", "#dc3545"
        elif 18.5 <= imc < 25:
            return "Normal", "#28a745"
        elif 25 <= imc < 30:
            return "Sobrepeso", "#fd7e14"
        else:
            return "Obesidade", "#dc3545"
    
    def create_anthropometry_chart(self):
        """Cria gráfico de dados antropométricos"""
        anthro = self.get_anthropometry_data()
        
        # Dados para comparação (valores de referência)
        metrics = {
            'Peso Atual': anthro.get('Peso Atual (kg)', 0),
            'Peso Usual': anthro.get('Peso Usual (kg)', 0),
            'Circ. Braço': anthro.get('Circunferência do Braço (cm)', 0),
            'Circ. Panturrilha': anthro.get('Circunferência da Panturrilha (cm)', 0),
            'Gordura Corporal': anthro.get('Percentual de Gordura Corporal (%)', 0)
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=list(metrics.keys()),
            y=list(metrics.values()),
            marker_color=['#2E8B57', '#4682B4', '#FF6347', '#32CD32', '#FFD700']
        ))
        
        fig.update_layout(
            title="Dados Antropométricos",
            xaxis_title="Medidas",
            yaxis_title="Valores",
            template="plotly_white"
        )
        
        return fig
    
    def create_biochemical_chart(self):
        """Cria gráfico de exames bioquímicos"""
        bio = self.get_biochemical_data()
        
        # Principais marcadores
        markers = {
            'Glicose': bio.get('Glicose (mg/dL)', 0),
            'Colesterol': bio.get('Colesterol total (mg/dL)', 0),
            'HDL': bio.get('HDL (mg/dL)', 0),
            'LDL': bio.get('LDL (mg/dL)', 0),
            'Albumina': bio.get('Albumina (g/dL)', 0) * 10,  # Multiplicado para visualização
            'Hemoglobina': bio.get('Hemoglobina (g/dL)', 0)
        }
        
        # Valores de referência
        reference_values = {
            'Glicose': 100,
            'Colesterol': 200,
            'HDL': 40,
            'LDL': 100,
            'Albumina': 35,  # 3.5 * 10
            'Hemoglobina': 14
        }
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            name='Valores do Paciente',
            x=list(markers.keys()),
            y=list(markers.values()),
            marker_color='#2E8B57'
        ))
        
        fig.add_trace(go.Bar(
            name='Valores de Referência',
            x=list(reference_values.keys()),
            y=list(reference_values.values()),
            marker_color='#87CEEB',
            opacity=0.7
        ))
        
        fig.update_layout(
            title="Exames Bioquímicos vs Valores de Referência",
            xaxis_title="Marcadores",
            yaxis_title="Valores",
            template="plotly_white",
            barmode='group'
        )
        
        return fig
    
    def create_mna_radar_chart(self):
        """Cria gráfico radar da avaliação MNA"""
        mna = self.get_mna_data()
        
        categories = []
        values = []
        
        # Mapeia as questões MNA para categorias mais legíveis
        mna_mapping = {
            'A. Nos últimos três meses houve diminuição da ingesta alimentar devido a perda de apetite, problemas digestivos ou dificuldade para mastigar ou deglutir?': 'Ingesta Alimentar',
            'B. Perda de peso nos últimos 3 meses': 'Perda de Peso',
            'C. Mobilidade': 'Mobilidade',
            'D. Passou por algum stress psicológico ou doença aguda nos últimos três meses?': 'Stress/Doença',
            'E. Problemas neuropsicológicos': 'Neuropsicológico',
            'F. Índice de Massa Corporal (IMC)': 'IMC'
        }
        
        for question, category in mna_mapping.items():
            if question in mna:
                categories.append(category)
                values.append(mna[question])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories,
            fill='toself',
            name='Avaliação MNA',
            line_color='#2E8B57'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 3]
                )),
            showlegend=True,
            title="Perfil MNA - Mini Avaliação Nutricional"
        )
        
        return fig
    
    def create_nutrition_goals_chart(self):
        """Cria gráfico de metas nutricionais"""
        if 'PRESCRIÇÃO DIETÉTICA' in self.data and 'HISTÓRICO ALIMENTAR' in self.data:
            prescription = self.data['PRESCRIÇÃO DIETÉTICA']
            history = self.data['HISTÓRICO ALIMENTAR']
            
            # Metas vs Consumo atual
            nutrients = {
                'Calorias': {
                    'Meta': prescription.get('Meta Calórica (Kcal/dia)', 0),
                    'Atual': history.get('Total de Calorias', 0)
                },
                'Proteínas': {
                    'Meta': prescription.get('Meta de Proteína (g/dia)', 0),
                    'Atual': history.get('Total de Proteínas', 0)
                },
                'Carboidratos': {
                    'Meta': prescription.get('Meta de Carboidratos (g/dia)', 0),
                    'Atual': history.get('Total de Carboidratos', 0)
                },
                'Gorduras': {
                    'Meta': prescription.get('Meta de Gordura (g/dia)', 0),
                    'Atual': history.get('Total de Gorduras', 0)
                }
            }
            
            categories = list(nutrients.keys())
            metas = [nutrients[cat]['Meta'] for cat in categories]
            atuais = [nutrients[cat]['Atual'] for cat in categories]
            
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Meta',
                x=categories,
                y=metas,
                marker_color='#4682B4'
            ))
            
            fig.add_trace(go.Bar(
                name='Consumo Atual',
                x=categories,
                y=atuais,
                marker_color='#2E8B57'
            ))
            
            fig.update_layout(
                title="Metas Nutricionais vs Consumo Atual",
                xaxis_title="Nutrientes",
                yaxis_title="Quantidade",
                template="plotly_white",
                barmode='group'
            )
            
            return fig
        
        return None
    
    def generate_pdf_report(self):
        """Gera relatório em PDF"""
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Título
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=colors.HexColor('#2E8B57'),
            alignment=1
        )
        story.append(Paragraph("Relatório Nutricional", title_style))
        story.append(Spacer(1, 20))
        
        # Informações do paciente
        patient_info = self.get_patient_info()
        if patient_info:
            story.append(Paragraph("Dados do Paciente", styles['Heading2']))
            
            patient_data = [
                ['Nome:', patient_info.get('Nome', 'N/A')],
                ['Data de Nascimento:', patient_info.get('Data de Nascimento', 'N/A')],
                ['Sexo:', patient_info.get('Sexo', 'N/A')],
                ['Telefone:', patient_info.get('Telefone', 'N/A')],
                ['Registro:', str(patient_info.get('Número de Registro', 'N/A'))]
            ]
            
            patient_table = Table(patient_data, colWidths=[2*inch, 3*inch])
            patient_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(patient_table)
            story.append(Spacer(1, 20))
        
        # Dados antropométricos
        anthro = self.get_anthropometry_data()
        if anthro:
            story.append(Paragraph("Avaliação Antropométrica", styles['Heading2']))
            
            imc = self.calculate_imc()
            imc_classification, _ = self.classify_imc(imc) if imc else ("N/A", "")
            
            anthro_data = [
                ['Peso Atual:', f"{anthro.get('Peso Atual (kg)', 'N/A')} kg"],
                ['Altura:', f"{anthro.get('Altura (cm)', 'N/A')} cm"],
                ['IMC:', f"{imc:.1f}" if imc else "N/A"],
                ['Classificação IMC:', imc_classification],
                ['Circunferência do Braço:', f"{anthro.get('Circunferência do Braço (cm)', 'N/A')} cm"],
                ['% Gordura Corporal:', f"{anthro.get('Percentual de Gordura Corporal (%)', 'N/A')}%"]
            ]
            
            anthro_table = Table(anthro_data, colWidths=[2.5*inch, 2.5*inch])
            anthro_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(anthro_table)
            story.append(Spacer(1, 20))
        
        # Avaliação MNA
        mna = self.get_mna_data()
        if mna:
            story.append(Paragraph("Avaliação MNA", styles['Heading2']))
            
            mna_data = [
                ['Pontuação Total:', str(mna.get('Pontuação Total', 'N/A'))],
                ['Diagnóstico:', mna.get('Diagnóstico', 'N/A')]
            ]
            
            mna_table = Table(mna_data, colWidths=[2.5*inch, 2.5*inch])
            mna_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(mna_table)
            story.append(Spacer(1, 20))
        
        # Prescrição dietética
        if 'PRESCRIÇÃO DIETÉTICA' in self.data:
            prescription = self.data['PRESCRIÇÃO DIETÉTICA']
            story.append(Paragraph("Prescrição Dietética", styles['Heading2']))
            
            prescription_data = [
                ['Tipo de Dieta:', prescription.get('Tipo de Dieta', 'N/A')],
                ['Meta Calórica:', f"{prescription.get('Meta Calórica (Kcal/dia)', 'N/A')} kcal/dia"],
                ['Meta de Proteína:', f"{prescription.get('Meta de Proteína (g/dia)', 'N/A')} g/dia"],
                ['Restrições:', prescription.get('Restrições Alimentare', 'Nenhuma')]
            ]
            
            prescription_table = Table(prescription_data, colWidths=[2.5*inch, 2.5*inch])
            prescription_table.setStyle(TableStyle([
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
            ]))
            story.append(prescription_table)
        
        doc.build(story)
        buffer.seek(0)
        return buffer

def main():
    st.markdown('<h1 class="main-header">🍎 Dashboard Nutricional</h1>', unsafe_allow_html=True)
    
    dashboard = NutritionDashboard()
    
    # Sidebar
    st.sidebar.title("📁 Carregar Dados")
    uploaded_file = st.sidebar.file_uploader(
        "Selecione o arquivo CSV do paciente",
        type=['csv'],
        help="Faça upload do arquivo CSV com os dados nutricionais do paciente"
    )
    
    if uploaded_file is not None:
        if dashboard.load_csv_data(uploaded_file):
            st.sidebar.success("✅ Arquivo carregado com sucesso!")
            
            # Informações básicas do paciente
            patient_info = dashboard.get_patient_info()
            
            if patient_info:
                st.sidebar.markdown("### 👤 Informações do Paciente")
                st.sidebar.write(f"**Nome:** {patient_info.get('Nome', 'N/A')}")
                st.sidebar.write(f"**Idade:** {2025 - int(patient_info.get('Data de Nascimento', '1900').split('-')[0])} anos")
                st.sidebar.write(f"**Sexo:** {patient_info.get('Sexo', 'N/A')}")
            
            # Layout principal
            col1, col2, col3, col4 = st.columns(4)
            
            # Métricas principais
            anthro = dashboard.get_anthropometry_data()
            imc = dashboard.calculate_imc()
            
            with col1:
                peso = anthro.get('Peso Atual (kg)', 0)
                st.metric("Peso Atual", f"{peso} kg")
            
            with col2:
                altura = anthro.get('Altura (cm)', 0)
                st.metric("Altura", f"{altura} cm")
            
            with col3:
                if imc:
                    classification, color = dashboard.classify_imc(imc)
                    st.metric("IMC", f"{imc:.1f}", help=f"Classificação: {classification}")
                else:
                    st.metric("IMC", "N/A")
            
            with col4:
                mna = dashboard.get_mna_data()
                mna_score = mna.get('Pontuação Total', 0)
                st.metric("Score MNA", f"{mna_score}")
            
            st.markdown("---")
            
            # Abas para diferentes visualizações
            tab1, tab2, tab3, tab4 = st.tabs(["📊 Antropometria", "🧪 Exames", "🎯 Avaliação MNA", "🍽️ Nutrição"])
            
            with tab1:
                st.subheader("Dados Antropométricos")
                fig_anthro = dashboard.create_anthropometry_chart()
                st.plotly_chart(fig_anthro, use_container_width=True)
                
                # Tabela detalhada
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Medidas Corporais:**")
                    anthro_display = {
                        "Peso Atual": f"{anthro.get('Peso Atual (kg)', 'N/A')} kg",
                        "Peso Usual": f"{anthro.get('Peso Usual (kg)', 'N/A')} kg",
                        "Circunferência Braço": f"{anthro.get('Circunferência do Braço (cm)', 'N/A')} cm",
                        "Circunferência Panturrilha": f"{anthro.get('Circunferência da Panturrilha (cm)', 'N/A')} cm"
                    }
                    for key, value in anthro_display.items():
                        st.write(f"• {key}: {value}")
                
                with col2:
                    st.markdown("**Composição Corporal:**")
                    composition = {
                        "% Gordura Corporal": f"{anthro.get('Percentual de Gordura Corporal (%)', 'N/A')}%",
                        "Massa Muscular": f"{anthro.get('Massa Muscular (kg)', 'N/A')} kg",
                        "Relação Cintura/Quadril": f"{anthro.get('Relação Cintura/Quadril', 'N/A')}"
                    }
                    for key, value in composition.items():
                        st.write(f"• {key}: {value}")
            
            with tab2:
                st.subheader("Exames Bioquímicos")
                fig_bio = dashboard.create_biochemical_chart()
                st.plotly_chart(fig_bio, use_container_width=True)
                
                bio = dashboard.get_biochemical_data()
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown("**Metabolismo:**")
                    st.write(f"• Glicose: {bio.get('Glicose (mg/dL)', 'N/A')} mg/dL")
                    st.write(f"• Ureia: {bio.get('Ureia (mg/dL)', 'N/A')} mg/dL")
                    st.write(f"• Creatinina: {bio.get('Createina (mg/dL)', 'N/A')} mg/dL")
                
                with col2:
                    st.markdown("**Lipídios:**")
                    st.write(f"• Colesterol Total: {bio.get('Colesterol total (mg/dL)', 'N/A')} mg/dL")
                    st.write(f"• HDL: {bio.get('HDL (mg/dL)', 'N/A')} mg/dL")
                    st.write(f"• LDL: {bio.get('LDL (mg/dL)', 'N/A')} mg/dL")
                
                with col3:
                    st.markdown("**Proteínas:**")
                    st.write(f"• Albumina: {bio.get('Albumina (g/dL)', 'N/A')} g/dL")
                    st.write(f"• Hemoglobina: {bio.get('Hemoglobina (g/dL)', 'N/A')} g/dL")
                    st.write(f"• Ferritina: {bio.get('Ferritina (ng/mL)', 'N/A')} ng/mL")
            
            with tab3:
                st.subheader("Mini Avaliação Nutricional (MNA)")
                fig_mna = dashboard.create_mna_radar_chart()
                st.plotly_chart(fig_mna, use_container_width=True)
                
                mna = dashboard.get_mna_data()
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**Resultado:**")
                    score = mna.get('Pontuação Total', 0)
                    diagnosis = mna.get('Diagnóstico', 'N/A')
                    
                    if score >= 24:
                        st.success(f"Score: {score} - Estado nutricional normal")
                    elif score >= 17:
                        st.warning(f"Score: {score} - {diagnosis}")
                    else:
                        st.error(f"Score: {score} - Desnutrido")
                
                with col2:
                    st.markdown("**Interpretação:**")
                    st.write("• 24-30 pontos: Estado nutricional normal")
                    st.write("• 17-23.5 pontos: Risco de desnutrição")
                    st.write("• < 17 pontos: Desnutrição")
            
            with tab4:
                st.subheader("Prescrição vs Consumo Nutricional")
                fig_nutrition = dashboard.create_nutrition_goals_chart()
                if fig_nutrition:
                    st.plotly_chart(fig_nutrition, use_container_width=True)
                
                # Plano alimentar
                if 'PRESCRIÇÃO DIETÉTICA' in dashboard.data:
                    prescription = dashboard.data['PRESCRIÇÃO DIETÉTICA']
                    st.markdown("**Plano Alimentar:**")
                    plan = prescription.get('Plano Alimentar Detalhado', 'N/A')
                    st.write(plan)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**Metas Diárias:**")
                        st.write(f"• Calorias: {prescription.get('Meta Calórica (Kcal/dia)', 'N/A')} kcal")
                        st.write(f"• Proteínas: {prescription.get('Meta de Proteína (g/dia)', 'N/A')} g")
                        st.write(f"• Carboidratos: {prescription.get('Meta de Carboidratos (g/dia)', 'N/A')} g")
                    
                    with col2:
                        st.markdown("**Restrições e Suplementos:**")
                        st.write(f"• Restrições: {prescription.get('Restrições Alimentare', 'Nenhuma')}")
                        st.write(f"• Suplementos: {prescription.get('Suplementos Nutricionais', 'Nenhum')}")
            
            st.markdown("---")
            
            # Botão para gerar PDF
            if st.button("📄 Gerar Relatório PDF", type="primary"):
                with st.spinner("Gerando relatório..."):
                    pdf_buffer = dashboard.generate_pdf_report()
                    
                    st.download_button(
                        label="⬇️ Baixar Relatório PDF",
                        data=pdf_buffer.getvalue(),
                        file_name=f"relatorio_nutricional_{patient_info.get('Nome', 'paciente').replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
                    st.success("✅ Relatório gerado com sucesso!")
        
        else:
            st.error("❌ Erro ao carregar o arquivo. Verifique o formato dos dados.")
    
    else:
        st.info("👆 Faça upload de um arquivo CSV para começar a análise.")
        
        # Instruções
        st.markdown("""
        ### 📋 Como usar:
        
        1. **Faça upload do arquivo CSV** com os dados do paciente
        2. **Explore as abas** para visualizar diferentes aspectos da avaliação nutricional
        3. **Analise os gráficos** e métricas apresentadas
        4. **Gere um relatório PDF** para documentação
        
        ### 📊 O que você encontrará:
        
        - **Antropometria**: Peso, altura, IMC, composição corporal
        - **Exames**: Resultados bioquímicos e marcadores nutricionais  
        - **Avaliação MNA**: Mini avaliação nutricional para idosos
        - **Nutrição**: Prescrição dietética vs consumo atual
        
        ### 🎯 Funcionalidades:
        
        - ✅ Dashboard interativo com gráficos dinâmicos
        - ✅ Análise automática de dados nutricionais
        - ✅ Classificação automática de IMC e MNA
        - ✅ Geração de relatórios em PDF
        - ✅ Interface responsiva e intuitiva
        """)

if __name__ == "__main__":
    main()