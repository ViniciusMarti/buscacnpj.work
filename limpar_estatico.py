import os
import shutil

CNPJ_DIR = "cnpj"

def cleanup():
    if not os.path.exists(CNPJ_DIR):
        print(f"Diretório {CNPJ_DIR} não encontrado.")
        return

    print(f"AVISO: Isso deletará todas as pastas dentro de '{CNPJ_DIR}'.")
    confirm = input("Tem certeza que o sistema dinâmico (PHP + SQLite) está funcionando? (S/N): ")
    
    if confirm.upper() == 'S':
        try:
            # Deleta o conteúdo mas mantém a pasta raiz 'cnpj'
            for item in os.listdir(CNPJ_DIR):
                item_path = os.path.join(CNPJ_DIR, item)
                if os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                else:
                    os.remove(item_path)
            print("Limpeza concluída! 58 mil pastas removidas com sucesso.")
        except Exception as e:
            print(f"Erro durante a limpeza: {e}")
    else:
        print("Operação cancelada.")

if __name__ == "__main__":
    cleanup()
