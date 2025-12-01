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
                raise Exception("Falha na autenticação")

        # Ajustar o EPIC para o formato da Capital (adiciona :US se necessário)
        if ":" not in epic:
            epic = f"{epic}:US"  # GS vira GS:US
        
        url = f"{self.base_url}/markets/{epic}"
        
        try:
            response = requests.get(url, headers={
                "X-CAP-API-KEY": self.api_key,
                "CST": self.cst,
                "X-SECURITY-TOKEN": self.x_security_token
            })
            
            if response.status_code != 200:
                raise Exception(f"Erro HTTP {response.status_code}: {response.text}")
            
            dados = response.json()
            
            # Extrair o preço (BID é o preço de venda/atual)
            preco_bid = dados.get('snapshot', {}).get('bid')
            
            if preco_bid is None:
                raise Exception(f"Preço não encontrado para {epic}")
            
            return preco_bid
            
        except Exception as e:
            raise Exception(f"Erro ao buscar {epic}: {str(e)}")
    
    @app.get("/descobrir-epic/{termo}") # type: ignore
    async def descobrir_epic(termo: str):
        """ Endpoint para descobrir o EPIC correto de uma ação Exemplo: /descobrir-epic/Microsoft"""
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
                resultados = response.json()
                
                # Formatar os resultados de forma legível
                epics_encontrados = []
                for item in resultados[:10]:  # Primeiros 10 resultados
                    epics_encontrados.append({
                        "epic": item.get('epic'),
                        "nome": item.get('instrumentName'),
                        "tipo": item.get('instrumentType')
                    })
                
                return {
                    "termo_buscado": termo,
                    "total_encontrados": len(resultados),
                    "resultados": epics_encontrados
                }
            else:
                return {"erro": f"HTTP {response.status_code}", "detalhes": response.text}
                
        except Exception as e:
            return {"erro": str(e)}




