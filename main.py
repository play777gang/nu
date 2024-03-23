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

import tempfile  # Importando o módulo tempfile para lidar com arquivos temporários

app = FastAPI()

# Dicionário para armazenar os certificados temporariamente
certificates = {}

# Função para gerar um ID aleatório
def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))

# Função para salvar o certificado em um arquivo temporário e armazenar o caminho desse arquivo
def save_cert(cert, name):
    _, temp_path = tempfile.mkstemp(suffix=".p12")
    with open(temp_path, 'wb') as cert_file:
        cert_file.write(cert.export())
    return temp_path

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

@app.get("/")
def root():
    return {"Olá": "Mundo"}

@app.get("/certificado/{cpf}/{senha}")
def certificadoleve(cpf: str, senha: str):
    device_id = generate_random_id()
    generator = CertificateGenerator(cpf, senha, device_id)

    try:
        email = generator.request_code()
        certificates[cpf] = generator  # Armazenando o gerador no dicionário
        return {"email": email}
    except Exception as e:
        return {"error": str(e)}
    finally:
        # Limpar o dicionário para garantir que apenas o último certificado seja retido
        certificates.pop(cpf, None)

@app.get("/codigo/{codigo}/{cpf}")
def leve(codigo: str, cpf: str):
    if cpf not in certificates:
        return {"error": "CPF não encontrado."}

    generator = certificates[cpf]
    try:
        cert1, cert2 = generator.exchange_certs(codigo)
        cert_path = save_cert(cert1, (codigo + '.p12'))
        return {"mensagem": "Certificado Gerado com sucesso!", "certificado": cert_path}
    except Exception as e:
        return {"error": "Erro ao gerar certificado. Verifique os dados e tente novamente."}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=80)
