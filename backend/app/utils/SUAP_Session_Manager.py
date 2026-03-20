from cryptography.fernet import Fernet
import os

FERNET_KEY = os.getenv("FERNET_KEY")
if not FERNET_KEY:
    # Se por algum motivo não estiver no env, gera uma temporária (não recomendado para persistência)
    FERNET_KEY = Fernet.generate_key()
else:
    FERNET_KEY = FERNET_KEY.encode()

fernet = Fernet(FERNET_KEY)

def encriptar_session(session_id: str) -> str:
    return fernet.encrypt(session_id.encode()).decode()

def decriptar_session(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()
