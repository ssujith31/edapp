from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from bs4 import BeautifulSoup
import markdown
import pygame
import speech_recognition as sr
from gtts import gTTS
import openai

app = Flask(__name__, static_folder='assets', template_folder='templates')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

openai.api_key = "your-api-key"  # Replace with your actual OpenAI API key

def get_response_from_openai(prompt):
    try:
        response = openai.Completion.create(
            model="text-davinci-003",  # Ensure this model is available
            prompt=prompt,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def playvoice(filename1):
    pygame.mixer.music.load(filename1)
    pygame.mixer.music.play()

pygame.mixer.init()

def remove_tags(html):
    soup = BeautifulSoup(html, "html.parser")
    for data in soup(['style', 'script']):
        data.decompose()
    return ' '.join(soup.stripped_strings)

@app.route('/login')
def login():
    return render_template("login.html")

@app.route('/loginaction', methods=["POST"])
def loginaction():
    if request.method == 'POST':
        data = request.form
        if data['email'] == "anandapk90@gmail.com" and data['password'] == "123":
            session["name"] = data['email']
            return render_template("profile.html")
        else:
            return render_template("login.html", msg="Invalid Login")

@app.route('/signout')
def signout():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        session["name"] = None
        return redirect(url_for('login'))

@app.route('/courses')
def courses():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        return render_template("courses.html")

@app.route('/profile')
def profile():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        return render_template("profile.html")

@app.route('/basicmathpage')
def basicmathpage():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        return render_template("basicmath.html")

@app.route('/stopvoice', methods=['POST'])
def stopvoice():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        pygame.mixer.music.stop()
        return {"status": "stoppedvoice"}

@app.route('/displaycontent', methods=["POST"])
def displaycontent():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            data1 = request.json
            file_map = {
                "add": "contents/addition.txt",
                "subtract": "contents/subtraction.txt",
                "multiply": "contents/multiplication.txt",
                "divide": "contents/division.txt"
            }
            file_path = file_map.get(data1['operation'])
            if file_path:
                with open(file_path, "r") as f:
                    content = f.read()
                content1 = markdown.markdown(content)
                return {"data2": content1, "ops": data1['operation'].capitalize()}
            else:
                return {"data2": "", "ops": "Unknown Operation"}

@app.route('/doubttextmode', methods=["POST"])
def doubttextmode():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            q1 = request.json
            prepend = "Answer should be embedded in HTML tags. "
            tosend = prepend + q1['question']
            response = get_response_from_openai(tosend)
            if response:
                return {"answer": response}
            else:
                return {"answer": "An error occurred while processing your request."}

@app.route('/startconvert', methods=['POST'])
def startconvert():
    transcript_path = 'transcript.txt'
    with open(transcript_path, 'w') as transcript:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                transcript.write(r.recognize_google(audio))
            except Exception as e:
                print(f"Error recognizing speech: {e}")

            with open("recorded.wav", "wb") as f:
                f.write(audio.get_wav_data())

    with open(transcript_path, 'r') as f:
        message = f.read()
        response = get_response_from_openai(message)
        if response:
            return {"filename": "recorded.wav"}
        else:
            return {"filename": "recorded.wav", "error": "Failed to get a response"}

@app.route('/startconvert2', methods=['POST'])
def startconvert2():
    transcript_path = 'transcript.txt'
    with open(transcript_path, 'w') as transcript:
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                transcript.write(r.recognize_google(audio))
            except Exception as e:
                print(f"Error recognizing speech: {e}")

            with open("recorded.wav", "wb") as f:
                f.write(audio.get_wav_data())

    with open(transcript_path, 'r') as f:
        message = f.read()
        response = get_response_from_openai(message)
        if response:
            language = 'en'
            tts = gTTS(text=response, lang=language, slow=False)
            tts.save("welcome.mp3")
            pygame.mixer.music.load("welcome.mp3")
            pygame.mixer.music.play()
            return {"filename": "recorded.wav"}
        else:
            return {"filename": "recorded.wav", "error": "Failed to get a response"}

@socketio.on('voiceaction')
def handle_message(data):
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        transcript_path = 'datafiles/transcript.txt'
        with open(transcript_path, 'w') as transcript:
            r = sr.Recognizer()
            with sr.Microphone() as source:
                r.adjust_for_ambient_noise(source)
                audio = r.listen(source)
                try:
                    transcript.write(r.recognize_google(audio))
                except Exception as e:
                    print(f"Error recognizing speech: {e}")

                with open("datafiles/recorded.wav", "wb") as f:
                    f.write(audio.get_wav_data())

        with open(transcript_path, 'r') as f:
            message = f.read()
            response = get_response_from_openai(message)
            if response:
                tts = gTTS(text=response, lang='en', slow=False)
                tts.save("datafiles/welcome.mp3")
                pygame.mixer.music.load("datafiles/welcome.mp3")
                pygame.mixer.music.play()
                data3 = {"result": message, "answer": response}
                emit('displaydetails', data3)

                while pygame.mixer.music.get_busy():
                    continue

                emit('voicecompleted', {"status": "ok"})
            else:
                emit('displaydetails', {"result": message, "answer": "An error occurred while processing your request."})

if __name__ == '__main__':
    socketio.run(app)
