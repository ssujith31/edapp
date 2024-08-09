from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, emit
from flask_session import Session
from bs4 import BeautifulSoup
import markdown
import pygame
import speech_recognition as sr
import openai
import os
import threading

app = Flask(__name__, static_folder='assets', template_folder='templates')

@app.after_request
def add_header(response):
    response.cache_control.no_store = True
    return response

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
socketio = SocketIO(app)

# Initialize pygame
pygame.init()
pygame.mixer.quit()  # Disable audio-related functionality

# Initialize OpenAI client
openai.api_key = "sk-svcacct-5WprkT-n2Qp7UbWgSw0q8vdtjewYuRKiEMuXdZXvr9bxdT3BlbkFJna96_v8zVptAE0mYwWkJngkJQY-0jL5f99z033SgdKxBQA"

# Replace this with correct API call
# Example usage might be:
# assistant = openai.Completion.create(model="gpt-4", prompt="Hello, how can I assist you?")

def playvoice(filename1):
    # Update to not use pygame if not required
    pass

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
            if data1['operation'] == "add":
                with open("contents/addition.txt", "r") as f:
                    content = f.read()
                content1 = markdown.markdown(content)
                return {"data2": content1, "ops": "Addition"}
            elif data1['operation'] == "subtract":
                with open("contents/subtraction.txt", "r") as f:
                    content = f.read()
                content1 = markdown.markdown(content)
                return {"data2": content1, "ops": "Subtraction"}
            elif data1['operation'] == "multiply":
                with open("contents/multiplication.txt", "r") as f:
                    content = f.read()
                content1 = markdown.markdown(content)
                return {"data2": content1, "ops": "Multiplication"}
            elif data1['operation'] == "divide":
                with open("contents/division.txt", "r") as f:
                    content = f.read()
                content1 = markdown.markdown(content)
                return {"data2": content1, "ops": "Division"}

@app.route('/doubttextmode', methods=["POST"])
def doubttextmode():
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        if request.method == "POST":
            q1 = request.json
            prompt = "Answer should be embedded in HTML tags. " + q1['question']
            response = openai.Completion.create(model="gpt-4", prompt=prompt)
            response_text = response.choices[0].text
            new_str = response_text.replace('`', '').replace('html', '', 1)
            return {"answer": new_str}

@socketio.on('voiceaction')
def handle_message(data):
    if not session.get("name"):
        return redirect(url_for('login'))
    else:
        transcript = open('datafiles/transcript.txt', 'w')
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
            try:
                transcript.write(r.recognize_google(audio))
            except Exception as e:
                pass
            with open("datafiles/recorded.wav", "wb") as f:
                f.write(audio.get_wav_data())
        transcript.close()
        with open("datafiles/transcript.txt", "r") as f:
            response = openai.Completion.create(
                model="gpt-4",
                prompt=f.read()
            )
            response_text = response.choices[0].text
            # Save response to file and play audio if needed
            # Example code, modify as needed:
            with open("datafiles/welcome.mp3", "wb") as f:
                # Convert text to speech
                pass
            pygame.mixer.music.load("datafiles/welcome.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                continue
            emit('voicecompleted', {"status": "ok"})

@app.route('/startconvert', methods=['POST'])
def startconvert():
    transcript = open('transcript.txt', 'w')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            transcript.write(r.recognize_google(audio))
        except Exception as e:
            pass
        with open("recorded.wav", "wb") as f:
            f.write(audio.get_wav_data())
    transcript.close()
    with open("transcript.txt", "r") as f:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=f.read()
        )
        # Handle the response as needed
    return {"filename": "recorded.wav"}

@app.route('/startconvert2', methods=['POST'])
def startconvert2():
    transcript = open('transcript.txt', 'w')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        try:
            transcript.write(r.recognize_google(audio))
        except Exception as e:
            pass
        with open("recorded.wav", "wb") as f:
            f.write(audio.get_wav_data())
    transcript.close()
    with open("transcript.txt", "r") as f:
        response = openai.Completion.create(
            model="gpt-4",
            prompt=f.read()
        )
        # Handle the response as needed
    return {"filename": "recorded.wav"}

if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0')
