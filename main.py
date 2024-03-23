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






def generate_random_id() -> str:
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=12))


def log(message, color=Fore.BLUE):
    print(f'{color}{Style.DIM}[*] {Style.NORMAL}{Fore.LIGHTBLUE_EX}{message}')


def save_cert(cert, name):
    path = os.path.join(os.getcwd(), name)
    with open(path, 'wb') as cert_file:
        cert_file.write(cert.export())




app = FastAPI()




@app.get("/")
def root():
    return {"Dev": "PLAY7:(2799570-0396)"}

class codigo(BaseModel):
    id: int
    codigo: str

class saldo(BaseModel):
    cpf: int
    senha: str
    certificado: str


class usuario(BaseModel):
    cpf: int
    senha: str
    
class HttpClientWithPassword(HttpClient):
    def _cert_args(self):
        return {'pkcs12_data': self._cert, 'pkcs12_password': 'nubank'}



generators = []

junto = {}

junto = []


def save_to_log(message):
    with open('log.txt', 'a') as file:
        file.write(message + '\n')




@app.get("/certificado/{cpf}/{senha}")
def certificadoleve(cpf:str, senha:str):
    init()

    device_id = generate_random_id()

    cpf = cpf
    password = senha

    generator = CertificateGenerator(cpf, password, device_id)

    junto2 = {cpf : {"cpf": cpf, "chave": generator}}
    
    try:
        email = generator.request_code() 
    except NuException:
        return


    for i, item in enumerate(junto):
        if cpf in item:
            junto.pop(i)
            break

    junto.append(junto2)
    
    return {"email": email}
    
@app.get("/codigo/{codigo}/{cpf}")
def leve(codigo: str, cpf: str):
    for item in junto:
        if cpf in item:
            if "chave" in item[cpf]:
                chave = item[cpf]["chave"]
                try:
                    cert1, cert2 = chave.exchange_certs(codigo)
                    save_cert(cert1, (codigo+'.p12'))
                    return {"mensagem": "Play7Server - Certificado Gerado com sucesso!"}
                except Exception as e:
                    return {"error": "Erro ao gerar certificado. Verifique os dados e tente novamente."}
            else:
                return {"error": "Chave não encontrada para este CPF."}
        else:
            return {"error": "CPF não encontrado."}


@app.get("/perfilcompleto/{cpf}/{senha}/{certificado}")
def obter_perfilcompleto(cpf: str, senha: str, certificado: str):
    nu = Nubank()
    nu.authenticate_with_cert(cpf, senha, certificado)
    # debito = nu.get_account_balance()
    # perfil = nu.get_customer()
    info_card = nu.get_credit_card_balance()
    
    limite_disponivel = info_card.get('available', 'Limite disponivel não encontrado')
    
    fatura_atual = info_card.get('open', 'Fatura atual não encontrado')


    
    proximas_faturas = info_card.get('future', 'Fatura atual não encontrado')
    
    return {"limitedisponivel": info_card
            }





 
if __name__ == '__main__':
    main()
   
    #save_cert(cert1, 'cert.p12')

    #print(f'{Fore.GREEN}Certificates generated successfully. (cert.pem)')
    #print(f'{Fore.YELLOW}Warning, keep these certificates safe (Do not share or version in git)')


