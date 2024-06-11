import mysql.connector
from mysql.connector import Error
import streamlit as st


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
            return instructions['instruction'], instructions['temperature']
        return "", 0.7
    except Error as e:
        st.write(f"Error: {e}")
        return "", 0.7


def save_instructions(instruction, temperature):
    try:
        connection = mysql.connector.connect(
            host=st.secrets["mysql"]["host"],
            port=st.secrets["mysql"]["port"],
            user=st.secrets["mysql"]["user"],
            password=st.secrets["mysql"]["password"],
            database=st.secrets["mysql"]["database"]
        )
        cursor = connection.cursor()
        query = "REPLACE INTO instructions (id, instruction, temperature) VALUES (1, %s, %s)"
        cursor.execute(query, (instruction, temperature))
        connection.commit()
        cursor.close()
        connection.close()
    except Error as e:
        st.write(f"Error: {e}")
