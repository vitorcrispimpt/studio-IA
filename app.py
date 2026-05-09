import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & IDENTIDADE VISUAL
# ==========================================
st.set_page_config(page_title="Studio AI - Coach", page_icon="⚡", layout="centered")

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

# ==========================================
# 3. LIGAÇÃO À IA E BASES DE DADOS
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro técnico: Chave API não encontrada nos Secrets.")

BENCHMARKS = {
    "Nenhum": "Selecione um WOD Clássico para ver a referência...",
    "Fran": "21-15-9 reps for time: Thrusters (43/30kg) and Pull-ups.",
    "Murph": "For time: 1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run (Com colete 9/6kg)."
}

# 🗂️ BASE DE DADOS DE ALUNOS VIP (Podes adicionar mais depois)
CLIENTES_DB = {
    "👤 Novo Aluno (Preenchimento Manual)": {"obj": "Massa Muscular", "nivel": "Iniciante", "lesoes": "Nenhuma"},
    "João Silva": {"obj": "Massa Muscular", "nivel": "Intermédio", "lesoes": "Dor no ombro direito (evitar overhead pesado)"},
    "Maria Santos": {"obj": "Perda de Peso e Tonificação", "nivel": "Iniciante", "lesoes": "Lombar sensível, evitar peso morto pesado"},
    "Carlos PT": {"obj": "Força Máxima", "nivel": "Avançado", "lesoes": "Nenhuma"}
}

# ==========================================
# 4. BARRA LATERAL (LOGS)
# ==========================================
with st.sidebar:
    st.markdown("### 📊 Atividade de Hoje")
    st.write(f"**Planeamentos Gerados:** {len(st.session_state.historico_estudio)}")
    if len(st.session_state.historico_estudio) > 0:
        st.dataframe(pd.DataFrame(st.session_state.historico_estudio))

# ==========================================
# 5. SEPARADORES PRINCIPAIS (TABS)
# ==========================================
tab_alunos, tab_coach, tab_chat, tab_ferramentas = st.tabs([
    "🏋️ PT Personalizado", "🦍 Programação Box", "💬 Chat AI", "🧮 Ferramentas"
])

# ------------------------------------------
# TAB 1: TREINO PERSONALIZADO (A MÁQUINA DO COACH)
# ------------------------------------------
with tab_alunos:
    st.markdown("### 📋 Gerador de Microciclos (PT)")
    st.caption("Gera uma semana inteira de treinos, pronta a enviar pelo WhatsApp.")
    
    if not st.session_state.treino_ativo:
        with st.form("perfil_pt_avancado"):
            
            # Seletor de Base de Dados
            cliente_selecionado = st.selectbox("🗂️ Selecionar Aluno:", list(CLIENTES_DB.keys()))
            
            # Preenche os dados automaticamente consoante a escolha
            dados = CLIENTES_DB[cliente_selecionado]
            
            col1, col2 = st.columns(2)
            with col1:
                # Se for Novo Aluno, o campo fica em branco, senão usa o nome da chave
                nome_aluno = st.text_input("Nome do Aluno:", value="" if "Novo Aluno" in cliente_selecionado else cliente_selecionado)
                objetivo = st.text_input("Objetivo:", value=dados["obj"])
                
                # NOVIDADE: Frequência Semanal
                split = st.selectbox("Divisão de Treino (Split):", [
                    "1 Treino Único (Fullbody)",
                    "3x por semana (Fullbody)",
                    "4x por semana (Upper / Lower)",
                    "5x por semana (Bro Split - 1 músculo por dia)",
                    "6x por semana (Push / Pull / Legs)"
                ])
            
            with col2:
                nivel = st.selectbox("Nível de Experiência:", ["Iniciante", "Intermédio", "Avançado"], index=["Iniciante", "Intermédio", "Avançado"].index(dados["nivel"]))
                duracao = st.slider("Duração de cada treino (min):", 30, 120, 60)
            
            lesoes = st.text_area("Restrições / Notas Específicas:", value=dados["lesoes"], height=68)
            
            submit_pt = st.form_submit_button("🚀 Gerar Microciclo & Formato WhatsApp")
            
            if submit_pt and nome_aluno.strip():
                with st.spinner(f"A criar a arquitetura de treino para {nome_aluno}..."):
                    prompt = f"""
                    És o Personal Trainer mais conceituado de Portugal, especialista em biomecânica e hipertrofia.
                    Tarefa: Desenhar a programação para o aluno {nome_aluno}.
                    Objetivo: {objetivo} | Nível: {nivel} | Duração por treino: {duracao} min.
                    Restrições obrigatórias: {lesoes}.
                    Estrutura solicitada: {split}.
                    
                    A tua resposta DEVE conter duas secções perfeitamente separadas:
                    
                    === PARTE 1: VISÃO DO COACH 🧠 ===
                    Um parágrafo rápido para mim (o treinador principal), explicando porque escolheste esta distribuição de volume e que cuidados tiveste com a lesão do aluno. Mostra conhecimento técnico (Landmarks de volume, RPE, seleção de exercícios).
                    
                    === PARTE 2: PRONTO A COPIAR PARA WHATSAPP 📱 ===
                    Abaixo desta linha, escreve a programação COMPLETA da semana de forma extremamente limpa, usando listas de texto simples e Emojis. 
                    NÃO USES TABELAS MARKDOWN (pois ficam horríveis e desconfiguradas no telemóvel do aluno).
                    Usa o formato:
                    
                    🏋️‍♂️ *DIA 1: Nome do Foco*
                    🔸 Exercício 1: X séries x Y reps (Descanso: Z)
                    🔸 Exercício 2...
                    (E assim sucessivamente para todos os dias do split).
                    
                    Inclui notas breves de execução (ex: "foca na excêntrica") em itálico abaixo dos exercícios mais complexos. Termina com uma mensagem motivadora do Coach.
                    """
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.treino_ativo = True
                    st.session_state.historico_estudio.append({"nome": nome_aluno, "objetivo": "Microciclo PT", "hora": datetime.now().strftime("%H:%M")})
                    st.rerun()

    else:
        st.success("✅ Microciclo gerado com sucesso!")
        st.markdown(st.session_state.mensagens[-1]["content"])
        st.markdown("---")
        if st.button("🔄 Concluir e Planear Outro Aluno"):
            st.session_state.treino_ativo = False
            st.session_state.mensagens = []
            st.rerun()

