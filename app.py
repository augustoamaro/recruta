import streamlit as st
from PyPDF2 import PdfReader
import mysql.connector
from mysql.connector import Error
from openai import OpenAI

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

# Função de autenticação


def authenticate(username, password):
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        connection.close()
        if user:
            st.session_state.role = user['role']
            return True
        return False
    except Error as e:
        st.write(f"Error: {e}")
        return False

# Função para obter as instruções e temperatura


def get_instructions():
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor(dictionary=True)
        query = "SELECT * FROM instructions LIMIT 1"
        cursor.execute(query)
        instructions = cursor.fetchone()
        cursor.close()
        connection.close()
        if instructions:
            return instructions
        return None
    except Error as e:
        st.write(f"Error: {e}")
        return None

# Função para salvar as instruções e temperatura


def save_instructions(text, temperature, nota_apto, nota_min_semi_apto, nota_max_semi_apto):
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor()
        query = """
            REPLACE INTO instructions (
                id, instruction, temperature, nota_apto, nota_min_semi_apto, nota_max_semi_apto
            ) VALUES (1, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (text, temperature, nota_apto,
                       nota_min_semi_apto, nota_max_semi_apto))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        st.write(f"Error: {e}")

# Função para extrair texto de um PDF


def extract_text_from_pdf(pdf_file):
    pdf_reader = PdfReader(pdf_file)
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# Função para fazer uma pergunta à API do ChatGPT usando a biblioteca oficial


def ask_chatgpt(question, context, temperature, instructions):
    api_key = st.secrets["openai"]["openai_key"]
    client = OpenAI(api_key=api_key)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"Context: {context}\n\nPergunta: {question}"}
        ],
        temperature=temperature
    )

    if response and response.choices:
        return response.choices[0].message.content
    else:
        return "Nenhuma resposta válida foi retornada pela API."

# Interface do Streamlit


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
                st.experimental_rerun()
            else:
                st.error("Usuário ou senha incorretos")
    else:
        st.sidebar.title("Administração")

        if st.session_state.role == "admin":
            if "instruction_data" not in st.session_state:
                instructions_data = get_instructions()
                if instructions_data:
                    st.session_state.instruction_data = instructions_data
                else:
                    st.session_state.instruction_data = {
                        "instruction": "",
                        "temperature": 0.7,
                        "nota_apto": 0,
                        "nota_min_semi_apto": 0,
                        "nota_max_semi_apto": 0
                    }

            instruction_data = st.session_state.instruction_data

            st.sidebar.write("Bem-vindo, Administrador")
            instruction_data["instruction"] = st.sidebar.text_area(
                "Instruções", instruction_data["instruction"], height=300)
            instruction_data["temperature"] = st.sidebar.slider(
                "Temperatura", 0.0, 1.0, instruction_data["temperature"])
            instruction_data["nota_apto"] = st.sidebar.slider(
                "Nota Apto", 0, 100, step=1, value=instruction_data["nota_apto"])
            instruction_data["nota_min_semi_apto"] = st.sidebar.slider(
                "Nota Min Semi Apto", 0, 100, step=1, value=instruction_data["nota_min_semi_apto"])
            instruction_data["nota_max_semi_apto"] = st.sidebar.slider(
                "Nota Max Semi Apto", 0, 100, step=1, value=instruction_data["nota_max_semi_apto"])

            if st.sidebar.button("Salvar Instruções"):
                save_instructions(
                    instruction_data["instruction"],
                    instruction_data["temperature"],
                    instruction_data["nota_apto"],
                    instruction_data["nota_min_semi_apto"],
                    instruction_data["nota_max_semi_apto"]
                )
                st.success("Instruções salvas com sucesso!")

        else:
            st.sidebar.write("Acesso restrito ao administrador")

        st.title("RecrutaSmart")

        selected_vaga = st.selectbox("Selecione a vaga", vagas)

        # Upload de PDFs
        uploaded_files = st.file_uploader(
            "Upload de PDFs", type=["pdf"], accept_multiple_files=True)

        context = ""
        if uploaded_files:
            for uploaded_file in uploaded_files:
                text = extract_text_from_pdf(uploaded_file)
                context += text

        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Função para enviar mensagem
        def send_message():
            user_message = st.session_state.user_input
            if user_message:
                st.session_state.messages.append(
                    {"role": "user", "content": user_message})

                with st.spinner("O assistente está pensando..."):
                    instructions_data = get_instructions()
                    response = ask_chatgpt(
                        user_message,
                        f"{context}\n\nVaga: {selected_vaga}",
                        instructions_data['temperature'],
                        instructions_data['instruction']
                    )

                st.session_state.messages.append(
                    {"role": "assistant", "content": response})
                st.session_state.user_input = ""

        # Função para limpar mensagens
        def clear_messages():
            st.session_state.messages = []

        # Exibir mensagens
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.write(f"**Usuário:** {message['content']}")
            else:
                st.write(f"**Assistente:** {message['content']}")

        # Campo de entrada de mensagem e botões de enviar e limpar
        st.text_input("Digite sua pergunta:",
                      key="user_input", on_change=send_message)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col1:
            st.button("Enviar", on_click=send_message)
        with col2:
            st.button("Limpar Conversa", on_click=clear_messages)


if __name__ == "__main__":
    main()
