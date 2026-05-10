import streamlit as st
from openai import OpenAI
from datetime import datetime
import pandas as pd

# ==========================================
# 1. CONFIGURAÇÃO PREMIUM & UI
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

# ==========================================
# 2. BASE DE DADOS SIMULADA (O "COFRE" DA APP)
# ==========================================
USERS_DB = {
    "coach": {"pwd": "admin", "role": "coach", "name": "Head Coach", "obj": "", "nivel": "", "lesoes": ""},
    "joao": {"pwd": "123", "role": "student", "name": "João Silva", "obj": "Massa Muscular", "nivel": "Intermédio", "lesoes": "Dor no ombro direito (evitar overhead pesado)"},
    "maria": {"pwd": "abc", "role": "student", "name": "Maria Santos", "obj": "Perda de Peso", "nivel": "Iniciante", "lesoes": "Lombar sensível, evitar peso morto pesado"}
}

BENCHMARKS = {
    "Nenhum": "Selecione um WOD Clássico para ver a referência...",
    "Fran": "21-15-9 reps for time: Thrusters (43/30kg) and Pull-ups.",
    "Murph": "For time: 1.6km Run, 100 Pull-ups, 200 Push-ups, 300 Squats, 1.6km Run.",
    "Cindy": "AMRAP 20 min: 5 Pull-ups, 10 Push-ups, 15 Air Squats."
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
    pass # Falha silenciosa no login

# ==========================================
# 5. ECRÃ DE LOGIN (O PORTEIRO)
# ==========================================
if not st.session_state.logged_in:
    st.image("https://via.placeholder.com/800x200.png?text=STUDIO+AI+-+ELITE", use_column_width=True)
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
                st.error("❌ Credenciais incorretas.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# 6. HEADER & LOGOUT
# ==========================================
st.image("https://via.placeholder.com/1200x150.png?text=STUDIO+AI", use_column_width=True)
with st.sidebar:
    st.markdown(f"### 👤 Olá, {st.session_state.user_data['name']}")
    st.markdown(f"**Estatuto:** {'👑 Coach / Admin' if st.session_state.role == 'coach' else '🏅 Atleta Premium'}")
    st.markdown("---")
    if st.button("Terminar Sessão"):
        st.session_state.logged_in = False
        st.session_state.mensagens = []
        st.session_state.treino_ativo = False
        st.rerun()

# ==============================================================================
# 7. INTERFACE DO COACH (RESTAURO TOTAL DO BACKOFFICE)
# ==============================================================================
if st.session_state.role == "coach":
    tab_box, tab_pt, tab_chat, tab_ferramentas = st.tabs([
        "🦍 Programação Box", "🏋️ PT Personalizado", "💬 Chat AI", "🧮 Ferramentas"
    ])
    
    # --- TAB: CROSSFIT BOX ---
    with tab_box:
        st.markdown("### 🦍 Programação Interna da Box")
        st.caption("Gera periodizações precisas para as aulas de grupo com análise de histórico.")
        
        if not st.session_state.treino_ativo:
            with st.expander("🏆 Referência: Benchmarks e Hero WODs"):
                selecao_bench = st.selectbox("Consulta rápida:", list(BENCHMARKS.keys()))
                if selecao_bench != "Nenhum": st.info(f"**{selecao_bench}:** {BENCHMARKS[selecao_bench]}")
            
            with st.form("form_box_pro"):
                colA, colB = st.columns(2)
                with colA:
                    ciclo = st.selectbox("Duração a Gerar:", ["1 Aula (Hoje)", "1 Semana (Seg-Sáb)", "1 Mês (Periodização)"])
                    foco_box = st.selectbox("Foco Principal:", ["Geral (Equilibrado)", "Força Base (Weightlifting)", "Ginástica", "Endurance (Cardio)"])
                with colB:
                    estilo_wod = st.selectbox("Estilo do WOD:", [
                        "🌶️ Inovador & Fora da Caixa", "🔥 Teste Mental / Grit", "🛠️ Técnico e Tático", "🧱 Clássico e Direto"
                    ])

                historico_programacao = st.text_area("📋 Cola a Programação do Ciclo Anterior (A IA vai ler para evoluir):", height=100)
                regras = st.text_area("Regras Específicas do Coach (Ex: Sem saltos à corda esta semana):")
                
                if st.form_submit_button("🔥 Gerar Progressão & Programação"):
                    with st.spinner("A invocar a mente do Dave Castro para criar a periodização..."):
                        texto_historico = f"\n=== HISTÓRICO ANTERIOR ===\n{historico_programacao}\nCRIA O PRÓXIMO CICLO COM CONTINUIDADE LÓGICA.\n===================" if historico_programacao.strip() else ""
                        texto_regras = f"\nREGRAS: {regras}" if regras.strip() else ""
                        prompt = f"""
                        És Head Coach de CrossFit. Missão: {ciclo}. Foco: {foco_box}. Estilo: {estilo_wod}.
                        {texto_historico}{texto_regras}
                        Estrutura Diária (50m): Warm-up (10m), Skill/Força (15m - RX/Scaled), WOD (15m-20m - RX/Scaled/Time Cap), Cooldown (5m).
                        Justifica a tua periodização.
                        """
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                        st.session_state.treino_ativo = True
                        st.rerun()
        else:
            st.success("✅ Programação da Box gerada com sucesso!")
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Concluir e Fazer Nova Programação"):
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

    # --- TAB: PT PERSONALIZADO ---
    with tab_pt:
        st.markdown("### 📋 Gerador de Microciclos (PT)")
        st.caption("Cria semanas completas prontas a colar no WhatsApp do teu aluno.")
        
        if not st.session_state.treino_ativo:
            with st.form("form_coach_pt"):
                lista_alunos = {k: v for k, v in USERS_DB.items() if v["role"] == "student"}
                opcoes_alunos = ["Aluno Externo (Novo)"] + [v["name"] for k, v in lista_alunos.items()]
                aluno_sel = st.selectbox("🗂️ Selecionar Aluno:", opcoes_alunos)
                
                # Se for aluno da BD, vai buscar os dados, se não, deixa em branco
                obj_default = ""
                lesao_default = ""
                if aluno_sel != "Aluno Externo (Novo)":
                    for k, v in lista_alunos.items():
                        if v["name"] == aluno_sel:
                            obj_default = v["obj"]
                            lesao_default = v["lesoes"]
                
                col1, col2 = st.columns(2)
                with col1:
                    objetivo = st.text_input("Objetivo:", value=obj_default)
                    split = st.selectbox("Divisão (Split):", ["1 Treino Único", "3x (Fullbody)", "4x (Upper/Lower)", "5x (Bro Split)", "6x (PPL)"])
                with col2:
                    nivel = st.selectbox("Nível:", ["Iniciante", "Intermédio", "Avançado"])
                    duracao = st.slider("Duração por treino (min):", 30, 120, 60)
                
                lesoes = st.text_area("Restrições:", value=lesao_default)
                
                if st.form_submit_button("🚀 Gerar Microciclo (Modo WhatsApp)"):
                    with st.spinner("A desenhar a arquitetura..."):
                        prompt = f"""
                        És o PT principal da Box. Aluno: {aluno_sel}. Obj: {objetivo}. Nível: {nivel}. Restrições: {lesoes}. Split: {split}. Duração: {duracao}m.
                        PARTE 1: Visão do Coach (breve justificação biomecânica).
                        PARTE 2: Formato limpo e pronto a copiar para WHATSAPP (com Emojis, listas de texto simples, sem tabelas).
                        """
                        st.session_state.mensagens = [{"role": "system", "content": prompt}]
                        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                        st.session_state.treino_ativo = True
                        st.rerun()
        else:
            st.success("✅ Microciclo gerado!")
            st.markdown(st.session_state.mensagens[-1]["content"])
            if st.button("🔄 Planear Outro Aluno"):
                st.session_state.treino_ativo = False
                st.session_state.mensagens = []
                st.rerun()

    # --- TAB: CHAT AI & FERRAMENTAS ---
    with tab_chat:
        st.markdown("### 💬 Chat com o Assistente do Coach")
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]): st.markdown(msg["content"])
        
        chat_input = st.chat_input("Pede ajustes. Ex: Troca o WOD de terça por algo sem impacto...")
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
            st.markdown("### 📈 Diário de Recordes (Geral)")
            ex = st.text_input("Exercício:")
            carga = st.number_input("Carga (kg):", min_value=0.0, step=1.0)
            if st.button("💾 Guardar PR"):
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Exercício": ex, "Carga": carga}])
                st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, novo], ignore_index=True)
                st.success("Guardado!")
            if not st.session_state.historico_cargas.empty:
                filtro = st.selectbox("Ver evolução:", st.session_state.historico_cargas["Exercício"].unique())
                st.line_chart(st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == filtro].set_index("Data")["Carga"])

