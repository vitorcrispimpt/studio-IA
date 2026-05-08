import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. IDENTIDADE VISUAL PREMIUM
st.set_page_config(page_title="Studio AI - Premium", page_icon="👑", layout="centered")

# CSS para cores Premium (Dourado e Preto)
st.markdown("""
    <style>
    .stButton>button {
        background-color: #D4AF37; /* Cor Dourada */
        color: black;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 10px 20px;
    }
    .stButton>button:hover {
        background-color: #000000; /* Fica Preto ao passar o rato */
        color: #D4AF37;
        border: 1px solid #D4AF37;
    }
    </style>
""", unsafe_allow_html=True)

# 2. INICIALIZAR A "MEMÓRIA" DO ESTÚDIO E DO CHAT
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []
if "historico_estudio" not in st.session_state:
    st.session_state.historico_estudio = [] # Registo para o PT
if "treino_ativo" not in st.session_state:
    st.session_state.treino_ativo = False

# 3. LIGAÇÃO À INTELIGÊNCIA
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Chave API não configurada nos Secrets do Streamlit.")

# 4. A "CÂMARA SECRETA" (Menu lateral para o PT)
with st.sidebar:
    st.markdown("### 🔐 Área de Controlo (PT)")
    senha = st.text_input("Password de Acesso", type="password")
    
    # A tua senha secreta é "estudio2026"
    if senha == "estudio2026":
        st.success("Acesso Autorizado")
        st.markdown(f"**Treinos Gerados Hoje:** {len(st.session_state.historico_estudio)}")
        st.markdown("---")
        for log in st.session_state.historico_estudio:
            st.info(f"👤 {log['nome']} | 🎯 {log['objetivo']} | ⏱️ {log['hora']}")
    elif senha != "":
        st.error("Password incorreta.")

# 5. CABEÇALHO DA APP
st.title("👑 Studio AI: Treino de Elite")
st.markdown("---")

# 6. TREINO EXPRESSO (WOD) - Para clientes com pressa
st.markdown("### ⚡ Sem tempo para o formulário?")
if st.button("🔥 GERAR TREINO EXPRESSO (30 Minutos)"):
    with st.spinner("A preparar o WOD do dia..."):
        prompt_wod = """
        És um PT. Cria um treino metabólico intenso de 30 minutos em circuito. 
        Material: Apenas peso do corpo e Kettlebells.
        Inclui links 3D para os exercícios: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
        """
        st.session_state.mensagens = [{"role": "system", "content": prompt_wod}]
        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
        
        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
        st.session_state.treino_ativo = True
        
        # Gravar na câmara secreta
        hora_atual = datetime.now().strftime("%H:%M")
        st.session_state.historico_estudio.append({"nome": "Aluno (WOD Expresso)", "objetivo": "Metabólico", "hora": hora_atual})

st.markdown("---")

# 7. FORMULÁRIO COMPLETO
st.markdown("### 📋 Planeamento Personalizado")
with st.expander("📝 Preencher Perfil do Aluno (Clica para abrir)", expanded=not st.session_state.treino_ativo):
    with st.form("perfil_aluno"):
        col1, col2 = st.columns(2)
        with col1:
            nome = st.text_input("Nome do Aluno")
            objetivo = st.selectbox("Objetivo Principal", ["Perda de Massa Gorda", "Hipertrofia", "Performance/Força", "Saúde/Manutenção"])
        with col2:
            nivel = st.select_slider("Nível", options=["Iniciante", "Intermédio", "Avançado"])
            tempo = st.slider("Tempo (minutos)", 20, 90, 45)

        lesoes = st.text_area("Lesões ou dores?", "Nenhuma")
        equipamento = st.multiselect("Material hoje:", ["Máquinas", "Halteres", "Barras", "Kettlebells", "Peso do Corpo"], default=["Máquinas", "Halteres"])

        submit_button = st.form_submit_button("GERAR TREINO COMPLETO ✨")

# 8. LÓGICA DE GERAÇÃO E CHAT
if submit_button and nome.strip():
    with st.spinner('A desenhar o plano mais seguro...'):
        prompt_sistema = f"""
        És um PT Especialista. Treino para {nome}. Obj: {objetivo}. Nível: {nivel}. Tempo: {tempo}m.
        Lesões a proteger: {lesoes}. Material: {', '.join(equipamento)}.
        Estrutura a tabela e inclui links 3D: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy).
        """
        st.session_state.mensagens = [{"role": "system", "content": prompt_sistema}]
        response = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
        
        st.session_state.mensagens.append({"role": "assistant", "content": response.choices[0].message.content})
        st.session_state.treino_ativo = True
        
        # Gravar na câmara secreta
        hora_atual = datetime.now().strftime("%H:%M")
        st.session_state.historico_estudio.append({"nome": nome, "objetivo": objetivo, "hora": hora_atual})

# 9. EXIBIÇÃO DO TREINO, CHAT E FEEDBACK
if st.session_state.treino_ativo:
    st.success("✅ O teu plano está ativo! Podes pedir ajustes no chat abaixo.")
    
    # Mostrar histórico
    for msg in st.session_state.mensagens:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Caixa de Ajustes
    pedido_chat = st.chat_input("Pede um ajuste. Ex: A máquina de Leg Press está ocupada...")
    if pedido_chat:
        st.session_state.mensagens.append({"role": "user", "content": pedido_chat})
        with st.chat_message("user"):
            st.markdown(pedido_chat)
        with st.chat_message("assistant"):
            with st.spinner("A ajustar..."):
                resposta_chat = client.chat.completions.create(model="gpt-4o-mini", messages=st.session_state.mensagens)
                novo_treino = resposta_chat.choices[0].message.content
                st.markdown(novo_treino)
        st.session_state.mensagens.append({"role": "assistant", "content": novo_treino})

    # 10. FEEDBACK PÓS-TREINO
    st.markdown("---")
    if st.button("✅ CONCLUIR TREINO (Avaliação)"):
        msg_feedback = "Parabéns por concluíres o treino! 💪 De 0 a 10, qual foi o nível de cansaço? Sentiste algum desconforto nas articulações?"
        st.session_state.mensagens.append({"role": "assistant", "content": msg_feedback})
        st.rerun() # Atualiza a página para mostrar a pergunta da IA
