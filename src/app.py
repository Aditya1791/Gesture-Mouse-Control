import os
import sys
os.environ['PURE_PYTHON'] = '1'
os.environ['GEVENT_NO_C_EXT'] = '1'

import eel
from queue import Queue

class ChatBot:

    started = False
    userinputQueue = Queue()

    @staticmethod
    def isUserInput():
        return not ChatBot.userinputQueue.empty()

    @staticmethod
    def popUserInput():
        if ChatBot.userinputQueue.empty():
            return None
        return ChatBot.userinputQueue.get()

    @staticmethod
    def close_callback(route, websockets):
        ChatBot.started = False
        sys.exit(0)

    @staticmethod
    @eel.expose
    def getUserInput(msg):
        if msg:
            ChatBot.userinputQueue.put(msg)
            print(f"[GUI Input]: {msg}")

    @staticmethod
    def close():
        ChatBot.started = False

    @staticmethod
    def addUserMsg(msg):
        try:
            eel.addUserMsg(msg)
        except Exception as e:
            print(f"[Eel Error]: Could not send user message: {e}")

    @staticmethod
    def addAppMsg(msg):
        try:
            eel.addAppMsg(msg)
        except Exception as e:
            print(f"[Eel Error]: Could not send app message: {e}")

    @staticmethod
    def start():
        path = os.path.dirname(os.path.abspath(__file__))
        web_folder = os.path.join(path, 'web')
        eel.init(web_folder, allowed_extensions=['.js', '.html', '.css', '.png', '.jpg'])
        
        start_kwargs = {
            'host': 'localhost',
            'port': 27005,
            'block': False,
            'size': (380, 560),
            'position': (10, 100),
            'disable_cache': True,
            'close_callback': ChatBot.close_callback
        }

        launched = False
        # Try chrome first, then default browser, then fallback
        for mode in ['chrome', 'default', None]:
            try:
                print(f"[App] Starting Eel GUI with mode={mode}...")
                eel.start('index.html', mode=mode, **start_kwargs)
                launched = True
                break
            except Exception as e:
                print(f"[App] Failed launching Eel with mode={mode}: {e}")

        if launched:
            ChatBot.started = True
            while ChatBot.started:
                try:
                    eel.sleep(1.0)
                except Exception:
                    break
        else:
            print("[App Error] Could not launch Eel GUI window in any mode.")
