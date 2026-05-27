import csv
import os
import time
import urllib.parse
import requests
import random

# ================= CONFIGURAÇÕES =================
NOME_ARQUIVO_CSV = "prompts.csv"               
DIRETORIO_SAIDA = "new_imagens_geradas-ai"          
PAUSA_ENTRE_REQUISICOES = 3.0                # Aumentei para 3s para evitar bloqueios por excesso de requisições
LINHA_INICIAL = 1                          
MAX_TENTATIVAS = 3                           # Quantas vezes tentar de novo se der erro
# =================================================

def gerar_imagem_ia(palavra, frase, caminho_completo):
    estilo = "A simple children's painting style, naive art, cute, minimalist, colorful crayon drawing, clear definition"
    # prompt_completo = f"{estilo} depicting: {frase}. Focus on the concept of '{palavra}'."
    # prompt_completo = f"{estilo} depicting: {frase}."
    prompt_codificado = urllib.parse.quote(frase)
    
    # URL atualizada sem os parâmetros pagos (nologo e private). 
    # O seed aleatório garante que a IA gere uma nova imagem toda vez.
    semente = random.randint(1, 1000000)
    url = f"https://image.pollinations.ai/prompt/{prompt_codificado}?width=512&height=512&seed={semente}"
    
    for tentativa in range(1, MAX_TENTATIVAS + 1):
        try:
            # Aumentei o timeout para 60 segundos, pois a geração de IA às vezes demora
            resposta = requests.get(url, timeout=60)
            
            if resposta.status_code == 200:
                with open(caminho_completo, 'wb') as arquivo:
                    arquivo.write(resposta.content)
                    
                if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 0:
                    return True
            else:
                print(f" -> [ERRO {resposta.status_code}]", end="")
                
        except requests.exceptions.Timeout:
            print(f" -> [TIMEOUT na tentativa {tentativa}/{MAX_TENTATIVAS}]", end="")
        except Exception as e:
            print(f" -> [ERRO: {e}]", end="")
            
        # Se falhou, espera um pouco antes de tentar de novo
        if tentativa < MAX_TENTATIVAS:
            time.sleep(5)
            
    return False

def main():
    if not os.path.exists(DIRETORIO_SAIDA):
        os.makedirs(DIRETORIO_SAIDA)

    try:
        with open(NOME_ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo_entrada:
            leitor_csv = csv.reader(arquivo_entrada, delimiter='|')
            
            linhas = list(leitor_csv)
            total_linhas = len(linhas)
            print(f"Total de linhas encontradas no CSV: {total_linhas}")
            print("Iniciando geração de pinturas infantis por IA...\n" + "-"*50)
            
            for index, line in enumerate(linhas, start=LINHA_INICIAL):
                if len(line) >= 2:
                    palavra_en = line[0].strip()
                    frase_en = line[2].strip()
                    
                    nome_arquivo_img = f"{index:03d}_{palavra_en.replace(' ', '_').lower()}.jpg"
                    caminho_completo = os.path.join(DIRETORIO_SAIDA, nome_arquivo_img)
                    
                    print(f"[{index:03d}] Gerando arte para: '{palavra_en}'", end="", flush=True)
                    
                    if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 0:
                        print(" -> [IGNORADO - JÁ EXISTE]")
                        continue

                    sucesso = gerar_imagem_ia(palavra_en, frase_en, caminho_completo)
                    
                    if sucesso:
                        print(" -> [SUCESSO]")
                    else:
                        print(" -> [FALHA DEFINITIVA]")
                    
                    if index < (total_linhas + LINHA_INICIAL - 1):
                        time.sleep(PAUSA_ENTRE_REQUISICOES)
                        
            print("-"*50 + f"\nProcesso concluído! Artes salvas em '{DIRETORIO_SAIDA}'.")
            
    except FileNotFoundError:
        print(f"Erro: O arquivo {NOME_ARQUIVO_CSV} não foi encontrado.")

if __name__ == "__main__":
    main()