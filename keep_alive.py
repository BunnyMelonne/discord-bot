import os
from flask import Flask
from threading import Thread
import logging
import time

app = Flask('')

# Désactive les logs Flask pour éviter le spam
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route('/')
def home():
    return "BotRonron est en vie ! 🐱"

@app.route('/ping')
def ping():
    return "pong"

@app.route('/status')
def status():
    return {
        "status": "online",
        "bot": "BotRonron",
        "timestamp": int(time.time())
    }

def run():
    try:
        port = int(os.environ.get("PORT", 8080))
        app.run(host='0.0.0.0', port=port, debug=False)
    except Exception as e:
        print(f"Erreur serveur Flask: {e}")
        time.sleep(5)
        run()  # Redémarre en cas d'erreur

def keep_alive():
    print("🔥 Serveur keep-alive démarré")
    t = Thread(target=run)
    t.daemon = True
    t.start()
