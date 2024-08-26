import speech_recognition as sr
import pyaudio
import pyttsx3
import os

rec = sr.Recognizer()

def falar_ana(texto):
    ana.say(texto)
    ana.runAndWait()
    print(texto)

def falar_user():
    with sr.Microphone() as mic:
        rec.adjust_for_ambient_noise(mic, duration=1)
        audio = rec.listen(mic, timeout=15)
        texto = rec.recognize_google(audio, language='pt')

    print(texto)
    return texto

def criar_arquivo():
    topicos = "\n".join([f"- {evento}" for evento in eventos])

    caminho_area_de_trabalho = os.path.join(os.path.expanduser("~"), "Desktop", "eventos.txt")

    with open(caminho_area_de_trabalho, "w", encoding="utf-8") as arquivo:
        arquivo.write(topicos)

    falar_ana("Os eventos foram salvos na sua área de trabalho.")

def parar_continuar():
    falar_ana('Algo mais que deseja fazer? Responda positivo para continuarmos')
    continuar = falar_user()

    return continuar

ana = pyttsx3.init()
ana.setProperty('rate', 180)
ana.setProperty('volume', 0.7)

eventos = []
fala_inical = falar_user()

#ajeitar variaveis para poder aceitar mais variacao de texto
while True:
    if fala_inical.lower() == 'olá ana':
        falar_ana('Olá usuário, o que posso fazer por você?')

        user = falar_user()
        if any(palavra in user.lower() for palavra in ['cadastrar', 'evento', 'criar']):
            resposta = 'positivo'

            while any(palavra in resposta.lower() for palavra in ['positivo','claro']):
                falar_ana('Certo, qual evento você quer cadastrar?')

                user = falar_user()

                eventos.append(user)

                falar_ana('Evento cadastrado! Algo mais que deseja cadastrar?')

                resposta = falar_user()

            criar_arquivo()

            if parar_continuar()!= 'positivo':
                break

        elif any(palavra in user.lower() for palavra in ['ler', 'checar', 'qual']):
            caminho_area_de_trabalho = os.path.join(os.path.expanduser("~"), "Desktop", "eventos.txt")

            try:
                with open(caminho_area_de_trabalho, "r", encoding="utf-8") as arquivo:
                    conteudo = arquivo.read()
                    falar_ana(f"Aqui estão os eventos da sua agenda:\n {conteudo}")

                if parar_continuar() != 'positivo':
                    break

            except FileNotFoundError:
                falar_ana("O arquivo eventos.txt não foi encontrado na sua área de trabalho.")

                if parar_continuar() != 'positivo':
                    break
        else:
            falar_ana("Comando não reconhecido")
            break
    else:
        falar_ana("Comando não reconhecido")
        break

