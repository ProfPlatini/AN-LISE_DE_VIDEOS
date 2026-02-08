import pytubefix
import ffmpeg
import sys
import os
from dotenv import load_dotenv
from openai import OpenAI

# ==========================================================
# 1. CONFIGURAÇÃO INICIAL (A ORDEM IMPORTA!)
# ==========================================================

# 1º Passo: Carrega o arquivo .env
load_dotenv() 

# 2º Passo: Pega a chave que agora já está na memória
api_key = os.getenv("OPENAI_API_KEY")

# 3º Passo: Verifica se a chave foi encontrada
if not api_key:
    print("❌ ERRO: OPENAI_API_KEY não encontrada no arquivo .env!")
    print("Verifique se o arquivo .env está salvo corretamente.")
    sys.exit()

# 4º Passo: Inicializa o cliente com a chave válida
client = OpenAI(api_key=api_key)

# 5º Passo: Valida o link do terminal
if len(sys.argv) < 2:
    print("❌ Erro: Forneça o link do YouTube.")
    print('Exemplo: python app.py "https://www.youtube.com/..."')
    sys.exit()

url = sys.argv[1]
filename = "audio.wav"

# ==========================================================
# 2. EXTRAÇÃO E PROCESSAMENTO
# ==========================================================

print("1/4 - Baixando áudio...")
try:
    yt = pytubefix.YouTube(url)
    stream = yt.streams.get_audio_only().url
    ffmpeg.input(stream).output(filename, format='wav', loglevel="error").run(overwrite_output=True)
except Exception as e:
    print(f"❌ Erro no download/ffmpeg: {e}")
    sys.exit()

print("2/4 - Transcrevendo (Whisper)...")
with open(filename, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file
    ).text

print("3/4 - Resumindo (GPT-4o-mini)...")
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "Você resume vídeos em Markdown."},
        {"role": "user", "content": f"Resuma o seguinte conteúdo: {transcript}"}
    ]
)

print("4/4 - Salvando resultado...")
with open("resumo.md", "w+", encoding="utf-8") as md:
    md.write(completion.choices[0].message.content)

print("\n✅ Concluído! Verifique o arquivo 'resumo.md'.")