import streamlit as st
from openai import OpenAI

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Studio AI - Personal Trainer", 
    page_icon="🏋️‍♂️",
    layout="centered"
)

# Inicializar a "Memória" do Chat
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# 2. LIGAÇÃO À INTELIGÊNCIA (API)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Chave API não configurada nos Secrets do Streamlit.")

# 3. INTERFACE PRINCIPAL
st.title("🏋️‍♂️ Studio AI: Treino Inteligente")
st.subheader("Planeamento Científico Personalizado")
st.markdown("---")

# 4. FORMULÁRIO DE ANAMNESE
with st.expander("📝 Formulário do Aluno (Clica para abrir/fechar)", expanded=len(st.session_state.mensagens)==0):
    with st.form("perfil_aluno"):
        col1, col2 = st.columns(2)
        
        with col1:
            nome = st.text_input("Nome do Aluno")
            objetivo = st.selectbox(
                "Objetivo Principal", 
                ["Perda de Massa Gorda", "Hipertrofia", "Performance/Força", "Saúde/Manutenção"]
            )
        
        with col2:
            nivel = st.select_slider(
                "Nível de Experiência", 
                options=["Iniciante", "Intermédio", "Avançado"]
            )
            tempo = st.slider("Tempo disponível (minutos)", 20, 90, 45)

        lesoes = st.text_area(
            "Tens alguma lesão ou dor? (Ex: Hérnia lombar, dor no joelho, ombro instável)", 
            "Nenhuma"
        )
        
        equipamento = st.multiselect(
            "Material que tens disponível agora:", 
            ["Máquinas", "Halteres", "Barras", "Kettlebells", "Peso do Corpo", "Elásticos"],
            default=["Máquinas", "Halteres"]
        )

        submit_button = st.form_submit_button("GERAR TREINO AGORA ✨")

# 5. LÓGICA DE GERAÇÃO (PRIMEIRO TREINO)
if submit_button:
    if not nome.strip():
        st.error("Por favor, introduz o nome do aluno para continuar.")
    else:
        with st.spinner('A analisar as tuas limitações e a criar o treino mais seguro...'):
            try:
                # O PROMPT MESTRE
                prompt_sistema = f"""
                És um Especialista em Fisiologia do Exercício e Reabilitação Física.
                Cria um treino científico para o aluno {nome}, respeitando estas diretrizes:

                1. ANÁLISE DE SEGURANÇA:
                - Se '{lesoes}' contiver "Lombar": Substitui agachamentos axiais por Goblet Squats ou exercícios de estabilização.
                - Se '{lesoes}' contiver "Joelho": Evita impactos; foca em exercícios controlados.
                - Se '{lesoes}' contiver "Ombro": Evita press acima da cabeça; foca em retração escapular.

                2. METODOLOGIA:
                - Objetivo: {objetivo}. Nível: {nivel}. Tempo: {tempo} min.
                - Equipamento: Usa APENAS {', '.join(equipamento)}.

                3. FORMATO DO OUTPUT:
                - Resumo da Estratégia (1 frase).
                - Protocolo de Prevenção (Justifica as trocas por causa da lesão).
                - Tabela de Treino: Exercício | Séries/Reps | RPE (1-10) | Descanso.
                - PARA CADA EXERCÍCIO, inclui um link: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy)
                """

                # Limpar memória antiga e guardar a nova instrução
                st.session_state.mensagens = [{"role": "system", "content": prompt_sistema}]

                # Pedir o treino à IA
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=st.session_state.mensagens
                )
                
                treino_final = response.choices[0].message.content
                
                # Guardar a resposta da IA na memória
                st.session_state.mensagens.append({"role": "assistant", "content": treino_final})

            except Exception as e:
                st.error(f"Ocorreu um erro técnico: {e}")

# 6. EXIBIÇÃO DO TREINO E CHAT DINÂMICO
if len(st.session_state.mensagens) > 0:
    st.success("✅ O teu plano está pronto e ativo na memória!")
    st.markdown("---")
    
    # Mostrar todo o histórico (escondendo as regras secretas do sistema)
    for msg in st.session_state.mensagens:
        if msg["role"] != "system":
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    
    # Caixa de Chat para Ajustes
    st.markdown("### 💬 Ajustes na Hora")
    st.caption("A máquina está ocupada? Estás com dor? Pede uma alternativa abaixo:")
    
    pedido_chat = st.chat_input("Ex: Troca o Supino por uma alternativa com halteres...")
    
    if pedido_chat:
        # 1. Mostrar o que o utilizador pediu
        with st.chat_message("user"):
            st.markdown(pedido_chat)
        
        # 2. Guardar na memória
        st.session_state.mensagens.append({"role": "user", "content": pedido_chat})
        
        # 3. Pedir à IA para ajustar com base na memória
        with st.chat_message("assistant"):
            with st.spinner("A ajustar o teu treino..."):
                resposta_chat = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=st.session_state.mensagens
                )
                novo_treino = resposta_chat.choices[0].message.content
                st.markdown(novo_treino)
        
        # 4. Guardar a nova resposta na memória
        st.session_state.mensagens.append({"role": "assistant", "content": novo_treino})

# 7. SECÇÃO DE SUPORTE E FAQ
st.markdown("---")
with st.expander("🤔 Como é que a Studio AI garante a minha segurança?"):
    st.write("""
    **1. Base Científica:** Utilizamos protocolos validados pelas maiores organizações de fitness do mundo.
    **2. Filtro de Lesões:** A IA bloqueia exercícios de risco para a tua condição específica.
    **3. Execução Visual:** Tens acesso a vídeos 3D para cada exercício.
    **4. Supervisão:** Este sistema é uma ferramenta de apoio. Na dúvida, chama o teu PT!
    """)
