import openai
import streamlit as st


def ask_chatgpt(question, context, temperature, instructions):
    api_key = st.secrets["openai"]["openai_key"]
    openai.api_key = api_key

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": instructions},
            {"role": "user", "content": f"Context: {context}\n\nPergunta: {question}"}
        ],
        temperature=temperature
    )

    if response and response.choices:
        return response.choices[0].message['content']
    else:
        return "Nenhuma resposta válida foi retornada pela API."
