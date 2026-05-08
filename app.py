import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Studio AI - Elite", page_icon="⚡", layout="centered")

# A TUA NOVA PALETA DE CORES (Roxo, Azul e Azul Claro)
st.markdown("""
    <style>
    /* Fundo super claro com um toque de azul gelo para um design limpo */
    .stApp { background-color: #F4F7FB; } 
    
    /* Estilo dos Separadores (Tabs) */
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
    
    /* Títulos em Azul Forte */
    h1, h2, h3 { color: #0033CC !important; }
    
    /* Botões em Roxo */
    .stButton>button {
        background-color: #6A0DAD; /* Roxo */
        color: #FFFFFF;
        border-radius: 8px;
        padding: 12px 24px;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    
    /* Botões quando passas o rato (Azul Claro) */
    .stButton>button:hover { 
        background-color: #00BFFF; /* Azul Claro */
        color: white; 
        box-shadow: 0px 4px 12px rgba(0, 191, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# Substitui por link do teu Logótipo real
st.image("https://via.placeholder.com/800x200.png?text=LOG%C3%93TIPO+DO+TEU+EST%C3%9ADIO", use_column_width=True)
st.markdown("---")

# ==========================================
# 2. INICIALIZAR MEMÓRIA DA APP
# ==========================================
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "treino_ativo" not in st.session_state:
    st.session_state.treino_ativo = False
if "historico_estudio" not in st.session_state:
    st.session_state.historico_estudio = [] # Registo invisível para o PT
if "historico_cargas" not in st.session_state:
    st.session_state.historico_cargas = pd.DataFrame(columns=["Data", "Exercício", "Carga (kg)"])

# ==========================================
# 3. LIGAÇÃO À IA (OPENAI)
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Configura a chave API nos Secrets do Streamlit.")

# ==========================================
# 4. A "CÂMARA SECRETA" DO PT (Barra Lateral)
# ==========================================
with st.sidebar:
    st.markdown("### 🔐 Área de Controlo (PT)")
    senha = st.text_input("Password de Acesso", type="password")
    
    if senha == "estudio2026":
        st.success("Acesso Autorizado")
        st.markdown(f"**Treinos Gerados Hoje:** {len(st.session_state.historico_estudio)}")
        st.markdown("---")
        for log in st.session_state.historico_estudio:
            st.info(f"👤 {log['nome']} | 🎯 {log['objetivo']} | ⏱️ {log['hora']}")
    elif senha != "":
        st.error("Password incorreta.")

# ==========================================
# 5. SEPARADORES PRINCIPAIS (TABS)
# ==========================================
tab1, tab2, tab3 = st.tabs(["🏋️ Planeamento", "💬 Chat PT", "📈 Evolução de Cargas"])

# ------------------------------------------
# TAB 1: PLANEAMENTO E WOD
# ------------------------------------------
with tab1:
    if not st.session_state.treino_ativo:
        
        # 5.1 Treino Expresso (WOD)
        st.markdown("### ⚡ Sem tempo hoje?")
        if st.button("🔥 GERAR TREINO EXPRESSO (30 Minutos)"):
            with st.spinner("A preparar o WOD do dia..."):
                prompt_wod = """
                És um PT. Cria um treino metabólico intenso de 30 minutos. Material: Peso corporal e Kettlebells.
                Inclui para cada exercício: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
                """
                st.session_state.mensagens = [{"role": "system", "content": prompt_wod}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                
                # Registo para a Câmara Secreta
                st.session_state.historico_estudio.append({
                    "nome": "Aluno (Expresso)", "objetivo": "WOD Metabólico", 
                    "hora": datetime.now().strftime("%H:%M")
                })
                st.rerun()

        st.markdown("---")
        
        # 5.2 Formulário Completo
        st.markdown("### 📋 Planeamento Personalizado")
        with st.form("perfil_aluno"):
            nome = st.text_input("O teu Nome")
            col1, col2 = st.columns(2)
            with col1:
                objetivo = st.selectbox("Objetivo", ["Massa Muscular", "Perda de Peso", "Condicionamento", "Força"])
                tempo = st.slider("Tempo (minutos)", 20, 90, 45)
            with col2:
                nivel = st.select_slider("Nível", options=["Iniciante", "Intermédio", "Avançado"])
            
            lesoes = st.text_input("Alguma dor ou lesão hoje?", "Nenhuma")
            equipamento = st.multiselect("Material:", ["Máquinas", "Halteres", "Barras", "Kettlebells", "Peso do Corpo"], default=["Máquinas", "Halteres"])

            submit = st.form_submit_button("Gerar Plano Completo ✨")

        if submit and nome.strip():
            with st.spinner("A desenhar o teu treino de elite..."):
                prompt = f"""
                És um PT Especialista de Portugal. Treino para {nome}. Obj: {objetivo}. Nível: {nivel}. Tempo: {tempo}m.
                Lesões a proteger: {lesoes}. Material: {', '.join(equipamento)}.
                Cria uma tabela: Exercício | SériesxReps | Descanso.
                Inclui sempre: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
                """
                st.session_state.mensagens = [{"role": "system", "content": prompt}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                
                # Registo para a Câmara Secreta
                st.session_state.historico_estudio.append({
                    "nome": nome, "objetivo": objetivo, "hora": datetime.now().strftime("%H:%M")
                })
                st.rerun()
    
    # 5.3 O que acontece quando o treino já foi gerado
    else:
        st.success("✅ Plano Ativo! Usa a Tab 'Chat PT' se precisares de adaptar algum exercício.")
        
        # Mostrar o treino
        for msg in st.session_state.mensagens:
            if msg["role"] == "assistant":
                st.markdown(msg["content"])
        
        st.markdown("---")
        colA, colB = st.columns(2)
        with colA:
            # Botão Feedback
            if st.button("✅ Concluir Treino"):
                st.session_state.mensagens.append({"role": "assistant", "content": "Parabéns por concluíres o treino! 💪 De 0 a 10, qual foi o nível de esforço? E como se portaram as tuas articulações?"})
                st.info("Vai à Tab 'Chat PT' para responderes!")
        with colB:
            # Botão Reset
            if st.button("🔄 Novo Treino (Apagar atual)"):
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

# ------------------------------------------
# TAB 2: CHAT COM O PT VIRTUAL
# ------------------------------------------
with tab2:
    st.markdown("### 💬 Ajustes em Tempo Real")
    if not st.session_state.treino_ativo:
        st.info("Gera o teu treino primeiro no separador 'Planeamento'.")
    else:
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        pedido = st.chat_input("Ex: Uma máquina está ocupada, ou, o treino foi nível 8 de cansaço...")
        if pedido:
            st.session_state.mensagens.append({"role": "user", "content": pedido})
            with st.chat_message("user"): st.markdown(pedido)
            with st.chat_message("assistant"):
                with st.spinner("A analisar..."):
                    resposta = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    novo = resposta.choices[0].message.content
                    st.markdown(novo)
            st.session_state.mensagens.append({"role": "assistant", "content": novo})

# ------------------------------------------
# TAB 3: REGISTO E EVOLUÇÃO DE CARGAS
# ------------------------------------------
with tab3:
    st.markdown("### 📈 O teu Diário de Bordo")
    st.write("Regista as cargas levantadas para garantirmos a evolução.")
    
    with st.container():
        col_ex, col_kg, col_btn = st.columns([2, 1, 1])
        with col_ex: ex_input = st.text_input("Exercício (Ex: Supino)")
        with col_kg: carga_input = st.number_input("Carga (kg)", min_value=0.0, step=1.0)
        with col_btn: 
            st.write("") 
            st.write("")
            if st.button("Gravar 💾"):
                if ex_input:
                    nova_carga = pd.DataFrame([{
                        "Data": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Exercício": ex_input,
                        "Carga (kg)": carga_input
                    }])
                    st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, nova_carga], ignore_index=True)
                    st.success("Registado com sucesso!")
    
    st.markdown("---")
    st.markdown("#### Histórico de Hoje")
    if not st.session_state.historico_cargas.empty:
        st.dataframe(st.session_state.historico_cargas, use_container_width=True)
        
        st.markdown("#### Curva de Progressão")
        ex_selecionado = st.selectbox("Ver evolução de:", st.session_state.historico_cargas["Exercício"].unique())
        dados_grafico = st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == ex_selecionado]
        st.line_chart(dados_grafico.set_index("Data")["Carga (kg)"])
    else:
        st.info("Ainda não registaste cargas hoje.")
