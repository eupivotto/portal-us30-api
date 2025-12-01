import requests
import os

class CapitalClient:
    def __init__(self):
        self.base_url = "https://api-capital.backend-capital.com/api/v1"
        self.email = os.getenv("CAPITAL_EMAIL")
        self.api_key = os.getenv("CAPITAL_API_KEY")
        self.password = os.getenv("CAPITAL_PASSWORD")
        self.cst = None
        self.x_security_token = None

    def autenticar(self):
        """Faz login e guarda os tokens de sessão CST e X-SECURITY-TOKEN"""
        url = f"{self.base_url}/session"
        payload = {
            "identifier": self.email,
            "password": self.password
        }
        headers = {
            "X-CAP-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }

        try:
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                # SUCESSO! Pegamos os tokens
                self.cst = response.headers.get("CST")
                self.x_security_token = response.headers.get("X-SECURITY-TOKEN")
                print("✅ Login na Capital realizado com sucesso!")
                return True
            else:
                print(f"❌ Erro no login: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Erro de conexão: {e}")
            return False

    def pegar_precos_elite(self):
        """Busca os preços de GS, UNH, CAT e US30"""
        if not self.cst:
            if not self.autenticar():
                return None

        # Lista de ativos para buscar (EPICs da Capital)
        # GS = Goldman, UNH = UnitedHealth, CAT = Caterpillar, US30 = US30
        epics = "GS:US,UNH:US,CAT:US,US30" 
        
        url = f"{self.base_url}/market/navigation/breadth?epics={epics}" # Endpoint hipotético, vamos ajustar
        # NOTA: A Capital tem endpoints chatos. O melhor é usar o /markets para pegar detalhes
        
        # Vamos usar uma busca simples primeiro para testar
        # Como não dá pra testar sem mercado aberto, vamos deixar a estrutura pronta
        return {
            "status": "MERCADO_FECHADO",
            "nota": "Implementaremos a busca real de preços na segunda-feira"
        }
        
    def testar_conexao_btc(self):
        """Busca o preço do BITCOIN (Mercado Aberto 24h) para teste"""
        if not self.cst:
            if not self.autenticar():
                return {"erro": "Falha na autenticação"}

        # Endpoint para buscar preços de mercado
        # Epic do Bitcoin na Capital costuma ser 'BTCUSD'
        epic = "BTCUSD" 
        url = f"{self.base_url}/markets/{epic}"

        try:
            response = requests.get(url, headers={
                "X-CAP-API-KEY": self.api_key,
                "CST": self.cst,
                "X-SECURITY-TOKEN": self.x_security_token
            })
            
            dados = response.json()
            
            # Vamos ver se a API retornou o que esperamos
            if 'dealingRules' in dados: # Se tiver regras, achou o ativo
                # O preço geralmente vem em 'snapshot'
                preco_bid = dados.get('snapshot', {}).get('bid')
                preco_ask = dados.get('snapshot', {}).get('offer')
                
                return {
                    "ativo": "Bitcoin (Teste 24h)",
                    "preco_atual": preco_bid,
                    "status": "CONECTADO ✅"
                }
            else:
                return {"erro": "Não achou o BTC", "debug": dados}

        except Exception as e:
            return {"erro": f"Erro na requisição: {e}"}
    
    def buscar_preco(self, epic):
        """Busca o preço de qualquer ativo pelo EPIC"""
        if not self.cst:
            if not self.autenticar():
                return None
        
        # Usar o endpoint de busca que já sabemos que funciona
        url = f"{self.base_url}/markets"
        params = {"searchTerm": epic, "epics": epic}
        
        try:
            response = requests.get(url, params=params, headers={
                "X-CAP-API-KEY": self.api_key,
                "CST": self.cst,
                "X-SECURITY-TOKEN": self.x_security_token
            })
            
            if response.status_code == 200:
                dados = response.json()
                
                # A resposta vem em formato dict com chave "markets"
                markets = dados.get('markets', [])
                
                if markets and len(markets) > 0:
                    item = markets[0]
                    bid = item.get('bid')
                    offer = item.get('offer')
                    
                    # Retornar o preço médio
                    if bid and offer:
                        return round((bid + offer) / 2, 2)
                    elif bid:
                        return round(bid, 2)
                
                return None
            else:
                return None
                
        except Exception as e:
            return None
