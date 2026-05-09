import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Studio AI - Pro", page_icon="⚡", layout="centered")

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
    /* Estilo para a Calculadora */
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

# ==========================================
# 3. LIGAÇÃO À IA E BENCHMARKS
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Configura a chave API nos Secrets.")

BENCHMARKS = {
    "Nenhum": "Selecione um WOD Clássico...",
    "Fran": "21-15-9 reps for time: Thrusters (43/30kg) and Pull-ups.",
    "Murph": "For time: 1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run (Com colete 9/6kg).",
    "Cindy": "AMRAP 20 min: 5 Pull-ups, 10 Push-ups, 15 Air Squats.",
    "Grace": "For time: 30 Clean & Jerks (61/43kg).",
    "Hellen": "3 Rounds: 400m Run, 21 Kettlebell Swings (24/16kg), 12 Pull-ups."
}

# ==========================================
# 4. A "CÂMARA SECRETA" (SIDEBAR)
# ==========================================
with st.sidebar:
    st.markdown("### 🔐 Área PT")
    senha = st.text_input("Password", type="password")
    if senha == "estudio2026":
        st.success("Acesso Autorizado")
        st.write(f"Logs hoje: {len(st.session_state.historico_estudio)}")
        st.dataframe(pd.DataFrame(st.session_state.historico_estudio))

# ==========================================
# 5. SEPARADORES PRINCIPAIS (TABS)
# ==========================================
tab1, tab2, tab3, tab4 = st.tabs(["🏋️ Treino", "🔥 Box CrossFit", "💬 Chat", "📈 Evolução & Calculadora"])

# ------------------------------------------
# TAB 1 & 2: GERAÇÃO DE TREINO E BOX
# ------------------------------------------
with tab1:
    if not st.session_state.treino_ativo:
        st.markdown("### 📋 Planeamento Personalizado")
        with st.form("perfil_aluno"):
            nome = st.text_input("Nome")
            col1, col2 = st.columns(2)
            with col1:
                obj = st.selectbox("Objetivo", ["Massa Muscular", "Perda de Peso", "Performance"])
                tempo = st.slider("Tempo", 20, 90, 45)
            with col2:
                nivel = st.select_slider("Nível", options=["Iniciante", "Intermédio", "Avançado"])
            submit = st.form_submit_button("Gerar Treino ✨")
            if submit and nome.strip():
                with st.spinner("A criar..."):
                    prompt = f"És um PT de Portugal. Cria um treino de musculação para {nome}. Obj: {obj}. Tempo: {tempo}m. Nível: {nivel}. Inclui links 3D."
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.treino_ativo = True
                    st.rerun()
    else:
        st.markdown(st.session_state.mensagens[-1]["content"])
        if st.button("🔄 Novo Treino"):
            st.session_state.treino_ativo = False
            st.rerun()

with tab2:
    st.markdown("### 🦍 Programação da Box")
    with st.expander("🏆 Biblioteca de Benchmarks (WODs Clássicos)"):
        selecao_bench = st.selectbox("Escolhe um Benchmark:", list(BENCHMARKS.keys()))
        if selecao_bench != "Nenhum":
            st.info(f"**{selecao_bench}:** {BENCHMARKS[selecao_bench]}")
    
    st.markdown("---")
    with st.form("perfil_box"):
        ciclo = st.selectbox("Ciclo", ["Hoje", "1 Semana", "1 Mês", "2 Meses"])
        regras = st.text_area("Regras (Ex: Sábado Team WOD)")
        if st.form_submit_button("🔥 Gerar Programação"):
            with st.spinner("A periodizar..."):
                prompt = f"És Head Coach CrossFit. Cria programação de {ciclo}. Regras: {regras}. RX/Scaled e 50min aula."
                st.session_state.mensagens = [{"role": "system", "content": prompt}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                st.rerun()

# ------------------------------------------
# TAB 3: CHAT
# ------------------------------------------
with tab3:
    st.markdown("### 💬 Chat com o Coach AI")
    for msg in st.session_state.mensagens:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]): st.markdown(msg["content"])
    
    chat_input = st.chat_input("Dúvidas sobre o treino ou trocas?")
    if chat_input:
        st.session_state.mensagens.append({"role": "user", "content": chat_input})
        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
        st.rerun()

# ------------------------------------------
# TAB 4: EVOLUÇÃO & CALCULADORA
# ------------------------------------------
with tab4:
    col_calc, col_graph = st.columns([1, 1.2])

    with col_calc:
        st.markdown("### 🧮 Calculadora de % (1RM)")
        with st.container():
            st.markdown('<div class="calc-box">', unsafe_allow_html=True)
            rm_valor = st.number_input("Insere o teu 1RM (kg):", min_value=0.0, step=2.5, value=100.0)
            
            percentagens = [50, 60, 70, 75, 80, 85, 90, 95]
            dados_calc = {"%": [f"{p}%" for p in percentagens], "Carga": [f"{rm_valor * (p/100):.1f} kg" for p in percentagens]}
            st.table(pd.DataFrame(dados_calc))
            st.markdown('</div>', unsafe_allow_html=True)

    with col_graph:
        st.markdown("### 📈 Registo de Cargas")
        ex = st.text_input("Exercício (Ex: Back Squat)")
        carga = st.number_input("Carga Levantada (kg)", min_value=0.0, step=1.0)
        if st.button("💾 Registar PR"):
            novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Exercício": ex, "Carga": carga}])
            st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, novo], ignore_index=True)
            st.success("Carga guardada!")

        if not st.session_state.historico_cargas.empty:
            st.markdown("---")
            filtro_ex = st.selectbox("Progresso de:", st.session_state.historico_cargas["Exercício"].unique())
            df_plot = st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == filtro_ex]
            st.line_chart(df_plot.set_index("Data")["Carga"])
