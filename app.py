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
        st.markdown("### 🦍 Gerador de Aulas CrossFit (50 min)")
        st.write("Cria a programação com transições exatas, opções RX e Scaled, e regras personalizadas.")
        
        with st.form("perfil_crossfit"):
            ciclo = st.radio("Duração da Programação:", ["1 Aula Única (Hoje)", "Semana Completa (Segunda a Sábado)"])
            
            foco = st.selectbox("Qual o foco principal?", ["Equilibrado (Mix dos 3)", "Foco em Força (LPO)", "Foco em Ginástica", "Foco em Cardio (Endurance)"])
            equipamento_cf = st.multiselect("Equipamento disponível na Box:", ["Barra Olímpica e Discos", "Caixas (Plyo)", "Kettlebells", "Dumbbells", "Remos/Bikes", "Estrutura (Pull-ups/Toes to Bar)", "Corda de Saltar"], default=["Barra Olímpica e Discos", "Estrutura (Pull-ups/Toes to Bar)", "Caixas (Plyo)"])
            
            # CAIXA DE REGRAS ESPECÍFICAS
            regras_extras = st.text_area("Mandar Regras à IA (Opcional):", placeholder="Ex: Sábado é Team WOD. Quinta-feira focar em Ginástica. Não usar Burpees esta semana.")
            
            submit_cf = st.form_submit_button("🔥 GERAR PROGRAMAÇÃO")
            
        if submit_cf:
            mensagem_loading = "A programar a aula..." if ciclo == "1 Aula Única (Hoje)" else "A desenhar o microciclo semanal de 6 dias (pode demorar uns segundos)..."
            with st.spinner(mensagem_loading):
                
                regras_string = f"\nREGRAS EXTRAS DO HEAD COACH QUE DEVES OBEDECER: {regras_extras}" if regras_extras else ""
                
                if ciclo == "1 Aula Única (Hoje)":
                    prompt_cf = f"""
                    És um Head Coach de CrossFit (Level 3). Cria UMA aula de grupo de exatos 50 minutos estritamente estruturada.
                    Foco do dia: {foco}. Equipamento: {', '.join(equipamento_cf)}.
                    {regras_string}
                    
                    Usa os termos oficiais do CrossFit (AMRAP, EMOM, For Time, RX, Scaled, Time Cap).
                    ESTRUTURA OBRIGATÓRIA (Total: 50 min):
                    1. 🏃‍♂️ **Warm-up (10 min):** Aquecimento Geral + Específico.
                    2. ⏱️ **Transição (2 min):** Preparação de material.
                    3. 🏋️‍♂️ **Skill / Strength (15 min):** Progressão técnica ou bloco de força.
                    4. ⏱️ **Transição (3 min):** Adaptação de cargas (RX vs Scaled).
                    5. 🔥 **WOD (15 min):** Define o formato e o Time Cap obrigatório.
                    6. 🧘‍♂️ **Cooldown (5 min):** Alongamentos.
                    No WOD e na secção de Força, define obrigatoriamente as opções 🏆 RX e 🛡️ Scaled.
                    """
                else:
                    prompt_cf = f"""
                    És um Head Coach de CrossFit (Level 3/4). Cria uma PROGRAMAÇÃO SEMANAL COMPLETA de Segunda a Sábado (6 dias).
                    Cada dia corresponde a uma aula de 50 minutos. Foco macro da semana: {foco}. Equipamento disponível: {', '.join(equipamento_cf)}.
                    {regras_string}
                    
                    Garante que a semana faz sentido estruturalmente (não massacrar os mesmos músculos dias seguidos, alternar time domains - curtos e longos).
                    
                    Para CADA DIA (Segunda a Sábado), escreve um título com o dia da semana e o estímulo do dia, seguido desta estrutura (Soma 50 min):
                    1. 🏃‍♂️ Warm-up (10 min)
                    2. ⏱️ Transição (2 min)
                    3. 🏋️‍♂️ Skill/Strength (15 min) - Definir RX e Scaled
                    4. ⏱️ Transição (3 min)
                    5. 🔥 WOD (15 min) - Definir formato, Time Cap, RX e Scaled
                    6. 🧘‍♂️ Cooldown (5 min)
                    
                    Sê claro, direto e usa os termos oficiais da modalidade.
                    """

                st.session_state.mensagens = [{"role": "system", "content": prompt_cf}]
                response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
                st.session_state.treino_ativo = True
                
                registo_log = "Aula Grupo (1 Dia)" if ciclo == "1 Aula Única (Hoje)" else "Aula Grupo (Semana)"
                st.session_state.historico_estudio.append({"nome": registo_log, "objetivo": f"CrossFit - {foco}", "hora": datetime.now().strftime("%H:%M")})
                st.rerun()
    else:
        st.success("✅ Programação CrossFit Gerada! Podes pedir ajustes à IA usando a Tab 'Chat PT'.")
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
        
        pedido = st.chat_input("Ex: Uma máquina está ocupada, ou troca as pull-ups por outro movimento...")
        if pedido:
            st.session_state.mensagens.append({"role": "user", "content": pedido})
            with st.chat_message("user"): st.markdown(pedido)
            with st.chat_message("assistant"):
                with st.spinner("A reajustar..."):
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
