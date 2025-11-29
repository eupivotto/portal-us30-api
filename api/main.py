from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from .capital_client import CapitalClient



# Carrega as senhas do arquivo .env
load_dotenv()

app = FastAPI()

# Permite que o Front converse com esse Back
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Status": "Online", "Dono": "Trader US30"}

@app.get("/dados-elite")
def pegar_dados():
    # AQUI nós usamos a chave que está escondida no .env
    api_key = os.getenv("CAPITAL_API_KEY")
    
    # (Aqui virá a lógica real de conexão com a Capital.com depois)
    # Por enquanto, vamos simular para testar a estrutura
    return {
        "Goldman_Sachs": {"preco": 825.50, "viés": "COMPRA"},
        "Caterpillar": {"preco": 575.80, "viés": "COMPRA"},
        "Info_Secreta": f"Estou usando a chave que começa com: {api_key[:4]}..."
    }
@app.get("/teste-btc")
def teste_btc():
    cliente = CapitalClient()
    resultado = cliente.testar_conexao_btc()
    return resultado
