# Bot Discord "BotRonron"

Un bot Discord simple hébergé sur Render, maintenu actif avec UptimeRobot.

---

## Fonctionnalités

- Commande `!ping` répond avec `Pong !`
- Serveur Flask minimal pour keep-alive (ping par UptimeRobot)
- Chargement sécurisé du token via `.env` localement et variables d’environnement Render

---

## Installation et lancement local

1. Clone le repo :
    ```bash
    git clone <URL-du-repo>
    cd <nom-du-repo>
    ```

2. Crée un fichier `.env` à la racine avec :
    ```
    TOKEN=ton_token_discord
    ```

3. Installe les dépendances :
    ```bash
    pip install -r requirements.txt
    ```

4. Lance le bot localement :
    ```bash
    python bot.py
    ```

---

## Déploiement sur Render

1. Pousse ton code sur GitHub.

2. Sur [Render](https://render.com), crée un nouveau service Web lié à ton repo.

3. Configure la variable d’environnement `TOKEN` dans les paramètres du service.

4. Configure la commande de démarrage :
    ```
    python bot.py
    ```

5. Déploie et attends que le service soit en ligne.

---

## Keep-alive avec UptimeRobot

1. Crée un compte gratuit sur [UptimeRobot](https://uptimerobot.com).

2. Crée un nouveau monitor HTTP(s).

3. Configure l’URL avec celle de Render, par exemple :
    ```
    https://<ton-service>.onrender.com/
    ```

4. Configure un ping toutes les 5 minutes.

---

## Structure du projet

~~~
├── bot.py          # Code principal du bot
├── keep_alive.py   # Serveur Flask pour keep-alive
├── requirements.txt
├── .gitignore      # Ignore .env et config
└── README.md
~~~

## Remarques

- Ne jamais committer `.env` ou fichiers sensibles dans GitHub.
- Les variables sensibles doivent être gérées via les variables d’environnement Render.

---
