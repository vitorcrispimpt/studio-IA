import streamlit as st
from openai import OpenAI
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# ==========================================
# 1. LIGAÇÃO AO COFRE (SUPABASE)
# ==========================================
# Certifica-te que estas chaves estão nos Secrets do Streamlit
url: str = st.secrets["SUPABASE_URL"]
key: str = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(url, key)

# ==========================================
# 2. CONFIGURAÇÃO PREMIUM & UI (ESTILO APPLE/ELITE)
# ==========================================
st.set_page_config(page_title="Studio AI - Elite Pro", page_icon="⚡", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #F8F9FA; } 
    .stTabs [data-baseweb="tab-list"] { gap: 24px; border-bottom: 1px solid #ddd; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; color: #444; padding: 10px 20px; }
    .stTabs [data-baseweb="tab--active"] { color: #000; border-bottom: 2px solid #000; }
    
    h1, h2, h3 { color: #111 !important; font-family: 'Inter', sans-serif; }
    
    .stButton>button {
        background-color: #000000; color: #FFFFFF; border-radius: 12px;
        padding: 14px 28px; border: none; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #333333; box-shadow: 0px 8px 20px rgba(0, 0, 0, 0.15);
    }
    
    .premium-box {
        background-color: #FFFFFF; padding: 35px; border-radius: 20px;
        border: 1px solid #EAEAEA; box-shadow: 0px 10px 40px rgba(0,0,0,0.04); margin-bottom: 25px;
    }
    .calc-box {
        background-color: #FFFFFF; padding: 25px; border-radius: 15px;
        border: 1px solid #EEE; margin-bottom: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 3. DICIONÁRIOS DE REFERÊNCIA (BENCHMARKS)
# ==========================================
BENCHMARKS = {
    "Nenhum": "Selecione para ver a referência...",
    "Fran (CrossFit)": "21-15-9 reps: Thrusters (43/30kg) e Pull-ups.",
    "Murph (CrossFit)": "1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run (Colete 9/6kg).",
    "Hyrox Half-Sim": "1km Run, 1000m Ski, 1km Run, 50m Sled Push, 1km Run, 50m Sled Pull, 1km Run, 80m Burpee Broad Jumps.",
    "Hyrox Engine Test": "AMRAP 20m: 1000m Run, 500m Row, 50 Wall Balls.",
    "5K Run (Corrida)": "Distância: 5.000 metros (Teste de Limiar Aeróbico)."
}

# ==========================================
# 4. ESTADOS DE SESSÃO
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_data" not in st.session_state: st.session_state.user_data = {}
if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "treino_ativo" not in st.session_state: st.session_state.treino_ativo = False

# LIGAÇÃO À IA (OPENAI)
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

# ==========================================
# 5. SISTEMA DE LOGIN (CONSULTA SUPABASE)
# ==========================================
if not st.session_state.logged_in:
    st.image("https://via.placeholder.com/1000x250.png?text=STUDIO+AI+-+SISTEMA+DE+GEST%C3%83O+ELITE", use_column_width=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col_l1, col_l2, col_l3 = st.columns([1, 1.5, 1])
    with col_l2:
        st.markdown('<div class="premium-box">', unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Acesso à Plataforma</h3>", unsafe_allow_html=True)
        
        u_in = st.text_input("Username").lower().strip()
        p_in = st.text_input("Password", type="password")
        
        if st.button("Entrar"):
            # Verifica na tabela app_users do Supabase
            login_res = supabase.table("app_users").select("*").eq("username", u_in).eq("pwd", p_in).execute()
            
            if len(login_res.data) > 0:
                st.session_state.logged_in = True
                st.session_state.user_data = login_res.data[0]
                st.rerun()
            else:
                st.error("Credenciais inválidas. Verifica os dados ou a tua subscrição.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 6. LAYOUT PRINCIPAL (LOGADO)
# ==========================================
st.sidebar.image("https://via.placeholder.com/300x100.png?text=STUDIO+AI", use_container_width=True)
st.sidebar.markdown(f"### Bem-vindo, {st.session_state.user_data['name']}")
st.sidebar.markdown(f"**Perfil:** {'Coach Principal' if st.session_state.user_data['role'] == 'coach' else 'Atleta Premium'}")

if st.sidebar.button("Terminar Sessão"):
    st.session_state.logged_in = False
    st.session_state.user_data = {}
    st.session_state.mensagens = []
    st.session_state.treino_ativo = False
    st.rerun()

# ==============================================================================
# 7. MODO COACH (CENTRO DE COMANDO B2B)
# ==============================================================================
if st.session_state.user_data['role'] == 'coach':
    tab_box, tab_pt, tab_chat, tab_ferramentas = st.tabs([
        "🦍 Programação Box / Hyrox", "🏋️ Gestão Alunos PT", "💬 Chat Coach AI", "📊 Gestão & Ferramentas"
    ])
    
    # --- ABA 1: PROGRAMAÇÃO BOX ---
    with tab_box:
        st.markdown("### 🦍 Programação de Grupo (CrossFit / Hyrox)")
        if not st.session_state.treino_ativo:
            with st.expander("🏆 Ver Benchmarks de Referência"):
                bench_sel = st.selectbox("Consulta rápida:", list(BENCHMARKS.keys()))
                if bench_sel != "Nenhum": st.info(f"**{bench_sel}:** {BENCHMARKS[bench_sel]}")
            
            with st.form("form_box"):
                c1, c2 = st.columns(2)
                with c1:
                    ciclo = st.selectbox("Duração:", ["Hoje", "1 Semana", "1 Mês"])
                    foco = st.selectbox("Foco Principal:", ["Geral", "Força", "Ginástica", "Hyrox", "Endurance"])
                with c2:
                    estilo = st.selectbox("Estilo:", ["Inovador", "Teste Mental", "Técnico", "Clássico"])
                
                hist = st.text_area("📋 Histórico Anterior (Cola aqui os treinos passados):", placeholder="Ex: Semana passada focámos em Back Squats e Sled Pulls...")
                regras = st.text_input("Regras Específicas:", placeholder="Ex: Sem saltos à corda; Foco em técnica de Snatch.")
                
                if st.form_submit_button("Gerar Programação de Elite"):
                    with st.spinner("A periodizar..."):
                        p_hist = f"Análise do histórico: {hist}. Garante progressão." if hist else ""
                        prompt = f"És Head Coach. Cria {ciclo} de treino. Foco: {foco}. Estilo: {estilo}. {p_hist} Regras: {regras}."
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt}])
                        st.session_state.mensagens = [{"role": "assistant", "content": res.choices[0].message.content}]
                        st.session_state.treino_ativo = True
                        
                        # Grava LOG no Supabase
                        supabase.table("logs_treino").insert({"username": "coach", "tipo_treino": f"Box {foco}", "plano_gerado": res.choices[0].message.content}).execute()
                        st.rerun()
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("Criar Nova Programação"):
                st.session_state.treino_ativo = False
                st.rerun()

    # --- ABA 2: PT PERSONALIZADO ---
    with tab_pt:
        st.markdown("### 🏋️ Personal Training: Gestão de Microciclos")
        if not st.session_state.treino_ativo:
            # Vai buscar alunos reais à DB
            alunos_res = supabase.table("app_users").select("*").eq("role", "student").execute()
            nomes_db = [a['name'] for a in alunos_res.data]
            
            with st.form("form_pt"):
                aluno_sel = st.selectbox("Selecionar Aluno da Base de Dados:", ["Externo"] + nomes_db)
                
                # Dados padrão para aluno externo
                obj_f, les_f, niv_f, u_f = "", "", "Intermédio", ""
                if aluno_sel != "Externo":
                    for a in alunos_res.data:
                        if a['name'] == aluno_sel:
                            obj_f, les_f, niv_f, u_f = a['obj'], a['lesoes'], a['nivel'], a['username']

                c_pt1, c_pt2 = st.columns(2)
                with c_pt1:
                    objetivo = st.text_input("Objetivo:", value=obj_f)
                    split = st.selectbox("Split Semanal:", ["1 Treino", "3x Fullbody", "4x Upper/Lower", "Atleta Híbrido"])
                with c_pt2:
                    nivel = st.selectbox("Nível:", ["Iniciante", "Intermédio", "Avançado"], index=1)
                    duracao = st.slider("Minutos:", 30, 90, 60)
                
                lesoes_pt = st.text_area("Restrições:", value=les_f)
                
                if st.form_submit_button("Gerar Microciclo (Formato WhatsApp)"):
                    with st.spinner("A desenhar plano..."):
                        prompt = f"És PT. Aluno: {aluno_sel}. Objetivo: {objetivo}. Split: {split}. Lesões: {lesoes_pt}. Formato: WhatsApp com Emojis."
                        res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt}])
                        st.session_state.mensagens = [{"role": "assistant", "content": res.choices[0].message.content}]
                        st.session_state.treino_ativo = True
                        
                        if u_f: # Se aluno registado, guarda log para ele
                            supabase.table("logs_treino").insert({"username": u_f, "tipo_treino": f"PT {split}", "plano_gerado": res.choices[0].message.content}).execute()
                        st.rerun()
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("Planear Outro Aluno"):
                st.session_state.treino_ativo = False
                st.rerun()

    # --- ABA 3: CHAT AI COACH ---
    with tab_chat:
        st.markdown("### 💬 Assistente Inteligente do Coach")
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        c_in = st.chat_input("Pede ajustes ou dicas técnicas...")
        if c_in:
            st.session_state.mensagens.append({"role": "user", "content": c_in})
            res = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
            st.session_state.mensagens.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

    # --- ABA 4: FERRAMENTAS COACH ---
    with tab_ferramentas:
        col_f1, col_f2 = st.columns(2)
        with col_f1:
            st.markdown("#### 🧮 Calculadora 1RM")
            rm_val = st.number_input("Carga Máxima (kg):", value=100.0, step=2.5)
            percs = [50, 60, 70, 75, 80, 85, 90, 95]
            st.table(pd.DataFrame({"%": [f"{p}%" for p in percs], "Carga": [f"{rm_val*(p/100):.1f} kg" for p in percs]}))
        with col_f2:
            st.markdown("#### 👥 Alunos Registados")
            all_u = supabase.table("app_users").select("name, username, obj, nivel").eq("role", "student").execute()
            if all_u.data: st.dataframe(pd.DataFrame(all_u.data), use_container_width=True)

# ==============================================================================
# 8. MODO ALUNO (EXPERIÊNCIA PREMIUM B2C)
# ==============================================================================
elif st.session_state.user_data['role'] == 'student':
    t_al1, t_al2, t_al3 = st.tabs(["⚡ Treinar Agora", "💬 Coach AI", "📈 O Meu Diário"])
    
    # --- TREINO ALUNO ---
    with t_al1:
        st.markdown(f"### Olá {st.session_state.user_data['name']}! Prisioneiro do ferro hoje?")
        if not st.session_state.treino_ativo:
            st.markdown(f'<div class="premium-box"><b>Objetivo:</b> {st.session_state.user_data["obj"]}<br><b>Saúde:</b> {st.session_state.user_data["lesoes"]}</div>', unsafe_allow_html=True)
            
            tipo = st.radio("O que vamos atacar?", ["🏋️ Musculação", "🦍 CrossFit", "🎿 Hyrox", "🏃 Corrida"])
            tempo = st.slider("Tempo disponível (min):", 20, 90, 45)
            
            detalhe = ""
            if tipo == "🏋️ Musculação": detalhe = st.selectbox("Foco:", ["Fullbody", "Superior", "Inferior", "Cardio/Core"])
            elif tipo == "🎿 Hyrox": detalhe = st.selectbox("Foco:", ["Simulação", "Estações", "Corrida Comprometida"])
            elif tipo == "🏃 Corrida": detalhe = st.selectbox("Tipo:", ["Zona 2 (Leve)", "Intervalos", "Tempo Run"])
            
            if st.button("🔥 Gerar Treino"):
                with st.spinner("A ligar os motores..."):
                    prompt = f"És PT. Aluno: {st.session_state.user_data['name']}. Objetivo: {st.session_state.user_data['obj']}. Lesões: {st.session_state.user_data['lesoes']}. Tipo: {tipo} ({detalhe}). Tempo: {tempo}m."
                    res = client.chat.completions.create(model="gpt-4o-mini", messages=[{"role": "system", "content": prompt}])
                    st.session_state.mensagens = [{"role": "assistant", "content": res.choices[0].message.content}]
                    st.session_state.treino_ativo = True
                    
                    # LOG
                    supabase.table("logs_treino").insert({"username": st.session_state.user_data['username'], "tipo_treino": tipo, "foco": detalhe, "plano_gerado": res.choices[0].message.content}).execute()
                    st.rerun()
        else:
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("✅ Treino Concluído!"):
                st.balloons()
                st.session_state.treino_ativo = False
                st.rerun()

    # --- CHAT ALUNO ---
    with t_al2:
        st.markdown("### 💬 Dúvidas ou Ajustes?")
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        chat_in = st.chat_input("Ex: Não tenho barra, o que faço?")
        if chat_in:
            st.session_state.mensagens.append({"role": "user", "content": chat_in})
            res = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
            st.session_state.mensagens.append({"role": "assistant", "content": res.choices[0].message.content})
            st.rerun()

    # --- DIÁRIO ALUNO ---
    with t_al3:
        st.markdown("### 📈 Recordes e Progressão")
        col_d1, col_d2 = st.columns([1, 1.2])
        with col_d1:
            st.markdown("#### 🥇 Novo Recorde")
            ex_n = st.text_input("Exercício/Prova:")
            val_n = st.text_input("Resultado (kg ou Tempo):")
            cat_n = st.radio("Tipo:", ["Peso", "Tempo/Prova"], horizontal=True)
            if st.button("💾 Registar PR"):
                supabase.table("prs").insert({"username": st.session_state.user_data['username'], "data": datetime.now().strftime("%d/%m/%Y"), "exercicio": ex_n, "carga": val_n, "tipo": cat_n}).execute()
                st.success("Imortalizado!")
        
        with col_d2:
            st.markdown("#### 🏆 Histórico")
            prs_db = supabase.table("prs").select("*").eq("username", st.session_state.user_data['username']).execute()
            if prs_db.data:
                df_p = pd.DataFrame(prs_db.data)
                
                # Gráfico de Pesos
                df_w = df_p[df_p['tipo'] == 'Peso']
                if not df_w.empty:
                    df_w['val_num'] = df_w['carga'].str.extract('(\d+)').astype(float)
                    ex_sel = st.selectbox("Ver Gráfico de:", df_w['exercicio'].unique())
                    st.line_chart(df_w[df_w['exercicio'] == ex_sel].set_index('data')['val_num'])
                
                # Tabela de Tempos
                df_t = df_p[df_p['tipo'] == 'Tempo/Prova']
                if not df_t.empty: st.table(df_t[['data', 'exercicio', 'carga']].rename(columns={'carga': 'Tempo'}))
