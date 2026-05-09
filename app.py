import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Studio AI - Elite", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F4F7FB; } 
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
    h1, h2, h3 { color: #0033CC !important; }
    .stButton>button {
        background-color: #6A0DAD; color: #FFFFFF; border-radius: 8px;
        padding: 12px 24px; border: none; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #00BFFF; color: white; box-shadow: 0px 4px 12px rgba(0, 191, 255, 0.4);
    }
    .calc-box {
        background-color: #FFFFFF; padding: 20px; border-radius: 12px;
        border: 1px solid #E0E0E0; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.image("https://via.placeholder.com/800x200.png?text=LOG%C3%93TIPO+DO+TEU+EST%C3%9ADIO", use_column_width=True)

# ==========================================
# 2. INICIALIZAR MEMÓRIA DA APP
# ==========================================
if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "treino_ativo" not in st.session_state: st.session_state.treino_ativo = False
if "historico_estudio" not in st.session_state: st.session_state.historico_estudio = [] 
if "historico_cargas" not in st.session_state:
    st.session_state.historico_cargas = pd.DataFrame(columns=["Data", "Exercício", "Carga (kg)"])
# Nova variável para controlar quem é o Coach
if "is_coach" not in st.session_state: st.session_state.is_coach = False

# ==========================================
# 3. LIGAÇÃO À IA E BENCHMARKS
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro técnico: Chave API não encontrada.")

BENCHMARKS = {
    "Nenhum": "Selecione um WOD Clássico para ver a referência...",
    "Fran": "21-15-9 reps for time: Thrusters (43/30kg) and Pull-ups.",
    "Murph": "For time: 1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run (Com colete 9/6kg).",
    "Cindy": "AMRAP 20 min: 5 Pull-ups, 10 Push-ups, 15 Air Squats.",
    "Grace": "For time: 30 Clean & Jerks (61/43kg).",
    "Hellen": "3 Rounds: 400m Run, 21 Kettlebell Swings (24/16kg), 12 Pull-ups."
}

# ==========================================
# 4. A "CÂMARA SECRETA" (SIDEBAR - CONTROLO DE ACESSO)
# ==========================================
with st.sidebar:
    st.markdown("### 🔐 Acesso Equipa Técnica")
    senha = st.text_input("Password do Coach", type="password")
    
    if senha == "estudio2026":
        st.session_state.is_coach = True
        st.success("✅ Acesso de Coach Autorizado!")
        st.markdown("---")
        st.write(f"**Treinos Alunos Hoje:** {len(st.session_state.historico_estudio)}")
        if len(st.session_state.historico_estudio) > 0:
            st.dataframe(pd.DataFrame(st.session_state.historico_estudio))
    elif senha != "":
        st.session_state.is_coach = False
        st.error("❌ Password incorreta.")
    else:
        st.session_state.is_coach = False

# ==========================================
# 5. SEPARADORES PRINCIPAIS (TABS)
# ==========================================
tab_alunos, tab_chat, tab_ferramentas, tab_coach = st.tabs([
    "🏋️ Treino Alunos", "💬 Chat AI", "🧮 Ferramentas", "🔐 Programação Box"
])

# ------------------------------------------
# TAB 1: ÁREA DE ALUNOS (PÚBLICA)
# ------------------------------------------
with tab_alunos:
    if not st.session_state.treino_ativo:
        st.markdown("### 📋 Planeamento Personalizado (Estúdio)")
        with st.form("perfil_aluno"):
            nome = st.text_input("O teu Nome")
            col1, col2 = st.columns(2)
            with col1:
                obj = st.selectbox("Objetivo", ["Massa Muscular", "Perda de Peso", "Performance Geral"])
                tempo = st.slider("Tempo (minutos)", 20, 90, 45)
            with col2:
                nivel = st.select_slider("Nível", options=["Iniciante", "Intermédio", "Avançado"])
            
            lesoes = st.text_input("Alguma restrição ou dor?", "Nenhuma")
            submit_aluno = st.form_submit_button("Gerar Treino ✨")
            
            if submit_aluno and nome.strip():
                with st.spinner("A desenhar o teu treino..."):
                    prompt = f"""
                    És um PT. Cria treino de musculação para {nome}. Obj: {obj}. Tempo: {tempo}m. Nível: {nivel}. Restrições: {lesoes}.
                    Inclui sempre link 3D: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
                    """
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.treino_ativo = True
                    st.session_state.historico_estudio.append({"nome": nome, "objetivo": obj, "hora": datetime.now().strftime("%H:%M")})
                    st.rerun()
    else:
        st.markdown(st.session_state.mensagens[-1]["content"])
        st.markdown("---")
        if st.button("🔄 Concluir e Fazer Novo Treino"):
            st.session_state.treino_ativo = False
            st.session_state.mensagens = []
            st.rerun()

# ------------------------------------------
# TAB 2: CHAT AI (PÚBLICA)
# ------------------------------------------
with tab_chat:
    st.markdown("### 💬 Chat com o Coach Virtual")
    if len(st.session_state.mensagens) == 0:
        st.info("Gera um treino primeiro no separador 'Treino Alunos'.")
    else:
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): 
                    st.markdown(msg["content"])
        
        chat_input = st.chat_input("Ex: Uma máquina está ocupada, o que faço?")
        if chat_input:
            st.session_state.mensagens.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)
            with st.chat_message("assistant"):
                with st.spinner("A analisar..."):
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    novo = response.choices[0].message.content
                    st.markdown(novo)
            st.session_state.mensagens.append({"role": "assistant", "content": novo})

# ------------------------------------------
# TAB 3: FERRAMENTAS ALUNOS (PÚBLICA)
# ------------------------------------------
with tab_ferramentas:
    col_calc, col_graph = st.columns([1, 1.2])

    with col_calc:
        st.markdown("### 🧮 Percentagens 1RM")
        with st.container():
            st.markdown('<div class="calc-box">', unsafe_allow_html=True)
            rm_valor = st.number_input("O teu 1RM (kg):", min_value=0.0, step=2.5, value=100.0)
            percentagens = [50, 60, 70, 75, 80, 85, 90, 95]
            dados_calc = {"%": [f"{p}%" for p in percentagens], "Carga": [f"{rm_valor * (p/100):.1f} kg" for p in percentagens]}
            st.table(pd.DataFrame(dados_calc))
            st.markdown('</div>', unsafe_allow_html=True)

    with col_graph:
        st.markdown("### 📈 Registo de Cargas (PR)")
        ex = st.text_input("Exercício (Ex: Back Squat)")
        carga = st.number_input("Carga Levantada (kg)", min_value=0.0, step=1.0)
        if st.button("💾 Guardar PR"):
            novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y %H:%M"), "Exercício": ex, "Carga": carga}])
            st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, novo], ignore_index=True)
            st.success("Carga guardada com sucesso!")

        if not st.session_state.historico_cargas.empty:
            st.markdown("---")
            filtro_ex = st.selectbox("Progresso de:", st.session_state.historico_cargas["Exercício"].unique())
            df_plot = st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == filtro_ex]
            st.line_chart(df_plot.set_index("Data")["Carga"])

# ------------------------------------------
# TAB 4: ÁREA DO COACH / CROSSFIT (TRANCADA)
# ------------------------------------------
with tab_coach:
    if st.session_state.is_coach:
        st.markdown("### 🦍 Programação Interna da Box")
        st.caption("Bem-vindo ao Backoffice. Usa esta ferramenta para gerar as aulas semanais.")
        
        with st.expander("🏆 Referência: Benchmarks e Hero WODs"):
            selecao_bench = st.selectbox("Consulta rápida de WODs:", list(BENCHMARKS.keys()))
            if selecao_bench != "Nenhum":
                st.info(f"**{selecao_bench}:** {BENCHMARKS[selecao_bench]}")
        
        st.markdown("---")
        with st.form("perfil_box"):
            ciclo = st.selectbox("Duração do Ciclo a Gerar:", ["1 Aula (Hoje)", "1 Semana (Seg-Sáb)", "1 Mês (Periodização)"])
            foco_box = st.selectbox("Foco Principal:", ["Geral (Equilibrado)", "Força Base (Weightlifting)", "Ginástica", "Endurance (Cardio)"])
            regras = st.text_area("Regras Específicas do Head Coach (Ex: Sábado é Team WOD, focar em cleans na quarta):")
            
            if st.form_submit_button("🔥 Gerar Programação da Box"):
                with st.spinner("A calcular a periodização ótima para os alunos..."):
                    prompt = f"""
                    És Head Coach de uma Box de CrossFit. Cria a programação oficial para o ciclo de: {ciclo}.
                    Foco da periodização: {foco_box}.
                    Regras obrigatórias: {regras}.
                    
                    Cada aula diária TEM de ter a estrutura exata de 50 minutos:
                    - Warm-up (10m)
                    - Skill/Strength (15m) -> Define cargas RX e Scaled.
                    - WOD (15m) -> Define RX, Scaled e Time Cap obrigatório.
                    - Cooldown (5m) + 5m de transições totais.
                    
                    Se for mais que 1 dia, cria um planeamento coeso e que não sobrecarregue os mesmos grupos musculares repetidamente. Usa a terminologia oficial do CrossFit.
                    """
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    # Mostra a programação imediatamente abaixo do botão
                    st.markdown("### 📋 Programação Gerada:")
                    st.markdown(response.choices[0].message.content)
                    
    else:
        st.error("🔒 Área Restrita: Uso exclusivo da Equipa Técnica.")
        st.write("Por favor, abre o menu lateral esquerdo (clica na seta no canto superior esquerdo do ecrã) e insere a **Password do Coach** para aceder ao gerador de programação da Box.")
