import json
import hashlib
import os

# Caminho do arquivo de usuários relativo ao diretório do script
USUARIOS_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.json')

def carregar_usuarios() -> dict:
    """Carrega usuários do arquivo JSON."""
    if os.path.exists(USUARIOS_PATH):
        with open(USUARIOS_PATH, 'r') as f:
            return json.load(f)
    return {}

def salvar_usuario(usuario: str, senha: str) -> None:
    """
    Salva um novo usuário com senha hasheada.
    
    Args:
        usuario: Nome do usuário
        senha: Senha em texto plano
    """
    usuarios = carregar_usuarios()
    usuarios[usuario] = hashlib.sha256(senha.encode()).hexdigest()
    
    # Garante que o diretório existe
    os.makedirs(os.path.dirname(USUARIOS_PATH), exist_ok=True)
    
    with open(USUARIOS_PATH, 'w') as f:
        json.dump(usuarios, f, indent=4)

def autenticar(usuario: str, senha: str, usuarios: dict) -> bool:
    """
    Autentica um usuário.
    
    Args:
        usuario: Nome do usuário
        senha: Senha em texto plano
        usuarios: Dicionário de usuários e senhas hasheadas
    
    Returns:
        bool: True se autenticação bem sucedida, False caso contrário
    """
    if usuario not in usuarios:
        return False
    
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    return senha_hash == usuarios[usuario]
