import csv
import asyncio
import edge_tts
import os
import time

# ================= CONFIGURAÇÕES =================
NOME_ARQUIVO_CSV = "novos-anki-cards.csv"  # Substitua pelo nome do seu CSV
DIRETORIO_SAIDA = "new_audios_gerados"
VOZ = "en-US-AriaNeural"  # Para voz masculina use "en-US-GuyNeural"
PAUSA_ENTRE_AUDIOS = 1.0  # Tempo em segundos para esperar entre um áudio e outro
# =================================================

async def gerar_audio_sequencial(palavra, frase, linha_idx):
    texto_para_falar = f"{palavra}... {frase}"
    nome_arquivo = f"{linha_idx:03d}_{palavra.replace(' ', '_').lower()}.mp3"
    caminho_completo = os.path.join(DIRETORIO_SAIDA, nome_arquivo)
    
    print(f"[{linha_idx:03d}] Processando: {palavra}...", end="", flush=True)
    
    try:
        # Inicializa o comunicador do Edge TTS
        comunicador = edge_tts.Communicate(texto_para_falar, VOZ)
        
        # O 'await' aqui garante que ele ESPERA o download terminar completamente antes de avançar
        await comunicador.save(caminho_completo)
        
        # Validação de segurança: Verifica se o arquivo foi criado e não está vazio
        if os.path.exists(caminho_completo) and os.path.getsize(caminho_completo) > 0:
            print(" -> [SUCESSO]")
            return True
        else:
            print(" -> [ERRO: Arquivo gerado vazio]")
            return False
            
    except Exception as e:
        print(f" -> [FALHA: {e}]")
        return False

async def main():
    if not os.path.exists(DIRETORIO_SAIDA):
        os.makedirs(DIRETORIO_SAIDA)

    try:
        with open(NOME_ARQUIVO_CSV, mode='r', encoding='utf-8') as arquivo:
            leitor_csv = csv.reader(arquivo, delimiter='|') 
            
            linhas = list(leitor_csv)
            total_linhas = len(linhas)
            print(f"Total de linhas encontradas no CSV: {total_linhas}")
            print("Iniciando geração sequencial segura...\n" + "-"*50)
            
            for index, linha in enumerate(linhas, start=1):
                if len(linha) >= 2:
                    palavra = linha[0].strip()
                    frase = linha[1].strip()
                    
                    # Executa e aguarda a conclusão definitiva deste áudio
                    sucesso = await gerar_audio_sequencial(palavra, frase, index)
                    
                    # Se não for a última linha, dá uma pausa respiratória para a API
                    if index < total_linhas:
                        time.sleep(PAUSA_ENTRE_AUDIOS)
                        
            print("-"*50 + "\nProcesso concluído com segurança!")
            
    except FileNotFoundError:
        print(f"Erro: O arquivo {NOME_ARQUIVO_CSV} não foi encontrado.")

if __name__ == "__main__":
    asyncio.run(main())