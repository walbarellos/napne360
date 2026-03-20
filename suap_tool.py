import httpx
import json
import os
import sys
from datetime import datetime

# Adiciona o backend ao path para garantir que os imports funcionem se rodar da raiz
sys.path.append(os.path.join(os.path.dirname(__file__)))

def log_output(content, filename="auditoria_suap.txt"):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(filename, "a", encoding="utf-8") as f:
        f.write(f"\n{'='*50}\n")
        f.write(f"DATA: {timestamp}\n")
        f.write(content + "\n")
    print(content)

def testar_integracao(matricula_aluno, suap_user, suap_pass):
    base_url = "http://localhost:8000"
    client = httpx.Client(base_url=base_url, timeout=40.0)
    
    output = []
    output.append(">>> INICIANDO TESTE DE INTEGRAÇÃO NAPNE 360 <<<")

    try:
        # 1. Login no NAPNE 360 (Admin)
        output.append("1. Autenticando Admin local...")
        login = client.post("/auth/login", data={"username": "admin@napne.local", "password": "admin123"})
        
        if login.status_code != 200:
            output.append(f"ERRO LOGIN ADMIN: {login.text}")
            log_output("\n".join(output))
            return

        token = login.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        output.append("Sucesso: Admin autenticado.")

        # 2. Cadastro de Estudante via SUAP
        output.append(f"\n2. Solicitando matrícula do aluno {matricula_aluno} via SUAP...")
        payload = {
            "matricula_suap": matricula_aluno,
            "declarou_necessidade": True,
            "modalidade": "superior",
            "suap_username": suap_user,
            "suap_password": suap_pass
        }
        
        res = client.post("/matriculas/", json=payload, headers=headers)
        
        output.append(f"STATUS HTTP: {res.status_code}")
        response_data = res.json()
        output.append("RETORNO DA API:")
        output.append(json.dumps(response_data, indent=2, ensure_ascii=False))

        if res.status_code == 200:
            output.append("\n✅ SUCESSO: Estudante cadastrado e Dossiê iniciado.")
        else:
            output.append("\n❌ FALHA: Verifique os logs do servidor.")

    except Exception as e:
        output.append(f"ERRO CRÍTICO: {str(e)}")

    final_log = "\n".join(output)
    log_output(final_log)
    print(f"\n[!] Resultado detalhado salvo em: auditoria_suap.txt")

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Uso: python suap_tool.py <MATRICULA_ALUNO> <USER_SUAP> <PASS_SUAP>")
        print("Ex: python suap_tool.py 20261CRB12697480019 20261CRB12697480019 MinhaSenha123")
    else:
        testar_integracao(sys.argv[1], sys.argv[2], sys.argv[3])
