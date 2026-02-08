import pytubefix
import ffmpeg
import sys
from dotenv import load_dotenv
from openai import OpenAI
import os

# 1. Configuração Inicial
client = OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    print ("API KEY não encontrada, verifique se o arquivo .env existe e se a chave está escrita corretamente!")
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
load_dotenv() # Isso carrega as variáveis do arquivo .env
url = sys.argv[1] # Recebe o link via terminal
filename = "audio.wav"



# 2. Extração do Áudio
print("Baixando áudio...")
yt = pytubefix.YouTube(url)
stream = yt.streams[0].url # Pega o endereço do fluxo de dados
ffmpeg.input(stream).output(filename, format='wav', loglevel="error").run(overwrite_output=True)

# 3. Transcrição (Whisper)
print("Transcrevendo...")
audio_file = open(filename, "rb") # Abre o áudio em modo binário
transcript = client.audio.transcriptions.create(
    model="whisper-1",
    file=audio_file
).text

# 4. Resumo e Análise (GPT-4o-mini)
print("Analisando com I.A...")
completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {
            "role": "system", 
            "content": "Você é um assistente que resume vídeos detalhadamente. Responda com formatação Markdown."
        },
        {
            "role": "user", 
            "content": f"Descreva o seguinte vídeo: {transcript}"
        }
    ]
)

# 5. Salvando o Resultado
with open("resumo.md", "w+", encoding="utf-8") as md:
    md.write(completion.choices[0].message.content)

print("Sucesso! O resumo foi salvo em 'resumo.md'.")