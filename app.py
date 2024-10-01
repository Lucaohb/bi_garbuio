import streamlit as st
import pandas as pd
import pyodbc
import base64
import logging
import os

# Função para converter a imagem em Base64
def get_img_as_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Pegando a imagem de fundo e logo como base64
img = get_img_as_base64("Background1.png")
logo = get_img_as_base64("logo.png")

# Configuração da aplicação
st.set_page_config(page_title="Portal BI", layout="wide")

# Conexão com o banco de dados SQL Server
def get_db_connection():
    conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=186.209.34.142\BI_DASHBOARD;'  # Inclua o número da porta se necessário
    'port = 1433;'"
    'DATABASE=BI_Dashboard;'
    'UID=sa;'
    'PWD=G@rbuio24;'
    'Timeout=30;' 
)


    return conn

# Função para salvar logs no banco de dados SQL Server
def save_log_to_db(email):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        INSERT INTO access_logs (email, access_time)
        VALUES (?, CURRENT_TIMESTAMP)
    '''
    cursor.execute(query, (email,))
    conn.commit()
    cursor.close()
    conn.close()

# Configurar logging para salvar logs no SQL Server
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    class DBHandler(logging.Handler):
        def emit(self, record):
            log_entry = self.format(record)
            # Extrair o email do usuário para salvar no banco de dados
            email = st.session_state['user']['email'] if 'user' in st.session_state else 'unknown'
            save_log_to_db(email)

    db_handler = DBHandler()
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    db_handler.setFormatter(formatter)
    logger.addHandler(db_handler)

    return logger

# Inicializando o logger
logger = configure_logging()
logger.info("Aplicação iniciada.")


# Dicionário que mapeia URLs para os títulos dos dashboards
dashboard_titles = {
        "https://app.powerbi.com/view?r=eyJrIjoiMmU1MTBmYTItMmY3MS00NjYzLTg3ZWUtOWQyYzI1YTgyYTQxIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Central de BIs",
        "https://app.powerbi.com/view?r=eyJrIjoiNzYwMTE4OWEtZTc2Zi00NGQ0LWJhOTgtNzE0ZDMwN2Q0NzI3IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9&chromeless=true": "Faturamento",
        "https://app.powerbi.com/view?r=eyJrIjoiZmYzMjkyMjItYWE0MC00YWM3LWFmOTMtZmYyNTg4ZjQ0YTMxIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Geral",
        "https://app.powerbi.com/view?r=eyJrIjoiMTljYjYxOGQtNDMzMy00MTE2LTkxMzYtNmZhMGM1MmMzZjgxIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Anderson",
        "https://app.powerbi.com/view?r=eyJrIjoiYTIyNGRkZjUtYTBkMS00ZjgxLTgyOWMtOTcxYTc4NjRiMDQ2IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Luiz",
        "https://app.powerbi.com/view?r=eyJrIjoiMWMxMTEwZWEtODM4ZS00YmM0LThjNzEtMTdkYmUwYWYzODE4IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Cesar",
        "https://app.powerbi.com/view?r=eyJrIjoiY2RmZWFhYTctNzZjOC00YmVjLThiNTItNWZiMjFkMGJmOWJjIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Frederico",
        "https://app.powerbi.com/view?r=eyJrIjoiMGM5YzM3MGQtZTkwZi00NzFhLTlkNzYtNmFkNTk4ZGUwODdlIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Janaina",
        "https://app.powerbi.com/view?r=eyJrIjoiMWEzODYyNDctNTU1NS00OWZlLWE2NGYtZGVmOTM3NjkyMTI1IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Anderson",
        "https://app.powerbi.com/view?r=eyJrIjoiMWEzODYyNDctNTU1NS00OWZlLWE2NGYtZGVmOTM3NjkyMTI1IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Controladoria Rafael",  
        "https://app.powerbi.com/reportEmbed?reportId=385a53c2-365e-416c-9ca5-f9c3f08bcd11&autoAuth=true&ctid=cc2a95ea-335c-443b-8443-e9ad33ff9e04": "Controladoria Geral Exportável",
        "https://app.powerbi.com/view?r=eyJrIjoiZjg0YTQ5OGQtOWI2MC00YWFkLTk3ZmMtYzcyYTMxY2U0YTcyIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Abastecimento",
        "https://app.powerbi.com/reportEmbed?reportId=0ba6b5ca-c1a0-44b6-9033-db6491ca6f36&autoAuth=true&ctid=cc2a95ea-335c-443b-8443-e9ad33ff9e04": "Abastecimento Exportável",
        "https://app.powerbi.com/view?r=eyJrIjoiN2IwYjFhZGUtYWYwNC00NjI2LWFkMGYtMmVjYzE2MTI1ZWM3IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Suprimentos",
        "https://app.powerbi.com/view?r=eyJrIjoiOTBlNDlkNmUtMWM1Ni00MWE2LThiMDEtMDIwMmVmNmNjN2RjIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Recursos Humanos",
        "https://app.powerbi.com/view?r=eyJrIjoiZDYzODQ2MGYtZjU4NS00Y2M1LWFjZDEtNGViMzIyYjNlZGQwIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Manutenção",
        "https://app.powerbi.com/view?r=eyJrIjoiNmMxYzJhNTctYmNkZC00MzVlLWI1ZTMtN2U0NWE2YjYxMjY4IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Contas a Pagar",
        "https://app.powerbi.com/view?r=eyJrIjoiYWQxMGYwNTgtZWEwMi00OTg0LTgyZjAtYTI0ZDcwY2NiMzkzIiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Pátio",
        "https://app.powerbi.com/view?r=eyJrIjoiMzVhNDliNjYtNGU1MS00YTUzLWIwMTctZWZmNThmYzZiZjk0IiwidCI6ImNjMmE5NWVhLTMzNWMtNDQzYi04NDQzLWU5YWQzM2ZmOWUwNCJ9": "Torre de Controle"
    }

# Função para carregar usuários e seus dashboards
def load_users():
    df = pd.read_excel('users.xlsx')
    users = {}
    for _, row in df.iterrows():
        users[row['email']] = {
            "email": row['email'],
            "password": row['password'],
            "role": row['role'],
            "dashboards": str(row['dashboards']).split(','),  # Garantindo que seja uma string
            "name": row['name']
        }
    return users

users = load_users()

# Função para verificar login
def check_login(email, password):
    user = users.get(email)
    if user and user['password'] == password:
        save_log_to_db(email)  # Salva o log no banco ao fazer login
        return user
    return None

# Função para exibir os dashboards do usuário
def display_dashboards(user):
    st.markdown(
        f"""
        <div style="text-align: center;">
            <img src="data:image/png;base64,{logo}" alt="Logo" style="width: 200px;">
            <br></br>
        </div>
        """, unsafe_allow_html=True
    )
    st.title(f"Bem-vindo, {user['name']}! Você está acessando o dashboard gerencial.")
    st.header("Aqui você encontrará informações valiosas e insights úteis para a organização.")
    
    for idx, dashboard_url in enumerate(user['dashboards']): 
        if isinstance(dashboard_url, str):
            title = dashboard_titles.get(dashboard_url.strip(), f"Dashboard {idx + 1}")
            st.subheader(title)
            iframe_html = f"""
            <iframe src="{dashboard_url.strip()}" width="100%" height="900px" style="border:none;"></iframe>
            """
            st.markdown(iframe_html, unsafe_allow_html=True)

    # Mostrar botão de exportar logs apenas para admins
    if user['role'] == 'admin':
        if st.button('Exportar Logs'):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM access_logs')
            logs = cursor.fetchall()
            df_logs = pd.DataFrame(logs, columns=['ID', 'Email', 'Access Time'])
            logs_csv = df_logs.to_csv(index=False)
            cursor.close()
            conn.close()
            st.download_button('Baixar Logs', logs_csv, file_name='logs.csv')

# Página de login
def login_page():
    st.markdown(f"""
    <style>
        [data-testid="stAppViewContainer"] {{
            background-image: url("data:image/png;base64,{img}");
            background-size: cover;
            background-position: center;
        }}
        button[data-testid="stButton"] {{
            width: 150px;
            height: 45px;
            font-size: 5px;
            border-radius: 10px;
            background-color: #4CAF50;
            color: white;
        }}
    </style>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("<h1 style='color: black;text-align: center;'>Login</h1>", unsafe_allow_html=True)
        st.markdown("<h4>E-mail</h4>", unsafe_allow_html=True)
        email = st.text_input(" ", key="email")  
        st.markdown("<h4>Senha</h4>", unsafe_allow_html=True)
        password = st.text_input(" ", type="password", key="password")

        if st.button("Login", key="login_button"):
            user = check_login(st.session_state["email"], st.session_state["password"])
            if user:
                st.session_state['user'] = user
                st.markdown("<script>window.scrollTo(0, 0);</script>", unsafe_allow_html=True)
                st.experimental_rerun()
            else:
                st.error("Credenciais inválidas")

# Página principal
def main():
    if 'user' not in st.session_state:
        login_page()
    else:
        user = st.session_state['user']
        display_dashboards(user)

        if st.button("Logout"):
            del st.session_state['user']
            st.experimental_rerun()

if __name__ == '__main__':
    main()
