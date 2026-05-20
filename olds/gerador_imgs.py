import csv
import os
import time
import requests

# ================= CONFIGURAÇÕES =================
NOME_ARQUIVO_CSV = "cards.csv"               # Nome do seu CSV original
DIRETORIO_SAIDA = "imagens_geradas"          # Pasta onde as imagens serão salvas
API_KEY_PEXELS = "kUdCv3vS4UrZZCapqADkZi4MwpxzxvW8WMVUYb2KBZtlINNRZr4JkM2T"    # Substitua pela sua chave gratuita do Pexels
PAUSA_ENTRE_REQUISICOES = 1.0                # Pausa para evitar bloqueio da API
LINHA_INICIAL = 1                            # Altere se quiser começar a numeração de outro valor (ex: 3201)
# =================================================

def buscar_url_imagem(palavra):
    """Consulta a API do Pexels e retorna a URL da primeira imagem relevante."""
    headers = {"Authorization": API_KEY_PEXELS}
    url = f"https://api.pexels.com/v1/search?query={palavra}&per_page=1"
    
    try:
        resposta = requests.get(url, headers=headers)
        resposta.raise_for_status()
        dados = resposta.json()
        
        if dados.get("photos"):
            # Pega a versão "medium" para ter boa qualidade sem pesar muito
            return dados["photos"][0]["src"]["medium"]
    except Exception:
        pass
    return None

def baixar_imagem(url, caminho_completo):
    """Faz o download da imagem e salva no disco."""
    try:
        resposta = requests.get(url, stream=True)
        resposta.raise_for_status()
        
        with open(caminho_completo, 'wb') as arquivo:
            for chunk in resposta.iter_content(1024):
                arquivo.write(chunk)
                
        # Validação: Verifica se o arquivo foi criado e não está vazio
        if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 0:
            return True
    except Exception:
        pass
    return False

def main():
    if not os.path.exists(DIRETORIO_SAIDA):
        os.makedirs(DIRETORIO_SAIDA)

    try:
        with open(NOME_ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo_entrada:
            leitor_csv = csv.reader(arquivo_entrada, delimiter=',')
            
            linhas = list(leitor_csv)
            total_linhas = len(linhas)
            print(f"Total de linhas encontradas no CSV: {total_linhas}")
            print("Iniciando download sequencial de imagens...\n" + "-"*50)
            
            for index, linha in enumerate(linhas, start=LINHA_INICIAL):
                # Precisa apenas da primeira coluna (a palavra)
                if len(linha) >= 1:
                    palavra_en = linha[0].strip()
                    
                    # Aplica a mesma lógica de nomenclatura do áudio: 001_palavra.jpg
                    nome_arquivo_img = f"{index:03d}_{palavra_en.replace(' ', '_').lower()}.jpg"
                    caminho_completo = os.path.join(DIRETORIO_SAIDA, nome_arquivo_img)
                    
                    print(f"[{index:03d}] Processando: {palavra_en}...", end="", flush=True)
                    
                    # Evita refazer o download se o arquivo já existir (útil se o script for interrompido)
                    if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 0:
                        print(" -> [IGNORADO - JÁ EXISTE]")
                        continue

                    url_img = buscar_url_imagem(palavra_en)
                    sucesso = False
                    
                    if url_img:
                        sucesso = baixar_imagem(url_img, caminho_completo)
                    
                    if sucesso:
                        print(" -> [SUCESSO]")
                    else:
                        print(" -> [FALHA/NÃO ENCONTRADA]")
                    
                    # Pausa para não estourar o limite da API
                    if index < (total_linhas + LINHA_INICIAL - 1):
                        time.sleep(PAUSA_ENTRE_REQUISICOES)
                        
            print("-"*50 + f"\nProcesso concluído! Imagens salvas em '{DIRETORIO_SAIDA}'.")
            
    except FileNotFoundError:
        print(f"Erro: O arquivo {NOME_ARQUIVO_CSV} não foi encontrado.")

if __name__ == "__main__":
    main()