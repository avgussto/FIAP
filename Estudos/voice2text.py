import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import numpy as np
import pandas as pd
import nltk
from more_itertools.recipes import padnone
from nltk import download
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import CountVectorizer
import whisper
from pydub import AudioSegment
import os

# Baixa e carrega as stopwords em português (palavras comuns que serão ignoradas no processamento)
nltk.download('stopwords')
stop_words_br = stopwords.words('portuguese')

# Lista de palavras "mágicas" (palavras importantes que serão destacadas)
palavras_magicas = ['obrigado', 'obrigada', 'por favor', 'desculpa', 'desculpe', 'por gentileza', 'bom dia',
                    'boa tarde', 'boa noite', 'agradeço', 'agradece', 'gratidão', 'sinto muito', 'perdão', 'me perdoe', 'com licença']

# Carrega o modelo de transcrição Whisper
model = whisper.load_model("base")

# Função para carregar um arquivo de áudio
def carregar_audio(label_nome_audio):
    arquivo = filedialog.askopenfile(filetypes=[("Audio files", "*.wav;*.mp3;*.flac;*.aac")])  # Abre janela para escolher arquivo
    if arquivo:
        audio = AudioSegment.from_file(arquivo.name)  # Carrega o áudio
        nome_sem_path = os.path.basename(arquivo.name)  # Pega o nome do arquivo sem o caminho completo
        label_nome_audio.configure(text=f'Arquivo selecionado: {nome_sem_path}')  # Mostra o nome do arquivo na interface
        return audio, arquivo.name  # Retorna o áudio e o nome do arquivo
    return None, None  # Se não houver arquivo, retorna None

# Função para calcular a duração do áudio
def duracao_audio(audio):
    try:
        duracao = len(audio) / 1000  # Converte a duração para segundos
        return duracao
    except Exception as e:
        print(f"Erro ao pegar a duração do áudio: {e}")
        return None

# Função para transcrever o áudio usando o Whisper
def transcricao(audio):
    try:
        resultado = model.transcribe(audio)  # Transcreve o áudio
        texto = resultado["text"]  # Pega o texto transcrito
        return texto
    except Exception as e:
        print(f"Erro ao transcrever o áudio: {e}")
        return None

# Função principal que processa o áudio, transcreve e exibe as estatísticas
def processamento(label_duracao, texto_transcricao_box, label_nome_audio, label_estatistica_box):
    audio, nome_arquivo = carregar_audio(label_nome_audio)  # Carrega o áudio
    if audio:
        duracao = duracao_audio(audio)  # Pega a duração do áudio
        texto = transcricao(nome_arquivo)  # Transcreve o áudio

        # Vetoriza o texto transcrito, ignorando as stopwords
        vectorizer = CountVectorizer(stop_words=stop_words_br)
        matrix = vectorizer.fit_transform([texto])

        # Calcula estatísticas básicas
        total_palavras = len(vectorizer.get_feature_names_out())  # Número total de palavras
        palavras_por_min = total_palavras / (duracao / 60)  # Palavras por minuto

        lista_palavras = vectorizer.get_feature_names_out()  # Lista de palavras

        # Conta a frequência de cada palavra
        contagem_palavras = np.asarray(matrix.sum(axis=0)).flatten()

        # Cria um dicionário de palavras e suas frequências
        freq_palavras = dict(zip(lista_palavras, contagem_palavras))
        freq_palavras_ordenada = sorted(freq_palavras.items(), key=lambda x: x[1], reverse=True)  # Ordena por frequência

        # Calcula o percentual de palavras "mágicas" no texto
        freq_palavras_df = pd.DataFrame(freq_palavras_ordenada, columns=['Palavra', 'Frequência'])
        percentual_palavras_magicas = sum(
            freq_palavras_df[freq_palavras_df['Palavra'].isin(palavras_magicas)]['Frequência']) / total_palavras * 100
        percentual_palavras_magicas = round(percentual_palavras_magicas)

        # Atualiza a interface com a duração e as estatísticas calculadas
        label_duracao.configure(text=f"Duração: {duracao} segundos")
        lista_palavras_formatadas = [f"{palavra}: {frequencia}" for palavra, frequencia in freq_palavras_ordenada]
        estatistica_texto = (f"Número total de palavras no texto: {total_palavras}\n\n"
                             f"Palavras por minuto: {palavras_por_min:.2f}\n\n"
                             f"Percentual de palavras mágicas: {percentual_palavras_magicas}%\n\n"
                             f"Lista das palavras que mais aparecem:\n" + "\n".join(lista_palavras_formatadas))

        # Exibe as estatísticas e a transcrição na interface
        label_estatistica_box.delete("1.0", tk.END)
        label_estatistica_box.insert(tk.END, estatistica_texto)

        texto_transcricao_box.delete("1.0", tk.END)
        texto_transcricao_box.insert(tk.END, texto)

    else:
        print("Nenhum áudio carregado.")

# Função principal que cria a interface gráfica
def app():
    # Configurações iniciais do tema da interface
    ctk.set_appearance_mode('System')
    ctk.set_default_color_theme('blue')

    # Cria a janela principal
    root = ctk.CTk()
    root.geometry("1920x1080")
    root.title("Voice2Text")

    # Cria o Frame principal que suporta scroll
    main_frame = ctk.CTkScrollableFrame(root, orientation="vertical", width=1080, height=1920)
    main_frame.pack(fill=ctk.BOTH, expand=1)

    # Label do título com fonte maior
    label_titulo = ctk.CTkLabel(main_frame, text="Voice2Text", font=("Arial", 24))
    label_titulo.pack(pady=10)

    # Label do aviso com fonte menor
    label_aviso = ctk.CTkLabel(main_frame, text="AVISO: Dependendo da qualidade do áudio, a qualidade transcrição pode ser deteriorada, tenha isso em mente.", font=("Arial", 12))
    label_aviso.pack()

    # Label que mostra a duração do áudio
    label_duracao = ctk.CTkLabel(main_frame, text="")

    # Caixa de texto para exibir a transcrição, com largura e altura ajustadas
    texto_transcricao_box = ctk.CTkTextbox(main_frame, height=300, wrap="word", width=1000)

    # Botão para carregar o áudio
    botao_carregar = ctk.CTkButton(main_frame, text="Carregar Áudio",
                                   command=lambda: processamento(label_duracao, texto_transcricao_box, label_nome_audio, estatistica_box))
    botao_carregar.pack(pady=20)

    # Label que mostra o nome do áudio selecionado
    label_nome_audio = ctk.CTkLabel(main_frame, text="Nenhum áudio selecionado")
    label_nome_audio.pack()

    # Label que mostra a duração do áudio
    label_duracao.pack(pady=5)

    # Label para indicar a seção da transcrição
    label_transcricao = ctk.CTkLabel(main_frame, text="Transcrição do Áudio")
    label_transcricao.pack()

    # Caixa de texto onde a transcrição do áudio será exibida
    texto_transcricao_box.pack(pady=10)

    # Label para indicar a seção de estatísticas
    label_estatistica_titulo = ctk.CTkLabel(main_frame, text="Algumas informações sobre o áudio carregado")
    label_estatistica_titulo.pack(pady=10)

    # Caixa de texto onde as estatísticas serão exibidas
    estatistica_box = ctk.CTkTextbox(main_frame, height=150, width=600)
    estatistica_box.pack(pady=10)

    # Inicia o loop da aplicação
    root.mainloop()

# Executa a aplicação
app()
