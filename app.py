import streamlit as st
from openai import OpenAI

# 1. CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Studio AI - Personal Trainer", 
    page_icon="🏋️‍♂️",
    layout="centered"
)

# 2. LIGAÇÃO À INTELIGÊNCIA (API)
try:
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
except Exception:
    st.error("Erro: Chave API não configurada nos Secrets do Streamlit.")

# 3. INTERFACE PRINCIPAL
st.title("🏋️‍♂️ Studio AI: Treino Inteligente")
st.subheader("Planeamento Científico Personalizado")
st.markdown("---")

# 4. FORMULÁRIO DE ANAMNESE (O que o cliente preenche)
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

# 5. LÓGICA DE GERAÇÃO COM IA
if submit_button:
    if not nome.strip():
        st.error("Por favor, introduz o nome do aluno para continuar.")
    else:
        with st.spinner('A analisar as tuas limitações e a criar o treino mais seguro...'):
            try:
                # O PROMPT MESTRE (Com a regra dos vídeos 3D)
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
                - Baseia-te em evidências (ACSM/NSCA).

                3. FORMATO DO OUTPUT (ESTRITO):
                - Resumo da Estratégia (1 frase).
                - Protocolo de Prevenção (Justifica as trocas por causa da lesão).
                - Tabela de Treino: Exercício | Séries/Reps | RPE (1-10) | Descanso | Notas Técnicas.
                - PARA CADA EXERCÍCIO, inclui obrigatoriamente um link clicável no formato Markdown para ver a animação 3D do movimento no YouTube. Exemplo: [🎥 Ver Animação 3D](https://www.youtube.com/results?search_query=NOME+DO+EXERCICIO+3d+animation+anatomy)
                - Dica Científica final sobre o objetivo.
                """

                # Chamada à API (Usando o gpt-4o-mini que é mais rápido e económico)
                response = client.chat.completions.create(
                    model="gpt-4o-mini", 
                    messages=[{"role": "system", "content": prompt_sistema}]
                )
                
                treino_final = response.choices[0].message.content

                # 6. EXIBIÇÃO DOS RESULTADOS
                st.success(f"Plano de {nome} pronto!")
                st.markdown("---")
                st.markdown(treino_final)
                
                # Opção de download para o aluno levar no telemóvel
                st.download_button(
                    label="📥 Guardar Treino no Telemóvel",
                    data=treino_final,
                    file_name=f"treino_{nome}.txt",
                    mime="text/plain"
                )

            except Exception as e:
                st.error(f"Ocorreu um erro técnico: {e}")

# 7. SECÇÃO DE SUPORTE E FAQ (Atualizada com a parte dos vídeos)
st.markdown("---")
with st.expander("🤔 Como é que a Studio AI garante a minha segurança?"):
    st.write("""
    **1. Base Científica:** Utilizamos protocolos validados pelas maiores organizações de fitness do mundo.
    **2. Filtro de Lesões:** A IA bloqueia exercícios de risco para a tua condição específica.
    **3. Execução Visual:** Tens acesso a vídeos 3D para cada exercício, garantindo a tua técnica.
    **4. Supervisão:** Este sistema é uma ferramenta de apoio. Na dúvida, chama o teu Personal Trainer!
    """)

with st.expander("💡 Dicas para um treino perfeito"):
    st.write("""
    * Sê muito específico na descrição das tuas dores.
    * Mantém o teu nível de experiência atualizado.
    * Respeita o tempo de descanso sugerido na tabela.
    * Clica em **🎥 Ver Animação 3D** sempre que não conheceres um movimento.
    """)

st.caption("Studio AI © 2026 - Treino de Elite para Todos.")