# ------------------------------------------
# TAB 2: ÁREA DO COACH / CROSSFIT (MANTIDA)
# ------------------------------------------
with tab_coach:
    st.markdown("### 🦍 Programação Interna da Box")
    st.caption("Gera periodizações precisas para as aulas de grupo.")
    
    if not st.session_state.treino_ativo:
        with st.form("perfil_box"):
            colA, colB = st.columns(2)
            with colA:
                ciclo = st.selectbox("Duração a Gerar:", ["1 Aula (Hoje)", "1 Semana (Seg-Sáb)", "1 Mês (Periodização)"])
                foco_box = st.selectbox("Foco Principal:", ["Geral (Equilibrado)", "Força Base", "Ginástica", "Endurance"])
            with colB:
                estilo_wod = st.selectbox("Estilo do WOD:", [
                    "🌶️ Inovador & Fora da Caixa", "🔥 Teste Mental / Grit", "🛠️ Técnico e Tático", "🧱 Clássico e Direto"
                ])

            historico = st.text_area("📋 Histórico do Ciclo Anterior (Opcional):")
            regras = st.text_area("Regras Específicas do Coach:")
            
            if st.form_submit_button("🔥 Gerar Programação da Box"):
                with st.spinner("A desenhar o próximo ciclo..."):
                    prompt = f"És Head Coach CrossFit. Cria programação de {ciclo}. Foco: {foco_box}. Estilo: {estilo_wod}. Regras: {regras}. Histórico passado: {historico}. Define RX e Scaled."
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.treino_ativo = True
                    st.rerun()
    else:
        st.markdown(st.session_state.mensagens[-1]["content"])
        st.markdown("---")
        if st.button("🔄 Nova Programação da Box"):
            st.session_state.treino_ativo = False
            st.session_state.mensagens = []
            st.rerun()

# ------------------------------------------
# TAB 3: CHAT AI
# ------------------------------------------
with tab_chat:
    st.markdown("### 💬 Chat com o Coach Virtual")
    if len(st.session_state.mensagens) == 0:
        st.info("Gera um planeamento primeiro para poderes afiná-lo aqui.")
    else:
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): 
                    st.markdown(msg["content"])
        
        chat_input = st.chat_input("Pede ajustes rápidos (Ex: Troca a máquina de Extensão de Pernas por outra coisa)...")
        if chat_input:
            st.session_state.mensagens.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)
            with st.chat_message("assistant"):
                with st.spinner("A reajustar..."):
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    novo = response.choices[0].message.content
                    st.markdown(novo)
            st.session_state.mensagens.append({"role": "assistant", "content": novo})

# ------------------------------------------
# TAB 4: FERRAMENTAS
# ------------------------------------------
with tab_ferramentas:
    col_calc, col_graph = st.columns([1, 1.2])

    with col_calc:
        st.markdown("### 🧮 Percentagens 1RM")
        with st.container():
            st.markdown('<div class="calc-box">', unsafe_allow_html=True)
            rm_valor = st.number_input("1RM (kg):", min_value=0.0, step=2.5, value=100.0)
            percentagens = [50, 60, 70, 75, 80, 85, 90, 95]
            dados_calc = {"%": [f"{p}%" for p in percentagens], "Carga": [f"{rm_valor * (p/100):.1f} kg" for p in percentagens]}
            st.table(pd.DataFrame(dados_calc))
            st.markdown('</div>', unsafe_allow_html=True)

    with col_graph:
        st.markdown("### 📈 Teste de Registo")
        st.info("Ferramenta interna de testes rápidos.")
