import streamlit as st
from extract import extract_text_from_pdf
from analyze import ask_chatgpt
from database import authenticate, get_instructions, save_instructions


def get_vaga_instructions(vaga):
    instrucoes = {
        "analista de manutenção": """
        - Curso técnico em mecânica concluído;
        - Graduação em engenharia concluído ou em andamento;
        - Vivência e prática em manutenção de linha leve e pesados;
        - Inglês Técnico
        - Disponibilidade para residir em Itajaí -SC
        """,
        "mecânico": """
        - Realizar manutenção preventiva e corretiva dos equipamentos;
        - Auxiliar na análise e identificação de problemas dos equipamentos;
        - Realizar reparos, substituição de peças, fazendo ajustes e regulagem;
        - Identificar peças / insumos necessários para PCM
        """,
        "auxiliar de manutenção": """
        - Auxiliar nas manutenções corretivas e preventivas sob a supervisão dos mecânicos.
        - Localizar e retirar peças e insumos nos locais de estoque da empresa.
        - Interagir com o departamento de suprimentos para identificar as necessidades de materiais adicionais.
        - Realizar pedidos de reposição de estoque conforme necessário.
        - Coletar informações de horímetro e/ou odômetro dos equipamentos para manutenção programada.
        - Manter registros precisos de todas as transações de materiais, incluindo entradas e saídas.
        - Comunicar-se de forma eficaz com os mecânicos para garantir que suas necessidades sejam atendidas prontamente.
        """,
        "auxiliar de escritório": """
        - Ensino médio completo;
        - Pacote Office;
        - Conhecimento em Faturamento.
        """,
        "turismo": """
        - Ensino médio completo;
        - Pacote Office;
        - Boa comunicação;
        - Disponibilidade de horário;
        """,
        "motorista basculante": """
        - Carteira Habilitação D ou E;
        - Experiência prévia na condução desses modelos de veículos.
        """,
        "motorista swl": """
        - Habilitação C, D e/ou E;
        - Ensino Médio Completo;
        - Vivência e prática em condução de caminhões dentro de áreas urbanas;
        - Vivência e prática em caminhão PIPA/HIDROJATO e/ou caminhão tanque, e/ou caminhão coletor de lixo / coletor de entulho, e/ou caminhão de apoio e/ou caminhão betoneira.
        """,
        "programador": """
        - Conhecimento em programação na linguagem PHP;
        - Conhecimento em programação na linguagem Python;
        - Conhecimento em Inglês.
        """
    }
    return instrucoes.get(vaga, "")


