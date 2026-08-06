import pyttsx3
import speech_recognition as sr
from datetime import date
import time
import webbrowser
import datetime
from pynput.keyboard import Key, Controller
import pyautogui
import sys
import os
from os import listdir
from os.path import isfile, join
import smtplib
import wikipedia
import Gesture_Controller
import app
from threading import Thread

# -------------Object Initialization---------------
today = date.today()
r = sr.Recognizer()
keyboard = Controller()

# Initialize TTS Engine Safely
engine = None
try:
    engine = pyttsx3.init('sapi5')
    voices = engine.getProperty('voices')
    if voices:
        engine.setProperty('voice', voices[0].id)
except Exception:
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if voices:
            engine.setProperty('voice', voices[0].id)
    except Exception as e:
        print(f"[TTS Warning] Could not initialize pyttsx3 engine: {e}")

# Check Microphone availability safely
mic_available = False
try:
    with sr.Microphone() as source:
        r.energy_threshold = 500 
        r.dynamic_energy_threshold = False
        mic_available = True
except Exception as e:
    print(f"[Microphone Warning] Audio microphone not available or PyAudio missing: {e}")

# ----------------Variables------------------------
file_exp_status = False
files = []
path = 'C:\\' if os.name == 'nt' else '/'
is_awake = True  # Bot status

# ------------------Functions----------------------
def reply(audio):
    app.ChatBot.addAppMsg(audio)
    print(f"[Proton]: {audio}")
    if engine:
        try:
            engine.say(audio)
            engine.runAndWait()
        except Exception as e:
            print(f"[TTS Error]: {e}")

def wish():
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour < 12:
        reply("Good Morning!")
    elif hour >= 12 and hour < 18:
        reply("Good Afternoon!")   
    else:
        reply("Good Evening!")  
    reply("I am Proton, how may I help you?")

def record_audio():
    global mic_available
    if not mic_available:
        time.sleep(0.5)
        return ""

    try:
        with sr.Microphone() as source:
            r.pause_threshold = 0.8
            audio = r.listen(source, phrase_time_limit=5)
            voice_data = r.recognize_google(audio)
            return voice_data.lower()
    except sr.RequestError:
        reply('Sorry, service is down. Please check your Internet connection.')
    except sr.UnknownValueError:
        pass
    except Exception as e:
        print(f"[Record Audio Exception]: {e}")
        mic_available = False
        reply('Microphone disabled or disconnected. Please type your commands in the GUI.')
    return ""

