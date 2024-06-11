from openai import OpenAI
import streamlit as st


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
        message = response.choices[0].message
        return message.content if message else "Nenhuma resposta válida foi retornada pela API."
    else:
        return "Nenhuma resposta válida foi retornada pela API."
