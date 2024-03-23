from fastapi import FastAPI
from pydantic import BaseModel
from pynubank import Nubank, MockHttpClient
import os
import random
import string
from getpass import getpass
import json
from colorama import init, Fore, Style

from pynubank import NuException
from pynubank.utils.certificate_generator import CertificateGenerator
import ftplib
from pynubank import Nubank, HttpClient
import requests
import mysql.connector

app = FastAPI()

# Configurações de conexão com o banco de dados
db_config = {
    'user': 'xampca78_admin',
    'password': 'Em@88005424',
    'host': 'br506.hostgator.com.br',
    'database': 'xampca78_py',
}

# Função para conectar ao banco de dados
def connect_to_database():
    return mysql.connector.connect(**db_config)

# Definindo modelos Pydantic
class Codigo(BaseModel):
    id: int
    codigo: str

class Saldo(BaseModel):
    cpf: int
    senha: str
    certificado: str

class Usuario(BaseModel):
    cpf: int
    senha: str

# Função para gerar um ID aleatório
def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# Função para salvar o certificado
def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())

@app.get("/")
def root():
    return {"Dev": "PLAY7:(2799570-0396)"}

@app.get("/certificado/{cpf}/{senha}")
def certificadoleve(cpf: str, senha: str):
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        device_id = generate_random_id()
        generator = CertificateGenerator(cpf, senha, device_id)
        email = generator.request_code()

        # Salvando no banco de dados
        sql = "INSERT INTO certificados (cpf, device_id, email) VALUES (%s, %s, %s)"
        val = (cpf, device_id, email)
        cursor.execute(sql, val)
        conn.commit()

        cursor.close()
        conn.close()

        return {"email": email}
    except NuException as e:
        return {"error": str(e)}

@app.get("/codigo/{codigo}/{cpf}")
def leve(codigo: str, cpf: str):
    conn = connect_to_database()
    cursor = conn.cursor()

    try:
        # Verifica se o CPF existe no banco de dados
        cursor.execute("SELECT * FROM certificados WHERE cpf = %s", (cpf,))
        result = cursor.fetchone()
        if not result:
            return {"error": "CPF não encontrado."}

        # Gerar certificado
        generator = result[2]  # Supondo que o terceiro campo seja o generator
        cert1, cert2 = generator.exchange_certs(codigo)

        # Salvar certificado
        save_cert(cert1, (codigo + '.p12'))

        cursor.close()
        conn.close()

        return {"mensagem": "Play7Server - Certificado Gerado com sucesso!"}
    except Exception as e:
        return {"error": "Erro ao gerar certificado. Verifique os dados e tente novamente."}

@app.get("/perfilcompleto/{cpf}/{senha}/{certificado}")
def obter_perfilcompleto(cpf: str, senha: str, certificado: str):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)

    # Obter informações do perfil completo aqui
    # Deixei comentado, pois a lógica específica não está definida

    return {"mensagem": "Perfil completo obtido com sucesso!"}

def main():
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)

if __name__ == '__main__':
    main()