def respond(voice_data):
    global file_exp_status, files, is_awake, path
    if not voice_data:
        return

    print(f"[User Input Raw]: {voice_data}")
    voice_data_clean = voice_data.replace('proton', '').strip()

    if not is_awake:
        if 'wake up' in voice_data_clean or 'wake up' in voice_data:
            is_awake = True
            wish()
        return

    # STATIC CONTROLS
    if 'hello' in voice_data_clean or 'hi' in voice_data_clean:
        wish()

    elif 'what is your name' in voice_data_clean:
        reply('My name is Proton!')

    elif 'date' in voice_data_clean:
        reply(today.strftime("%B %d, %Y"))

    elif 'time' in voice_data_clean:
        reply(datetime.datetime.now().strftime("%I:%M %p"))

    elif 'search' in voice_data_clean:
        search_query = voice_data_clean.split('search')[-1].strip()
        if search_query:
            reply(f'Searching for {search_query}')
            url = 'https://google.com/search?q=' + search_query
            try:
                webbrowser.get().open(url)
                reply('This is what I found Sir.')
            except Exception:
                reply('Please check your Internet connection.')

    elif 'location' in voice_data_clean:
        reply('Which place are you looking for?')
        temp_audio = record_audio()
        if temp_audio:
            app.ChatBot.addUserMsg(temp_audio)
            reply('Locating...')
            url = 'https://google.com/maps/place/' + temp_audio
            try:
                webbrowser.get().open(url)
                reply('This is what I found Sir.')
            except Exception:
                reply('Please check your Internet connection.')

    elif 'bye' in voice_data_clean or 'by' in voice_data_clean:
        reply("Good bye Sir! Have a nice day.")
        is_awake = False

    elif 'exit' in voice_data_clean or 'terminate' in voice_data_clean:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
        reply("Exiting application...")
        app.ChatBot.close()
        sys.exit()

    # DYNAMIC CONTROLS
    elif 'launch gesture recognition' in voice_data_clean:
        if Gesture_Controller.GestureController.gc_mode:
            reply('Gesture recognition is already active.')
        else:
            gc = Gesture_Controller.GestureController()
            if Gesture_Controller.GestureController.gc_mode:
                t = Thread(target=gc.start, daemon=True)
                t.start()
                reply('Launched Gesture Recognition Successfully.')
            else:
                reply('Could not launch Gesture Recognition. Please check if camera is connected.')

    elif 'stop gesture recognition' in voice_data_clean or 'top gesture recognition' in voice_data_clean:
        if Gesture_Controller.GestureController.gc_mode:
            Gesture_Controller.GestureController.gc_mode = 0
            reply('Gesture recognition stopped.')
        else:
            reply('Gesture recognition is already inactive.')

    elif 'copy' in voice_data_clean:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('c')
            keyboard.release('c')
        reply('Copied')

    elif 'paste' in voice_data_clean or 'pest' in voice_data_clean:
        with keyboard.pressed(Key.ctrl):
            keyboard.press('v')
            keyboard.release('v')
        reply('Pasted')

    # File Navigation
    elif 'list' in voice_data_clean:
        try:
            path = 'C:\\' if os.name == 'nt' else '/'
            files = listdir(path)
            filestr = ""
            for idx, f in enumerate(files, 1):
                filestr += f"{idx}:  {f}<br>"
            file_exp_status = True
            reply('These are the files in your root directory:')
            app.ChatBot.addAppMsg(filestr)
        except Exception as e:
            reply(f"Could not list directory: {e}")

    elif file_exp_status:
        if 'open' in voice_data_clean:
            parts = voice_data_clean.split(' ')
            try:
                file_idx = int(parts[-1]) - 1
                if 0 <= file_idx < len(files):
                    target_path = os.path.join(path, files[file_idx])
                    if isfile(target_path):
                        os.startfile(target_path)
                        file_exp_status = False
                        reply(f"Opened file {files[file_idx]}")
                    else:
                        path = target_path
                        files = listdir(path)
                        filestr = ""
                        for idx, f in enumerate(files, 1):
                            filestr += f"{idx}:  {f}<br>"
                        reply(f"Opened directory {os.path.basename(path)}:")
                        app.ChatBot.addAppMsg(filestr)
                else:
                    reply("Invalid item number selected.")
            except (ValueError, IndexError):
                reply("Please specify a valid item number to open.")
            except Exception:
                reply("You do not have permission or error accessing this path.")

        elif 'back' in voice_data_clean:
            try:
                parent_path = os.path.dirname(os.path.rstrip(path, r'\/'))
                if parent_path and parent_path != path:
                    path = parent_path
                    files = listdir(path)
                    filestr = ""
                    for idx, f in enumerate(files, 1):
                        filestr += f"{idx}:  {f}<br>"
                    reply("Navigated back:")
                    app.ChatBot.addAppMsg(filestr)
                else:
                    reply("Already at the root directory.")
            except Exception as e:
                reply(f"Could not navigate back: {e}")
        else:
            reply('I am not programmed for this action!')
    else:
        reply('I am not programmed for this action!')

# ------------------Driver Code--------------------
if __name__ == '__main__':
    t1 = Thread(target=app.ChatBot.start, daemon=True)
    t1.start()

    # Wait until GUI starts or times out
    wait_counter = 0
    while not app.ChatBot.started and wait_counter < 10:
        time.sleep(0.5)
        wait_counter += 1

    wish()
    if not mic_available:
        reply("Note: Microphone input is unavailable. Use the GUI text box below to control Proton!")

    while app.ChatBot.started:
        if app.ChatBot.isUserInput():
            user_input = app.ChatBot.popUserInput()
            if user_input:
                respond(user_input)
        else:
            v_data = record_audio()
            if v_data and 'proton' in v_data:
                try:
                    respond(v_data)
                except SystemExit:
                    break
                except Exception as e:
                    print(f"[Error in respond]: {e}")
                    break
            else:
                time.sleep(0.1)
