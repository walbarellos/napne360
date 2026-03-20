import httpx

# Configurações
BASE_URL = "https://suap.ifac.edu.br"
USERNAME = "20261CRB12697480019"
PASSWORD = "Albarello5050!50!"

client = httpx.Client(base_url=BASE_URL, follow_redirects=True)

print(f"Tentando login em {BASE_URL}...")

# Passo 1 — Obter CSRF token
r = client.get("/accounts/login/")
csrf = client.cookies.get("__Host-csrftoken") or client.cookies.get("csrftoken")

# Passo 2 — Realizar Login
r = client.post("/accounts/login/", data={
    "username": USERNAME,
    "password": PASSWORD,
    "csrfmiddlewaretoken": csrf,
    "next": "/"
}, headers={"Referer": f"{BASE_URL}/accounts/login/"})

# No IFAC, o cookie de sessão costuma ser __Host-sessionid
session_id = client.cookies.get("__Host-sessionid") or client.cookies.get("sessionid")

if session_id:
    print("Login realizado com sucesso!")
    
    # Endpoints descobertos que funcionam nesta instância do SUAP (Django Ninja)
    endpoints = {
        "Dados Básicos": "/api/eu/",
        "Meus Dados Detalhados": "/api/v2/minhas-informacoes/meus-dados/",
        "Dados Acadêmicos": "/api/edu/meus-dados-aluno/",
    }

    for label, url in endpoints.items():
        print(f"\n--- {label} ({url}) ---")
        res = client.get(url)
        if res.status_code == 200:
            data = res.json()
            # Mostra apenas alguns campos para não poluir
            if "nome" in data: print(f"Nome: {data['nome']}")
            if "matricula" in data: print(f"Matrícula: {data['matricula']}")
            if "curso" in data: print(f"Curso: {data['curso']}")
            if "situacao" in data: print(f"Situação: {data['situacao']}")
        else:
            print(f"Erro {res.status_code} ao acessar endpoint.")

else:
    print("Falha no login. Verifique as credenciais.")
