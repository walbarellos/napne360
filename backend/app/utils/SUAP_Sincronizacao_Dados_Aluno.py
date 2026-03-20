import httpx

async def buscar_dados_suap(username: str, password: str) -> dict:
    base = "https://suap.ifac.edu.br"
    async with httpx.AsyncClient(base_url=base, follow_redirects=True) as client:
        # 1. Pega o CSRF
        await client.get("/accounts/login/")
        csrf = client.cookies.get("__Host-csrftoken") or client.cookies.get("csrftoken")
        
        # 2. Faz o Login
        login_res = await client.post("/accounts/login/", data={
            "username": username,
            "password": password,
            "csrfmiddlewaretoken": csrf,
            "next": "/"
        }, headers={"Referer": f"{base}/accounts/login/"})

        if "__Host-sessionid" not in client.cookies and "sessionid" not in client.cookies:
             raise Exception("Falha na autenticação com o SUAP. Verifique as credenciais.")

        # 3. Consome a API Django Ninja do IFAC
        res_eu = await client.get("/api/eu/")
        res_acad = await client.get("/api/edu/meus-dados-aluno/")
        
        if res_eu.status_code != 200 or res_acad.status_code != 200:
            raise Exception(f"Erro ao buscar dados no SUAP: EU({res_eu.status_code}) ACAD({res_acad.status_code})")
            
        eu = res_eu.json()
        acad = res_acad.json()

    # Mapeia para o formato interno do NAPNE 360
    return {
        "nome"     : eu.get("nome_social") or eu.get("nome") or eu.get("nome_registro"),
        "matricula": eu["identificacao"],
        "cpf"      : eu.get("cpf", "").replace(".", "").replace("-", ""),
        "email"    : eu.get("email_preferencial") or eu.get("email"),
        "campus"   : eu.get("campus"),
        "curso"    : acad.get("curso"),
        "periodo"  : acad.get("periodo_referencia"),
        "ira"      : float(acad.get("ira", "0").replace(",", ".")),
        "situacao" : acad.get("situacao"),
    }
