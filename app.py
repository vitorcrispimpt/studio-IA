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
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { font-weight: bold; }
    h1, h2, h3 { color: #0033CC !important; }
    .stButton>button {
        background-color: #6A0DAD; color: #FFFFFF; border-radius: 8px;
        padding: 12px 24px; border: none; width: 100%; font-weight: bold; transition: 0.3s;
    }
    .stButton>button:hover { 
        background-color: #00BFFF; color: white; box-shadow: 0px 4px 12px rgba(0, 191, 255, 0.4);
    }
    </style>
""", unsafe_allow_html=True)

# A TUA IMAGEM
st.image("https://via.placeholder.com/800x200.png?text=LOG%C3%93TIPO+DO+TEU+EST%C3%9ADIO", use_column_width=True)
st.markdown("---")

# ==========================================
# 2. INICIALIZAR MEMÓRIA DA APP
# ==========================================
if "mensagens" not in st.session_state: st.session_state.mensagens = []
if "treino_ativo" not in st.session_state: st.session_state.treino_ativo = False
if "historico_estudio" not in st.session_state: st.session_state.historico_estudio = [] 
if "historico_cargas" not in st.session_state: st.session_state.historico_cargas = pd.DataFrame(columns=["Data", "Exercício", "Carga (kg)"])

# ==========================================
# 3. LIGAÇÃO À IA (OPENAI)
# ==========================================
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Configura a chave API nos Secrets do Streamlit.")

# ==========================================
# 4. A "CÂMARA SECRETA" DO PT
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
tab1, tab4, tab2, tab3 = st.tabs(["🏋️ PT Personalizado", "🔥 Box CrossFit", "💬 Chat PT", "📈 Evolução"])

# ------------------------------------------
# TAB 1: PT PERSONALIZADO (Musculação/Estúdio)
# ------------------------------------------
with tab1:
    if not st.session_state.treino_ativo:
        st.markdown("### 📋 Planeamento de Musculação/Estúdio")
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
                Inclui sempre link 3D: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
                """
                st.session_state.mensagens = [{"role": "system", "content": prompt}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                st.session_state.historico_estudio.append({"nome": nome, "objetivo": objetivo, "hora": datetime.now().strftime("%H:%M")})
                st.rerun()
    else:
        st.success("✅ Plano Ativo! Usa a Tab 'Chat PT' para ajustes.")
        for msg in st.session_state.mensagens:
            if msg["role"] == "assistant":
                st.markdown(msg["content"])
        
        st.markdown("---")
        if st.button("🔄 Novo Treino / Limpar App"):
            st.session_state.treino_ativo = False
            st.session_state.mensagens = []
            st.rerun()

# ------------------------------------------
# TAB 4: PROGRAMAÇÃO CROSSFIT
# ------------------------------------------
with tab4:
    if not st.session_state.treino_ativo:
        st.markdown("### 🦍 Gerador de Aulas e Ciclos CrossFit")
        st.write("Cria desde uma aula única até um Macrociclo de 2 meses com periodização.")
        
        with st.form("perfil_crossfit"):
            ciclo = st.selectbox("Duração da Programação:", [
                "1 Aula Única (Hoje)", 
                "1 Semana (Microciclo)", 
                "1 Mês (Mesociclo - 4 Semanas)", 
                "2 Meses (Macrociclo - 8 Semanas)"
            ])
            
            foco = st.selectbox("Qual o foco principal?", ["Equilibrado (Mix dos 3)", "Foco em Força (LPO)", "Foco em Ginástica", "Foco em Cardio (Endurance)"])
            equipamento_cf = st.multiselect("Equipamento disponível na Box:", ["Barra Olímpica e Discos", "Caixas (Plyo)", "Kettlebells", "Dumbbells", "Remos/Bikes", "Estrutura (Pull-ups/Toes to Bar)", "Corda de Saltar"], default=["Barra Olímpica e Discos", "Estrutura (Pull-ups/Toes to Bar)", "Caixas (Plyo)"])
            
            regras_extras = st.text_area("Mandar Regras à IA (Opcional):", placeholder="Ex: Sábado é Team WOD. Semana 4 deve ser Deload. Não usar Burpees esta semana.")
            
            submit_cf = st.form_submit_button("🔥 GERAR PROGRAMAÇÃO")
            
        if submit_cf:
            mensagem_loading = "A desenhar a periodização a longo prazo (isto pode demorar 1 a 2 minutos, não feches a App!)..." if "Mês" in ciclo or "Meses" in ciclo else "A programar..."
            with st.spinner(mensagem_loading):
                
                regras_string = f"\nREGRAS EXTRAS DO HEAD COACH QUE DEVES OBEDECER: {regras_extras}" if regras_extras else ""
                
                if ciclo == "1 Aula Única (Hoje)":
                    prompt_cf = f"""
                    És um Head Coach de CrossFit. Cria UMA aula de grupo de 50 minutos. Foco: {foco}. Equipamento: {', '.join(equipamento_cf)}.
                    {regras_string}
                    ESTRUTURA (Total: 50 min):
                    1. 🏃‍♂️ Warm-up (10 min)
                    2. ⏱️ Transição (2 min)
                    3. 🏋️‍♂️ Skill / Strength (15 min)
                    4. ⏱️ Transição (3 min)
                    5. 🔥 WOD (15 min) - Definir RX e Scaled e Time Cap.
                    6. 🧘‍♂️ Cooldown (5 min)
                    """
                elif ciclo == "1 Semana (Microciclo)":
                    prompt_cf = f"""
                    És um Head Coach de CrossFit. Cria um MICROCLICLO DE 1 SEMANA (Seg-Sáb). Foco: {foco}. Equipamento: {', '.join(equipamento_cf)}.
                    {regras_string}
                    Para cada dia, usa a estrutura de 50 min: Warm-up, Skill/Strength (RX/Scaled), WOD (RX/Scaled/Time Cap), Cooldown e transições. 
                    Garante variedade de estímulos.
                    """
                else:
                    # Lógica para 1 Mês ou 2 Meses
                    prompt_cf = f"""
                    És um Head Coach de CrossFit Especialista em Periodização. Cria uma programação de {ciclo} (Segunda a Sábado).
                    Foco Geral: {foco}. Equipamento: {', '.join(equipamento_cf)}.
                    {regras_string}
                    
                    PARTE 1: ESTRATÉGIA DE PERIODIZAÇÃO
                    - Descreve resumidamente o objetivo de cada semana (Ex: Semana 1 - Base/Hipertrofia, Semana 3 - Pico de Carga, Semana 4 - Deload).
                    
                    PARTE 2: PROGRAMAÇÃO DIÁRIA
                    Para a resposta não ficar demasiado extensa, para cada dia de cada semana, vai direto ao "sumo" do treino (assume que os aquecimentos de 10m e cooldowns de 5m são standard da Box).
                    Estrutura para cada dia:
                    - **[Semana X - Dia da Semana] (Estímulo)**
                    - 🏋️‍♂️ **Força/Skill (15 min):** O que fazer (Cargas/Reps para RX e Scaled).
                    - 🔥 **WOD (15 min):** Formato, Time Cap, Movimentos (RX e Scaled).
                    """

                st.session_state.mensagens = [{"role": "system", "content": prompt_cf}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                
                st.session_state.historico_estudio.append({"nome": "Aula Grupo", "objetivo": f"CrossFit - {ciclo}", "hora": datetime.now().strftime("%H:%M")})
                st.rerun()
    else:
        st.success("✅ Programação Gerada! Podes pedir ajustes à IA usando a Tab 'Chat PT'.")
        for msg in st.session_state.mensagens:
            if msg["role"] == "assistant":
                st.markdown(msg["content"])
        st.markdown("---")
        if st.button("🔄 Terminar e Gerar Nova Programação"):
            st.session_state.treino_ativo = False
            st.session_state.mensagens = []
            st.rerun()

# ------------------------------------------
# TAB 2: CHAT COM O PT VIRTUAL
# ------------------------------------------
with tab2:
    st.markdown("### 💬 Ajustes em Tempo Real")
    if not st.session_state.treino_ativo:
        st.info("Gera um treino primeiro no separador 'PT Personalizado' ou 'Box CrossFit'.")
    else:
        for msg in st.session_state.mensagens:
            if msg["role"] != "system":
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
        
        pedido = st.chat_input("Ex: Na semana 3, podes trocar os agachamentos por peso morto?")
        if pedido:
            st.session_state.mensagens.append({"role": "user", "content": pedido})
            with st.chat_message("user"): st.markdown(pedido)
            with st.chat_message("assistant"):
                with st.spinner("A reajustar a programação..."):
                    resposta = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                    novo = resposta.choices[0].message.content
                    st.markdown(novo)
            st.session_state.mensagens.append({"role": "assistant", "content": novo})

# ------------------------------------------
# TAB 3: REGISTO E EVOLUÇÃO DE CARGAS (PRs)
# ------------------------------------------
with tab3:
    st.markdown("### 📈 O teu Diário de Bordo")
    st.write("Regista as tuas cargas máximas (PRs) para garantirmos a evolução.")
    
    with st.container():
        col_ex, col_kg, col_btn = st.columns([2, 1, 1])
        with col_ex: ex_input = st.text_input("Exercício (Ex: Back Squat / Snatch)")
        with col_kg: carga_input = st.number_input("Carga (kg)", min_value=0.0, step=1.0)
        with col_btn: 
            st.write("") 
            st.write("")
            if st.button("Gravar PR 💾"):
                if ex_input:
                    nova_carga = pd.DataFrame([{"Data": datetime.now().strftime("%Y-%m-%d %H:%M"), "Exercício": ex_input, "Carga (kg)": carga_input}])
                    st.session_state.historico_cargas = pd.concat([st.session_state.historico_cargas, nova_carga], ignore_index=True)
                    st.success("Registado com sucesso!")
    
    st.markdown("---")
    if not st.session_state.historico_cargas.empty:
        st.dataframe(st.session_state.historico_cargas, use_container_width=True)
        st.markdown("#### Curva de Progressão")
        ex_selecionado = st.selectbox("Ver evolução de:", st.session_state.historico_cargas["Exercício"].unique())
        dados_grafico = st.session_state.historico_cargas[st.session_state.historico_cargas["Exercício"] == ex_selecionado]
        st.line_chart(dados_grafico.set_index("Data")["Carga (kg)"])
    else:
        st.info("Ainda não registaste cargas hoje.")