def main():
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.role = ""

    if not st.session_state.authenticated:
        st.title("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if authenticate(username, password):
                st.session_state.authenticated = True
                st.rerun()
            else:
                st.error("Usuário ou senha incorretos")
    else:
        if "instructions" not in st.session_state or "temperature" not in st.session_state or "nota_apto" not in st.session_state or "nota_min_semi_apto" not in st.session_state or "nota_max_semi_apto" not in st.session_state:
            instructions, nota_apto, nota_min_semi_apto, nota_max_semi_apto, temperature = get_instructions()
            st.session_state.instructions = instructions
            st.session_state.temperature = temperature
            st.session_state.nota_apto = nota_apto
            st.session_state.nota_min_semi_apto = nota_min_semi_apto
            st.session_state.nota_max_semi_apto = nota_max_semi_apto

        st.sidebar.title("Administração")
        if st.session_state.role == "admin":
            st.sidebar.write("Bem-vindo, Administrador")
            st.sidebar.text_area("Instruções", key="instructions", height=300)
            st.sidebar.slider("Temperatura", 0.0, 1.0,
                              st.session_state.temperature, key="temperature")
            st.sidebar.number_input(
                "Nota Apto", min_value=0, step=1, key="nota_apto")
            st.sidebar.number_input(
                "Nota Min Semi-Apto", min_value=0, step=1, key="nota_min_semi_apto")
            st.sidebar.number_input(
                "Nota Max Semi-Apto", min_value=0, step=1, key="nota_max_semi_apto")
            if st.sidebar.button("Salvar Instruções"):
                save_instructions(st.session_state.instructions,
                                  st.session_state.nota_apto,
                                  st.session_state.nota_min_semi_apto,
                                  st.session_state.nota_max_semi_apto,
                                  st.session_state.temperature)
                st.success("Instruções salvas com sucesso!")
        else:
            st.sidebar.write("Acesso restrito ao administrador")

        st.title("RecrutaSmart - Assistente de Seleção de Currículos")

        vagas = [
            "analista de manutenção",
            "mecânico",
            "auxiliar de manutenção",
            "auxiliar de escritório",
            "turismo",
            "motorista basculante",
            "motorista swl",
            "programador"
        ]

        vaga = st.selectbox("Selecione a Vaga", vagas)

        uploaded_files = st.file_uploader("Upload de Currículos (PDF)", type=[
                                          "pdf"], accept_multiple_files=True)

        context = ""
        if uploaded_files:
            for uploaded_file in uploaded_files:
                text = extract_text_from_pdf(uploaded_file)
                context += text

        if "messages" not in st.session_state:
            st.session_state.messages = []

        def send_message():
            user_message = "analise"
            if user_message:
                st.session_state.messages.append(
                    {"role": "user", "content": user_message})

                instructions = f"""
                Você é um assistente com nome de RecrutaSmart especializado em analisar e selecionar currículos em formato .PDF.
                Absorva as seguintes variáveis:
                “nota_apto” = {st.session_state.nota_apto};
                “nota_min_sa”={st.session_state.nota_min_semi_apto};
                “nota_max_sa”={st.session_state.nota_max_semi_apto};
                {get_vaga_instructions(vaga)}
                Sempre que o usuário solicitar o "analise". Siga as diretrizes abaixo para seleção do candidato:
                1. Liste de forma numerada todas as vagas.
                2. Quando não achar nenhum candidato apto a vaga imprima a mensagem "Não existe nenhum candidato que atenda aos REQUISITOS desta VAGA."
                3. Cada arquivo .PDF é um currículo de um candidato único, deve ser analisado.
                4. Não consulte currículos na internet, somente analise os currículos para preencher as vagas solicitadas.
                5. Conte o número de candidatos selecionados e mostre isso antes ao final do relatório.
                6. Cada requisito para vaga tem um peso de 10, ao final faça a média:
                   - Sempre que a média for superior a “nota_apto” este candidato está apto;
                   - Sempre que a média for no intervalo de “nota_min_sa” a “nota_max_sa” este candidato está semi-apto a função;
                   - Sempre que o candidato for considerado apto ou semi-apto imprima os dados pulando uma linha para imprimir o próximo:
                     - Nome:
                     - Cidade:
                     - Estado:
                     - Telefone:
                     - Email:
                   - Classifique/organize a lista de candidatos aptos por nome deixando este como título para cada candidato;
                   - Mostre a média de cada candidato apto e semi-apto;
                   - Separe os aptos dos semi-aptos;
                   - Não mostre os candidatos com média abaixo de “nota_min_sa”.
                7. Mostre os requisitos para a vaga somente no início da análise, sem mostrar o que cada candidato possui.
                8. Resumo da Análise:
                   - Após imprimir as análises dos candidatos mostre este resumo;
                   - Este resumo deve conter o número total de candidatos selecionados;
                   - O Número de candidatos que estão aptos (coloque os nomes dos aptos separando-os por vírgula);
                   - O número de candidatos que estão semi-apto (coloque os nomes dos semi-apto separando-os por vírgula).
                """

                with st.spinner("O assistente está analisando os currículos..."):
                    response = ask_chatgpt(
                        user_message, context, st.session_state.temperature, instructions)

                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
                st.session_state.user_input = ""

        def clear_messages():
            st.session_state.messages = []

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"**Usuário:** {message['content']}")
            else:
                st.write(f"**Assistente:** {message['content']}")

        st.text_input("Digite 'analise' para iniciar a análise dos currículos:",
                      key="user_input", on_change=send_message)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.button("Enviar", on_click=send_message)
        with col2:
            st.button("Limpar Conversa", on_click=clear_messages)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