# ==============================================================================
# 8. INTERFACE DO ALUNO (COM OPÇÃO MUSCULAÇÃO vs CROSSFIT)
# ==============================================================================
elif st.session_state.role == "student":
    tab_treino, tab_chat, tab_diario = st.tabs(["⚡ O Meu Treino", "💬 Coach Virtual", "📈 O Meu Diário"])
    
    with tab_treino:
        st.markdown(f"### Bem-vindo de volta, {st.session_state.user_data['name'].split()[0]}!")
        st.caption("Gera a tua sessão diária baseada no teu perfil.")
        
        if not st.session_state.treino_ativo:
            st.markdown('<div class="premium-box">', unsafe_allow_html=True)
            st.write(f"🎯 **Objetivo:** {st.session_state.user_data['obj']} | 🛡️ **Atenção:** {st.session_state.user_data['lesoes']}")
            
            # A GRANDE NOVIDADE PARA O ALUNO: Escolher o tipo de treino!
            tipo_treino = st.radio("Que tipo de treino vais fazer hoje?", ["🏋️ Musculação / Estúdio", "🦍 WOD de CrossFit"])
            
            tempo = st.slider("Quanto tempo tens para treinar hoje (min)?", 20, 90, 45)
            
            foco_musculacao = "Treino Completo"
            if tipo_treino == "🏋️ Musculação / Estúdio":
                foco_musculacao = st.selectbox("Qual o foco do treino?", ["Treino Completo (Fullbody)", "Membros Superiores", "Membros Inferiores", "Core e Cardio"])
            
            if st.button("🔥 Gerar o meu Treino de Hoje"):
                with st.spinner("A preparar a tua sessão..."):
                    if tipo_treino == "🏋️ Musculação / Estúdio":
                        prompt = f"""
                        És o PT pessoal do aluno {st.session_state.user_data['name']}. Nível: {st.session_state.user_data['nivel']}. 
                        Objetivo: {st.session_state.user_data['obj']}. Lesões: {st.session_state.user_data['lesoes']}.
                        Cria um treino de MUSCULAÇÃO de {tempo} min focado em {foco_musculacao}.
                        Mostra a estrutura em blocos limpos com links do YouTube "Ver Execução".
                        """
                    else:
                        prompt = f"""
                        És o Head Coach de CrossFit do aluno {st.session_state.user_data['name']}. Nível: {st.session_state.user_data['nivel']}.
                        Objetivo: {st.session_state.user_data['obj']}. CRÍTICO: Respeita esta lesão/restrição: {st.session_state.user_data['lesoes']}.
                        Cria um treino de CROSSFIT de {tempo} minutos.
                        Estrutura: Warm-up Específico, Skill/Força (adaptado à lesão) e um WOD metabólico divertido. Usa termos oficiais de CrossFit.
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
        if len(st.session_state.mensagens) == 0:
            st.info("Gera o teu treino primeiro para podermos falar sobre ele.")
        else:
            for msg in st.session_state.mensagens:
                if msg["role"] != "system":
                    with st.chat_message(msg["role"]): st.markdown(msg["content"])
            
            chat_input = st.chat_input("Ex: A barra está ocupada, o que posso usar no WOD?")
            if chat_input:
                st.session_state.mensagens.append({"role": "user", "content": chat_input})
                with st.chat_message("user"): st.markdown(chat_input)
                with st.chat_message("assistant"):
                    response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    st.markdown(response.choices[0].message.content)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})

    with tab_diario:
        st.markdown("### 📈 O Meu Diário e Calculadora")
        colA, colB = st.columns([1, 1.2])
        with colA:
            st.markdown("#### 🧮 1RM")
            rm_val = st.number_input("O teu 1RM (kg):", min_value=0.0, step=2.5, value=100.0)
            perc = [50, 60, 70, 75, 80, 85, 90, 95]
            st.table(pd.DataFrame({"%": [f"{p}%" for p in perc], "Carga": [f"{rm_val * (p/100):.1f} kg" for p in perc]}))
        with colB:
            st.markdown("#### 🥇 Guardar PR")
            ex = st.text_input("Exercício:")
            carga = st.number_input("Peso (kg):", min_value=0.0, step=1.0)
            if st.button("💾 Registar"):
                novo = pd.DataFrame([{"Data": datetime.now().strftime("%d/%m"), "Exercício": ex, "Carga": carga}])
                st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, novo], ignore_index=True)
                st.success("Belo PR!")
            if not st.session_state.historico_cargas.empty:
                filtro = st.selectbox("Progresso:", st.session_state.historico_cargas["Exercício"].unique())
                st.line_chart(st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == filtro].set_index("Data")["Carga"])
