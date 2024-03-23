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

# Função para gerar um ID aleatório
def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# Função para salvar os dados em um arquivo de texto na raiz do diretório
def save_to_txt(data, filename):
    with open(filename, "w") as file:
        file.write(data)

# Função para ler os dados de um arquivo de texto
def read_from_txt(filename):
    with open(filename, "r") as file:
        return file.read()

@app.get("/")
def root():
    return {"Dev": "PLAY7:(2799570-0396)"}

@app.get("/certificado/{cpf}/{senha}")
def certificadoleve(cpf: str, senha: str):
    try:
        device_id = generate_random_id()
        generator = CertificateGenerator(cpf, senha, device_id)
        email = generator.request_code()

        # Salvar os dados em um arquivo de texto na raiz do diretório
        data = f"CPF: {cpf}\nDevice ID: {device_id}\nEmail: {email}"
        filename = f"{cpf}_{device_id}.txt"
        save_to_txt(data, filename)

        return {"email": email}
    except NuException as e:
        return {"error": str(e)}

@app.get("/codigo/{codigo}/{cpf}")
def leve(codigo: str, cpf: str):
    try:
        # Carregar os dados do arquivo de texto
        filename = f"{cpf}_{codigo}.txt"
        data = read_from_txt(filename)

        # Verifica se o arquivo existe
        if not os.path.exists(filename):
            return {"error": "Arquivo não encontrado."}

        # Extrai o código do arquivo
        lines = data.split("\n")
        loaded_code = lines[1].split(": ")[1]

        # Verifica se o código informado está correto
        if loaded_code == codigo:
            # Gerar certificado
            cpf_loaded = lines[0].split(": ")[1]
            device_id_loaded = lines[2].split(": ")[1]
            generator = CertificateGenerator(cpf_loaded, None, device_id_loaded)
            cert1, cert2 = generator.exchange_certs(codigo)

            # Salvar certificado na raiz do diretório
            filename_cert = f"{codigo}.p12"
            with open(filename_cert, "wb") as file:
                file.write(cert1.export())

            return {"mensagem": "Play7Server - Certificado Gerado com sucesso!"}
        else:
            return {"error": "Código incorreto."}

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
