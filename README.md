# Bot Discord "BotRonron"

Un bot Discord simple et léger, hébergé sur Render, avec un serveur Flask minimal pour rester actif via UptimeRobot.

---

## Fonctionnalités principales

- Commande `/ping` qui répond `Pong !`
- Chargement sécurisé du token via `.env` localement et variables d’environnement sur Render
- Keep-alive grâce à un serveur Flask minimal et pings réguliers d’UptimeRobot
- Commandes modulaires organisées en extensions (cogs)

---

## Installation et usage local

1. Clone le dépôt :
    ```bash
    git clone https://github.com/BunnyMelonne/discord-bot.git
    cd discord-bot
    ```

2. Crée un fichier `.env` à la racine avec la variable suivante :
    ```
    TOKEN=ton_token_discord
    ENV=dev
    ```

3. Installe les dépendances Python :
    ```bash
    pip install -r requirements.txt
    ```

4. Lance le bot :
    ```bash
    python bot.py
    ```

---

## Déploiement sur Render

1. Pousse ton code sur GitHub.

2. Crée un service Web sur [Render](https://render.com) lié à ton dépôt.

3. Configure la variable d’environnement `TOKEN` dans les paramètres du service.

4. Configure la commande de démarrage à :
    ```
    python bot.py
    ```

5. Déploie et attends que le service soit en ligne.

---

## Keep-alive avec UptimeRobot

1. Crée un compte gratuit sur [UptimeRobot](https://uptimerobot.com).

2. Ajoute un nouveau monitor HTTP(s).

3. Utilise l’URL publique de ton service Render, par exemple :
    ```
    https://discord-bot-rn90.onrender.com/
    ```

4. Configure un ping toutes les 5 minutes pour maintenir le bot actif.

---

## Structure du projet

```plaintext
discord-bot/
├── bot.py             # Script principal du bot Discord
├── keep_alive.py      # Serveur Flask pour keep-alive
├── commands/          # Extensions (cogs) des commandes Discord
│   ├── menu.py
│   ├── status.py
│   ├── test_db.py
│   ├── avatar.py
│   └── hello.py
├── db.py              # Gestion base MongoDB (avec motor)
├── requirements.txt   # Dépendances Python
├── .env               # Variables d'environnement (non commit)
└── README.md          # Ce fichier
```

## Remarques importantes

- Ne jamais committer le fichier `.env` ni d’autres fichiers contenant des données sensibles.
- Les tokens et clés doivent être gérés via les variables d’environnement sur Render ou en local.
- Pour le développement local, utiliser `ENV=dev` dans `.env` pour synchroniser les commandes uniquement sur ton serveur de test Discord.

---
