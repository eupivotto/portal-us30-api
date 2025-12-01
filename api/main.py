from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
import requests
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

@app.get("/elite")
async def pegar_dados_elite():
    """
    Retorna os preços das ações que comandam o US30
    (Goldman Sachs, UnitedHealth, Caterpillar, Microsoft, Home Depot, McDonald's)
    """
    try:
        client = CapitalClient()
        client.autenticar()

        
        # Lista das "Donas do Índice" (os EPICs da Capital.com)
        acoes_elite = {
            "Goldman_Sachs": "GS",      # Epic: GS
            "UnitedHealth": "UNH",      # Epic: UNH
            "Caterpillar": "CAT",       # Epic: CAT
            "Microsoft": "MSFT",        # Epic: MSFT
            "Home_Depot": "HD",         # Epic: HD
            "McDonalds": "MCD"          # Epic: MCD
        }
        
        dados = {}
        
        for nome, epic in acoes_elite.items():
            try:
                preco = client.buscar_preco(epic)
                dados[nome] = {
                    "preco": preco,
                    "epic": epic
                }
            except Exception as e:
                dados[nome] = {
                    "preco": None,
                    "erro": str(e)
                }
        
        return {
            "status": "CONECTADO ✅",
            "timestamp": "Tempo Real",
            "dados": dados
        }
        
    except Exception as e:
        return {
            "status": "ERRO ❌",
            "mensagem": str(e)
        }
@app.get("/descobrir-epic/{termo}")
async def descobrir_epic(termo: str):
    """
    Endpoint para descobrir o EPIC correto de uma ação
    Exemplo: /descobrir-epic/Microsoft
    """
    try:
        client = CapitalClient()
        client.autenticar()
        
        url = f"{client.base_url}/markets"
        params = {"searchTerm": termo}
        
        response = requests.get(url, params=params, headers={
            "X-CAP-API-KEY": client.api_key,
            "CST": client.cst,
            "X-SECURITY-TOKEN": client.x_security_token
        })
        
        if response.status_code == 200:
            dados = response.json()
            
            # Debug: mostrar a estrutura real da resposta
            if not isinstance(dados, list):
                return {
                    "debug": "Resposta não é uma lista",
                    "tipo": str(type(dados)),
                    "conteudo": dados
                }
            
            # Formatar os resultados
            epics_encontrados = []
            for item in dados[:10]:
                epics_encontrados.append({
                    "epic": item.get('epic'),
                    "nome": item.get('instrumentName'),
                    "tipo": item.get('instrumentType')
                })
            
            return {
                "termo_buscado": termo,
                "total_encontrados": len(dados),
                "resultados": epics_encontrados
            }
        else:
            return {"erro": f"HTTP {response.status_code}", "detalhes": response.text}
            
    except Exception as e:
        return {"erro": str(e)}

