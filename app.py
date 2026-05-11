import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# ==========================================
# 1. LIGAÇÃO AO COFRE (SUPABASE)
# ==========================================
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. CONFIGURAÇÃO PREMIUM & UI
# ==========================================
st.set_page_config(page_title="Studio AI - Elite", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; } 
    .stTabs [data-baseweb="tab-list"] { gap: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; color: #333; }
    h1, h2, h3 { color: #111 !important; }
    
    .stButton>button {
        background-color: #000000; color: #FFFFFF; border-radius: 10px;
        padding: 12px 24px; border: none; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #333333; color: white; box-shadow: 0px 4px 15px rgba(0, 0, 0, 0.2);
    }
    .premium-box {
        background-color: #FFFFFF; padding: 30px; border-radius: 16px;
        border: 1px solid #EAEAEA; box-shadow: 0px 10px 30px rgba(0,0,0,0.05); margin-bottom: 20px;
    }
    .calc-box {
        background-color: #FFFFFF; padding: 20px; border-radius: 12px;
        border: 1px solid #E0E0E0; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

BENCHMARKS = {
    "Nenhum": "Selecione um Teste para ver a referência...",
    "Fran (CrossFit)": "21-15-9 reps: Thrusters (43/30kg) and Pull-ups.",
    "Murph (CrossFit)": "1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run.",
    "Hyrox Half-Sim": "1km Run, 1000m Ski, 1km Run, 50m Sled Push, 1km Run, 50m Sled Pull, 1km Run, 80m Burpee Broad Jumps.",
    "Hyrox Engine Test": "AMRAP 20m: 1000m Run, 500m Row, 50 Wall Balls.",
    "5K Run (Corrida)": "Distância: 5.000 metros o mais rápido possível."
}

# ==========================================
# 3. MEMÓRIA DE SESSÃO
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "treino_ativo" not in st.session_state: st.session_state.treino_ativo = False

# LIGAÇÃO À IA
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    pass 

# ==========================================
# 4. ECRÃ DE LOGIN (VERIFICAÇÃO NA BASE DE DADOS)
# ==========================================
if not st.session_state.logged_in:
    st.image("https://via.placeholder.com/800x200.png?text=STUDIO+AI+-+ELITE+DB", use_column_width=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div class="premium-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Acesso Reservado</h3>", unsafe_allow_html=True)
        
        user_input = st.text_input("Nome de Utilizador").lower().strip()
        pwd_input = st.text_input("Password", type="password")
        
        if st.button("Entrar na App"):
            # VAI AO SUPABASE VERIFICAR SE O USER EXISTE
            res = supabase.table("app_users").select("*").eq("username", user_input).eq("pwd", pwd_input).execute()
            
            if len(res.data) > 0:
                st.session_state.logged_in = True
                st.session_state.user_data = res.data[0] # Guarda todos os dados do aluno vindos da DB
                st.rerun()
            else:
                st.error("❌ Credenciais incorretas ou utilizador inexistente.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 5. HEADER & LOGOUT
# ==========================================
st.image("https://via.placeholder.com/1200x150.png?text=STUDIO+AI", use_column_width=True)
with st.sidebar:
    st.markdown(f"### 👤 Olá, {st.session_state.user_data['name']}")
    st.markdown(f"**Estatuto:** {'👑 Coach / Admin' if st.session_state.user_data['role'] == 'coach' else '🏅 Atleta Premium'}")
    st.markdown("---")
    if st.button("Terminar Sessão"):
        st.session_state.logged_in = False
        st.session_state.mensagens = []
        st.session_state.treino_ativo = False
        st.session_state.user_data = {}
        st.rerun()

# ==============================================================================
# 6. INTERFACE DO COACH (100% RESTAURADA + SUPABASE)
# ==============================================================================
if st.session_state.user_data['role'] == 'coach':
    tab_box, tab_pt, tab_chat, tab_ferramentas = st.tabs([
        "🦍 Programação Box / Hyrox", "🏋️ PT Personalizado", "💬 Chat AI", "🧮 Ferramentas Coach"
    ])
    
    with tab_box:
        st.markdown("### 🦍 Programação Interna: Box & Hyrox")
        st.caption("Gera periodizações precisas com análise de histórico.")
        
        if not st.session_state.treino_ativo:
            with st.expander("🏆 Referência: Benchmarks e Provas"):
                selecao_bench = st.selectbox("Consulta rápida:", list(BENCHMARKS.keys()))
                if selecao_bench != "Nenhum": st.info(f"**{selecao_bench}:** {BENCHMARKS[selecao_bench]}")
            
            with st.form("form_box_pro"):
                colA, colB = st.columns(2)
                with colA:
                    ciclo = st.selectbox("Duração a Gerar:", ["1 Aula (Hoje)", "1 Semana (Seg-Sáb)", "1 Mês (Periodização)"])
                    foco_box = st.selectbox("Foco Principal:", ["Geral (Equilibrado)", "Força Base", "Ginástica", "Hyrox (Corrida + Estações)", "Endurance Pura"])
                with colB:
                    estilo_wod = st.selectbox("Estilo do WOD:", [
                        "🌶️ Inovador & Fora da Caixa", "🔥 Teste Mental / Grit", "🛠️ Técnico e Tático / Pacing", "🧱 Clássico e Direto"
                    ])

                historico_programacao = st.text_area("📋 Cola a Programação do Ciclo Anterior (A IA vai ler para evoluir):", height=100)
                regras = st.text_area("Regras Específicas do Coach:")
                
                if st.form_submit_button("🔥 Gerar Progressão & Programação"):
                    with st.spinner("A invocar a mente de um Elite Coach..."):
                        texto_historico = f"\n=== HISTÓRICO ANTERIOR ===\n{historico_programacao}\nCRIA O PRÓXIMO CICLO COM CONTINUIDADE.\n===================" if historico_programacao.strip() else ""
                        texto_regras = f"\nREGRAS: {regras}" if regras.strip() else ""
                        prompt = f"""
                        És Head Coach de CrossFit e Hyrox. Missão: {ciclo}. Foco: {foco_box}. Estilo: {estilo_wod}.
                        {texto_historico}{texto_regras}
                        Estrutura Diária (50m): Warm-up (10m), Skill/Força (15m - RX/Scaled), WOD (15m-20m - RX/Scaled/Cap), Cooldown (5m).
                        """
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        plano_gerado = response.choices[0].message.content
                        st.session_state.mensagens.append({"role": "assistant", "content": plano_gerado})
                        st.session_state.treino_ativo = True
                        
                        # GUARDAR NA BASE DE DADOS (LOGS)
                        supabase.table("logs_treino").insert({
                            "username": st.session_state.user_data['username'],
                            "tipo_treino": "Programação Box - " + foco_box,
                            "plano_gerado": plano_gerado
                        }).execute()
                        st.rerun()
        else:
            st.success("✅ Programação gerada e guardada com sucesso!")
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Fazer Nova Programação"):
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

    with tab_pt:
        st.markdown("### 📋 Gerador de Microciclos (PT)")
        if not st.session_state.treino_ativo:
            with st.form("form_coach_pt"):
                # Vai buscar a lista de alunos REAIS à base de dados
                alunos_db = supabase.table("app_users").select("*").eq("role", "student").execute()
                nomes_db = [a['name'] for a in alunos_db.data]
                
                aluno_sel = st.selectbox("🗂️ Selecionar Aluno da BD:", ["Aluno Externo (Novo)"] + nomes_db)
                
                obj_default = ""
                lesao_default = ""
                nivel_default = "Intermédio"
                username_aluno_selecionado = ""
                
                if aluno_sel != "Aluno Externo (Novo)":
                    for a in alunos_db.data:
                        if a["name"] == aluno_sel:
                            obj_default = a["obj"]
                            lesao_default = a["lesoes"]
                            nivel_default = a["nivel"] if a["nivel"] else "Intermédio"
                            username_aluno_selecionado = a["username"]
                
                col1, col2 = st.columns(2)
                with col1:
                    objetivo = st.text_input("Objetivo:", value=obj_default)
                    split = st.selectbox("Divisão (Split):", ["1 Treino Único", "3x (Fullbody)", "4x (Upper/Lower)", "Atleta Híbrido (Força + Corrida)"])
                with col2:
                    nivel = st.selectbox("Nível:", ["Iniciante", "Intermédio", "Avançado"], index=["Iniciante", "Intermédio", "Avançado"].index(nivel_default))
                    duracao = st.slider("Duração por treino (min):", 30, 120, 60)
                
                lesoes = st.text_area("Restrições:", value=lesao_default)
                
                if st.form_submit_button("🚀 Gerar Microciclo (Modo WhatsApp)"):
                    with st.spinner("A desenhar a arquitetura..."):
                        prompt = f"""
                        És o PT principal. Aluno: {aluno_sel}. Obj: {objetivo}. Nível: {nivel}. Restrições: {lesoes}. Split: {split}. Duração: {duracao}m.
                        PARTE 1: Visão do Coach.
                        PARTE 2: Formato limpo para WHATSAPP (Emojis, listas simples, sem tabelas). 
                        """
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        plano_gerado = response.choices[0].message.content
                        st.session_state.mensagens.append({"role": "assistant", "content": plano_gerado})
                        st.session_state.treino_ativo = True
                        
                        # Guardar no perfil do aluno na BD, se for aluno registado
                        if username_aluno_selecionado:
                            supabase.table("logs_treino").insert({
                                "username": username_aluno_selecionado,
                                "tipo_treino": "Microciclo PT - " + split,
                                "plano_gerado": plano_gerado
                            }).execute()
                            
                        st.rerun()
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Planear Outro Aluno"):
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

    with tab_chat:
        st.markdown("### 💬 Chat com o Assistente do Coach")
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        chat_input = st.chat_input("Pede ajustes...")
        if chat_input:
            st.session_state.mensagens.append({"role": "user", "content": chat_input})
            with st.chat_message("user"): st.markdown(chat_input)
            with st.chat_message("assistant"):
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.markdown(response.choices[0].message.content)
            st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})

    with tab_ferramentas:
        col_calc, col_graph = st.columns([1, 1.2])
        with col_calc:
            st.markdown("### 🧮 Calculadora 1RM")
            st.markdown('<div class="calc-box">', unsafe_allow_html=True)
            rm_valor = st.number_input("1RM (kg):", min_value=0.0, step=2.5, value=100.0)
            percentagens = [50, 60, 70, 75, 80, 85, 90, 95]
            st.table(pd.DataFrame({"%": [f"{p}%" for p in percentagens], "Carga": [f"{rm_valor * (p/100):.1f} kg" for p in percentagens]}))
            st.markdown('</div>', unsafe_allow_html=True)
        with col_graph:
            st.markdown("### 📋 Alunos na Base de Dados")
            alunos_res = supabase.table("app_users").select("*").eq("role", "student").execute()
            if alunos_res.data:
                df_alunos = pd.DataFrame(alunos_res.data)
                st.dataframe(df_alunos[["name", "username", "obj", "nivel"]], use_container_width=True)

# ==============================================================================
# 7. INTERFACE DO ALUNO (HÍBRIDO + DIÁRIO LIGADO AO SUPABASE)
# ==============================================================================
elif st.session_state.user_data['role'] == 'student':
    tab_treino, tab_chat, tab_diario = st.tabs(["⚡ O Meu Treino", "💬 Coach Virtual", "📈 Diário & Calculadoras"])
    
    with tab_treino:
        st.markdown(f"### Esmaga o dia, {st.session_state.user_data['name'].split()[0]}! 🔥")
        
        if not st.session_state.treino_ativo:
