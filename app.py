import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & UI (ESTILO APPLE)
# ==========================================
st.set_page_config(page_title="Studio AI - Pro", page_icon="⚡", layout="centered")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; } 
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; color: #333; }
    h1, h2, h3 { color: #111 !important; font-family: 'San Francisco', Helvetica, Arial, sans-serif; }
    
    /* Botões Premium */
    .stButton>button {
        background-color: #000000; color: #FFFFFF; border-radius: 10px;
        padding: 12px 24px; border: none; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #333333; color: white; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    }
    
    /* Caixas de login e ferramentas */
    .premium-box {
        background-color: #FFFFFF; padding: 30px; border-radius: 16px;
        border: 1px solid #EAEAEA; box-shadow: 0px 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. BASE DE DADOS SIMULADA (O "COFRE" DA APP)
# ==========================================
# Aqui defines quem tem acesso à app (quem pagou a subscrição)
USERS_DB = {
    "coach": {"pwd": "admin", "role": "coach", "name": "Head Coach"},
    "joao": {"pwd": "123", "role": "student", "name": "João Silva", "obj": "Massa Muscular", "nivel": "Intermédio", "lesoes": "Ombro direito"},
    "maria": {"pwd": "abc", "role": "student", "name": "Maria Santos", "obj": "Perda de Peso", "nivel": "Iniciante", "lesoes": "Nenhuma"}
}

# ==========================================
# 3. MEMÓRIA DE SESSÃO
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "username" not in st.session_state: st.session_state.username = ""
if "role" not in st.session_state: st.session_state.role = ""
if "user_data" not in st.session_state: st.session_state.user_data = {}

if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "treino_ativo" not in st.session_state: st.session_state.treino_ativo = False
if "historico_cargas" not in st.session_state: st.session_state.historico_cargas = pd.DataFrame(columns=["Data", "Exercício", "Carga (kg)"])

# ==========================================
# 4. LIGAÇÃO À IA
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    pass # Falha silenciosa no login, avisa só lá dentro se houver erro.

# ==========================================
# 5. ECRÃ DE LOGIN (O PORTEIRO)
# ==========================================
if not st.session_state.logged_in:
    st.image("https://via.placeholder.com/800x200.png?text=STUDIO+AI+-+BETA", use_column_width=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="premium-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Acesso Reservado</h3>", unsafe_allow_html=True)
        
        user_input = st.text_input("Nome de Utilizador")
        pwd_input = st.text_input("Password", type="password")
        
        if st.button("Entrar na App"):
            if user_input in USERS_DB and USERS_DB[user_input]["pwd"] == pwd_input:
                st.session_state.logged_in = True
                st.session_state.username = user_input
                st.session_state.role = USERS_DB[user_input]["role"]
                st.session_state.user_data = USERS_DB[user_input]
                st.rerun()
            else:
                st.error("❌ Credenciais incorretas ou subscrição inativa.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop() # Pára a app aqui se não estiver logado

# ==========================================
# 6. HEADER & LOGOUT (UTILIZADOR LOGADO)
# ==========================================
st.image("https://via.placeholder.com/800x150.png?text=STUDIO+AI", use_column_width=True)
with st.sidebar:
    st.markdown(f"### 👤 Olá, {st.session_state.user_data['name']}")
    st.markdown(f"**Estatuto:** {'👑 Coach / Admin' if st.session_state.role == 'coach' else '🏅 Atleta Premium'}")
    st.markdown("---")
    if st.button("Terminar Sessão"):
        st.session_state.logged_in = False
        st.session_state.mensagens = []
        st.session_state.treino_ativo = False
        st.rerun()

# ==========================================
# 7. INTERFACE DO COACH (B2B)
# ==========================================
if st.session_state.role == "coach":
    tab_pt, tab_box, tab_tools = st.tabs(["🏋️ Gestão de Alunos (PT)", "🦍 Programação Box", "⚙️ Definições App"])
    
    with tab_pt:
        st.markdown("### 📋 Painel do Treinador Principal")
        st.caption("Gera treinos para os teus clientes e envia diretamente.")
        
        if not st.session_state.treino_ativo:
            with st.form("form_coach_pt"):
                # Filtra apenas os estudantes da base de dados
                lista_alunos = [v["name"] for k, v in USERS_DB.items() if v["role"] == "student"]
                aluno_sel = st.selectbox("Selecione o Aluno:", ["Aluno Externo (Novo)"] + lista_alunos)
                
                split = st.selectbox("Split Semanal:", ["1 Treino (Hoje)", "3x Fullbody", "4x Upper/Lower", "5x Bro Split"])
                notas_extra = st.text_input("Foco Específico (Ex: Focar glúteos e core):")
                
                if st.form_submit_button("Gerar Microciclo (Modo WhatsApp)"):
                    with st.spinner("A criar o plano..."):
                        prompt = f"""
                        És Head Coach. Cria treino para {aluno_sel}. Estrutura: {split}. Notas: {notas_extra}.
                        Dá-me o plano diretamente em formato MENSAGEM WHATSAPP limpo com Emojis. Sem tabelas.
                        """
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                        st.session_state.treino_ativo = True
                        st.rerun()
        else:
            st.success("✅ Plano gerado!")
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Voltar ao Painel de Alunos"):
                st.session_state.treino_ativo = False
                st.rerun()

    with tab_box:
        st.markdown("### 🦍 O Laboratório da Box")
        if not st.session_state.treino_ativo:
            with st.form("form_box"):
                ciclo = st.selectbox("Duração:", ["1 Dia", "1 Semana", "1 Mês"])
                foco = st.selectbox("Foco:", ["General Physical Preparedness (GPP)", "Strength Bias", "Engine Bias"])
                if st.form_submit_button("Gerar Programação de Grupo"):
                    with st.spinner("A periodizar a Box..."):
                        prompt = f"És um programador de elite CrossFit. Cria ciclo de {ciclo}. Foco: {foco}. Estrutura: Warmup, Força (RX/Scaled), WOD (RX/Scaled)."
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                        st.session_state.treino_ativo = True
                        st.rerun()
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Limpar Planeamento Box"):
                st.session_state.treino_ativo = False
                st.rerun()
                
    with tab_tools:
        st.info("Aqui no futuro poderás adicionar/remover utilizadores, ver quem tem pagamentos em atraso e ajustar as regras gerais da tua IA.")

# ==========================================
# 8. INTERFACE DO ALUNO (B2C)
# ==========================================
elif st.session_state.role == "student":
    tab_treino, tab_chat, tab_diario = st.tabs(["⚡ O Meu Treino", "💬 Coach Virtual", "📈 O Meu Diário"])
    
    with tab_treino:
        st.markdown(f"### Bem-vindo de volta, {st.session_state.user_data['name'].split()[0]}!")
        st.caption("O teu treino de hoje, ajustado ao teu corpo e objetivos.")
        
        if not st.session_state.treino_ativo:
            st.markdown('<div class="premium-box">', unsafe_allow_html=True)
            st.write(f"🎯 **O teu Objetivo:** {st.session_state.user_data['obj']}")
            st.write(f"🛡️ **As tuas Restrições:** {st.session_state.user_data['lesoes']}")
            
            tempo = st.slider("Quanto tempo tens para treinar hoje (min)?", 20, 90, 45)
            foco_hoje = st.selectbox("O que queres treinar hoje?", ["Treino Completo (Fullbody)", "Membros Superiores", "Membros Inferiores", "Core e Cardio"])
            
            if st.button("🔥 Gerar o meu Treino de Hoje"):
                with st.spinner("A preparar a tua sessão..."):
                    prompt = f"""
                    És um PT IA altamente motivador de uma App Premium. 
                    Cliente: {st.session_state.user_data['name']}. Nível: {st.session_state.user_data['nivel']}. 
                    Objetivo: {st.session_state.user_data['obj']}. Lesões a proteger: {st.session_state.user_data['lesoes']}.
                    Cria um treino de {tempo} minutos focado em {foco_hoje}.
                    Sê encorajador. Mostra a estrutura do treino em blocos limpos. Inclui links do YouTube "Ver Execução" para cada movimento.
                    """
                    st.session_state.mensagens = [{"role": "system", "content": prompt}]
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                    st.session_state.treino_ativo = True
                    st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            st.markdown("---")
            if st.button("✅ Concluir Treino"):
                st.balloons()
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

    with tab_chat:
        st.markdown("### 💬 Dúvidas no Treino?")
        st.caption("A máquina X está ocupada? Sentes alguma dor? O Coach AI resolve na hora.")
        if len(st.session_state.mensagens) == 0:
            st.info("Gera o teu treino primeiro para podermos falar sobre ele.")
        else:
            for msg in st.session_state.mensagens:
                if msg["role"] != "system":
                    with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            chat_input = st.chat_input("Ex: Troca o supino por halteres...")
            if chat_input:
                st.session_state.mensagens.append({"role": "user", "content": chat_input})
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.rerun()

    with tab_diario:
        st.markdown("### 📈 Recordes Pessoais")
        col1, col2 = st.columns([1, 1.5])
        with col1:
            ex = st.text_input("Exercício:")
            carga = st.number_input("Carga (kg):", min_value=0.0, step=1.0)
            if st.button("💾 Guardar PR"):
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m/%Y"), "Exercício": ex, "Carga": carga}])
                st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, novo], ignore_index=True)
                st.success("Guardado!")
        with col2:
            if not st.session_state.historico_cargas.empty:
                st.dataframe(st.session_state.historico_cargas, use_container_width=True)
