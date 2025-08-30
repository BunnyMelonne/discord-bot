# =========================================
# Importations
# =========================================

import random
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional, cast

import discord
from discord.ext import commands

# =========================================
# Helper utils
# =========================================

async def edit_message(message: Optional[discord.Message], **kwargs) -> None:
    """Édite un message Discord si celui-ci existe"""
    if not message:
        return
    try:
        await message.edit(**kwargs)
    except (discord.NotFound, discord.Forbidden):
        pass

def disable_all_buttons(view: discord.ui.View) -> None:
    """Désactive tous les boutons d'une vue Discord."""
    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.disabled = True

# =========================================
# Constantes
# =========================================

ROWS: int = 6
COLS: int = 7

EMPTY_CELL: str = "<:null:1405700337611837460>"
SPACER: str = "<:spacer:1408471845950324829>"

PIECES: dict[str, str] = {"p1": "🔴", "p2": "🔵"}
COLORS: dict[str, discord.Color] = {"p1": discord.Color(0xD22D39), "p2": discord.Color.blue()}

EMOJIS: list[str] = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

# =========================================
# Plateau
# =========================================

class Board:
    """Représente le plateau du Puissance 4 et gère les placements et vérifications."""

    def __init__(self):
        """Initialise une grille vide de dimensions ROWS x COLS."""
        self.grid: list[list[str]] = [[EMPTY_CELL for _ in range(COLS)] for _ in range(ROWS)]

    def drop_piece(self, col: int, piece: str) -> bool:
        """Place une pièce dans la colonne spécifiée si possible."""
        if not 0 <= col < COLS:
            return False
        for row in reversed(self.grid):
            if row[col] == EMPTY_CELL:
                row[col] = piece
                return True
        return False

    def check_win(self, piece: str) -> bool:
        """Vérifie si le joueur avec la pièce donnée a gagné."""
        # Horizontale
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(self.grid[r][c + i] == piece for i in range(4)):
                    return True
        # Verticale
        for r in range(ROWS - 3):
            for c in range(COLS):
                if all(self.grid[r + i][c] == piece for i in range(4)):
                    return True
        # Diagonale ↘
        for r in range(ROWS - 3):
            for c in range(COLS - 3):
                if all(self.grid[r + i][c + i] == piece for i in range(4)):
                    return True
        # Diagonale ↙
        for r in range(3, ROWS):
            for c in range(COLS - 3):
                if all(self.grid[r - i][c + i] == piece for i in range(4)):
                    return True
        return False

    def is_full(self) -> bool:
        """Retourne True si le plateau est rempli (match nul)."""
        return all(self.grid[0][c] != EMPTY_CELL for c in range(COLS))


# =========================================
# EmbedBuilder – affichage
# =========================================

class EmbedBuilder:
    """Génère des embeds Discord pour le jeu Puissance 4."""

    @staticmethod
    def board_display(view: "Puissance4View") -> str:
        """Retourne le plateau sous forme de chaîne avec emojis."""
        header = " ".join(EMOJIS)
        arrows = " ".join("🔻" if view.last_move == i else SPACER for i in range(COLS))
        grid_lines = [" ".join(row) for row in view.board.grid]
        return "\n".join([header, arrows] + grid_lines)

    @staticmethod
    def status_message(view: "Puissance4View") -> str:
        """Retourne le message de statut du jeu (tour, victoire ou match nul)."""
        if view.winner:
            base = f"🎉 {view.winner.mention} a gagné !"
            if view.winner != view.current_player:
                base += f"\n⏳ {view.current_player.mention} n'a pas joué à temps."
            return base
        if view.draw:
            return "🤝 Match nul !"
        return f"👉 Tour de {view.current_player.mention}"
    
    @staticmethod
    def timeout_timestamp(view: "Puissance4View") -> str:
        """Retourne le timestamp Discord pour la fin du tour, vide si terminé."""
        if view.winner or view.draw:
            return ""
        turn_end_time = datetime.now(timezone.utc) + timedelta(seconds=view.TURN_TIMEOUT)
        timestamp = int(turn_end_time.timestamp())
        return f"\n🕐 Fin du tour <t:{timestamp}:R>"

    @staticmethod
    def score_display(view: "Puissance4View") -> str:
        """Affiche le score des deux joueurs."""
        p1, p2 = view.players
        return (
            f"**🏆 Victoires :**\n"
            f"{view.pieces[p1.id]} {p1.mention} : **{view.scores[p1.id]}**\n"
            f"{view.pieces[p2.id]} {p2.mention} : **{view.scores[p2.id]}**"
        )

    @staticmethod
    def color(view: "Puissance4View") -> discord.Color:
        """Retourne la couleur de l'embed selon l'état du jeu."""
        if view.winner: return discord.Color.green()
        if view.draw: return discord.Color.greyple()
        return view.colors[view.current_player.id]

    @staticmethod
    def embed(view: "Puissance4View") -> discord.Embed:
        """Construit l'embed principal du jeu."""
        description = (
            f"{EmbedBuilder.board_display(view)}\n\n"
            f"{EmbedBuilder.status_message(view)}"
            f"{EmbedBuilder.timeout_timestamp(view)}\n\n"
            f"{EmbedBuilder.score_display(view)}"
        )
        return (
            discord.Embed(description=description, color=EmbedBuilder.color(view))
            .set_thumbnail(url="https://i.imgur.com/re2Z5fM.png")
        )
    
    @staticmethod
    def rejection_embed(player: discord.Member, confirmed: Optional[bool]) -> discord.Embed:
        """Embed affiché si l'invitation est refusée ou expirée."""
        if confirmed is False:
            title = "❌ Invitation refusée"
            description = f"{player.mention} a décliné l'invitation."
            color = discord.Color.red()
        else:
            title = "⌛ Invitation expirée"
            description = f"{player.mention} n'a pas répondu à temps."
            color = discord.Color.light_grey()
        
        return discord.Embed(title=title, description=description, color=color)

    @staticmethod
    def invitation_embed(player1: discord.Member, player2: discord.Member) -> discord.Embed:
        """Embed pour inviter un joueur à une partie."""
        return discord.Embed(
            title="Souhaitez-vous jouer au Puissance 4 ?",
            description=f"{player1.mention} souhaite faire une partie avec {player2.mention}.",
            color=discord.Color.blurple()
        )


# =========================================
# ButtonManager – gestion boutons
# =========================================

class ButtonManager:
    """Gère l'initialisation et la mise à jour des boutons pour le jeu."""

    @staticmethod
    def init_buttons(view: "Puissance4View"):
        """Crée les boutons pour chaque colonne et les ajoute à la vue."""
        view.clear_items()
        for i in range(COLS):
            view.add_item(Puissance4Button(i, view, row=0 if i < 4 else 1))

    @staticmethod
    def update_buttons(view: "Puissance4View"):
        """Active/désactive et colore les boutons selon le joueur actuel et l'état du plateau."""
        style = (
            discord.ButtonStyle.danger
            if view.current_player == view.players[0]
            else discord.ButtonStyle.primary
        )
        for button in view.children:
            if isinstance(button, Puissance4Button):
                button.disabled = view.board.grid[0][button.col] != EMPTY_CELL
                button.style = style

# =========================================
# Puissance4View – fusion GameState + View
# =========================================

class Puissance4View(discord.ui.View):
    """Représente l'état d'une partie de Puissance 4 et la vue interactive Discord."""

    TURN_TIMEOUT = 120

    def __init__(self, p1: discord.Member, p2: discord.Member, scores: Optional[dict] = None):
        """Initialise la partie, le plateau, les joueurs, les couleurs, et les boutons."""
        super().__init__(timeout=self.TURN_TIMEOUT)

        self.board = Board()
        self.players = [p1, p2]
        self.current_player = random.choice(self.players)
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.scores = scores or {p1.id: 0, p2.id: 0}

        self.last_move: Optional[int] = None
        self.winner: Optional[discord.Member] = None
        self.draw: bool = False

        self.message: Optional[discord.Message] = None
        self.lock = asyncio.Lock()

        ButtonManager.init_buttons(self)
        ButtonManager.update_buttons(self)

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul le joueur du tour peut interagir avec la vue."""
        if interaction.user != self.current_player:
            await interaction.response.send_message(
                "⏳ Ce n'est pas ton tour.", ephemeral=True
            )
            return False
        return True

    async def play_turn(self, col: int):
        """Joue un tour pour le joueur courant dans la colonne spécifiée."""
        async with self.lock:
            piece = self.pieces[self.current_player.id]
            if not self.board.drop_piece(col, piece):
                return

            self.last_move = col

            if self._check_game_end(piece):
                await self._end_game()
                return
            
            self.switch_turn()
            ButtonManager.update_buttons(self)
            await self.refresh_message()

    def _check_game_end(self, piece: str) -> bool:
        """Vérifie si la partie est terminée (victoire ou match nul)."""
        if self.board.check_win(piece):
            self.winner = self.current_player
            return True
        if self.board.is_full():
            self.draw = True
            return True
        return False

    async def _end_game(self):
        """Met fin à la partie et met à jour le score si nécessaire."""
        if self.winner:
            self.scores[self.winner.id] += 1
        self.stop()
        await self.refresh_message(EndgameView(self))

    def switch_turn(self):
        """Change le joueur courant pour le tour suivant."""
        self.current_player = self.players[1 - self.players.index(self.current_player)]

    async def refresh_message(self, view: Optional[discord.ui.View] = None):
        """Met à jour le message Discord avec le plateau et la vue actuelle."""
        await edit_message(
            self.message,
            embed=EmbedBuilder.embed(self),
            view=view or self
        )

    async def on_timeout(self):
        """Gère la fin du tour si le joueur n'a pas joué à temps."""
        async with self.lock:
            if not (self.winner or self.draw):
                self.winner = next(p for p in self.players if p != self.current_player)
            await self._end_game()


# =========================================
# Puissance4Button – bouton colonne
# =========================================

class Puissance4Button(discord.ui.Button):
    """Bouton représentant une colonne pour déposer une pièce."""

    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        """Initialise le bouton pour une colonne donnée et l'associe à la vue du jeu."""
        super().__init__(emoji=EMOJIS[col], row=row)
        self.col = col
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Déclenche le tour du joueur lorsqu'il clique sur le bouton."""
        await interaction.response.defer()
        await self.game_view.play_turn(self.col)

# =========================================
# EndgameView – fin de partie
# =========================================

class EndgameView(discord.ui.View):
    """Vue interactive affichée à la fin d'une partie avec options Rejouer/Arrêter."""

    def __init__(self, game_view: Puissance4View, timeout: int = 120):
        """Initialise les boutons pour rejouer ou arrêter la partie."""
        super().__init__(timeout=timeout)
        self.game_view = game_view
        self.add_item(RejouerButton(game_view))
        self.add_item(ArreterButton(game_view))

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seuls les joueurs de la partie peuvent interagir."""
        if interaction.user in self.game_view.players:
            return True
        await interaction.response.send_message(
            "🚫 Tu ne peux pas participer.", ephemeral=True
        )
        return False

    async def on_timeout(self):
        """Désactive les boutons à l'expiration de la vue."""
        self.stop()
        disable_all_buttons(self)
        await edit_message(self.game_view.message, view=self)


class RejouerButton(discord.ui.Button):
    """Bouton pour relancer une nouvelle partie avec les mêmes joueurs."""

    def __init__(self, game_view: Puissance4View):
        super().__init__(label="🔄 Rejouer", style=discord.ButtonStyle.success)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Crée une nouvelle vue de jeu et remplace l'ancienne."""
        if self.view:
            self.view.stop()

            new_view = Puissance4View(
                *self.game_view.players,
                scores=self.game_view.scores
            )

            new_view.message = self.game_view.message

            await interaction.response.edit_message(
                embed=EmbedBuilder.embed(new_view), 
                view=new_view
            )


class ArreterButton(discord.ui.Button):
    """Bouton pour arrêter la partie en cours."""

    def __init__(self, game_view: Puissance4View):
        super().__init__(label="🛑 Arrêter", style=discord.ButtonStyle.danger)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Arrête la partie et notifie les joueurs."""
        if self.view:
            self.view.stop()
            disable_all_buttons(self.view)
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send(f"🛑 {interaction.user.mention} a arrêté le jeu.")


# =========================================
# ConfirmationView – accepter/refuser partie
# =========================================

class ConfirmationView(discord.ui.View):
    """Vue pour confirmer ou refuser une invitation à jouer."""

    def __init__(self, player1: discord.Member, player2: discord.Member, timeout: int = 120):
        """Initialise les boutons de confirmation et l'état de l'invitation."""
        super().__init__(timeout=timeout)
        self.player1 = player1
        self.player2 = player2
        self.confirmed: Optional[bool] = None
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul l'adversaire invité peut interagir."""
        if interaction.user != self.player2:
            await interaction.response.send_message(
                "❌ Seul l'adversaire invité peut cliquer.", ephemeral=True
            )
            return False
        return True

    async def finalize(self):
        """Applique la décision finale et met à jour le message Discord."""
        self.stop()

        if not self.message:
            return

        if self.confirmed:
            view = Puissance4View(self.player1, self.player2)
            view.message = self.message
            embed = EmbedBuilder.embed(view)
        else:
            view = self
            embed = self._get_rejection_embed()
            disable_all_buttons(self)

        await edit_message(self.message, content=None, embed=embed, view=view)

    def _get_rejection_embed(self) -> discord.Embed:
        """Retourne l'embed de refus ou d'expiration de l'invitation."""
        return EmbedBuilder.rejection_embed(self.player2, self.confirmed)

    async def on_timeout(self):
        """Finalise automatiquement si le joueur invité n'a pas répondu."""
        await self.finalize()

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        """Bouton pour accepter l'invitation."""
        self.confirmed = True
        await interaction.response.defer()
        await self.finalize()

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        """Bouton pour refuser l'invitation."""
        self.confirmed = False
        await interaction.response.defer()
        await self.finalize()

# =========================================
# Cog commande /puissance4
# =========================================

class Puissance4(commands.Cog):
    """Cog Discord contenant la commande /puissance4 pour lancer une partie."""

    def __init__(self, bot: commands.Bot):
        """Initialise le Cog avec le bot."""
        self.bot = bot

    @discord.app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @discord.app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member) -> None:
        """Commande pour initier une partie contre un adversaire choisi."""

        player1 = cast(discord.Member, interaction.user)
        player2 = cast(discord.Member, adversaire)

        if player1 == player2 or player1.bot or player2.bot:
            await interaction.response.send_message(
                "❌ Impossible de jouer contre cet utilisateur.", ephemeral=True
            )
            return

        view = ConfirmationView(player1, player2)
        
        await interaction.response.send_message(
            content=f"{player2.mention}",
            embed=EmbedBuilder.invitation_embed(player1, player2),
            view=view
        )

        message = await interaction.original_response()
        view.message = await message.channel.fetch_message(message.id)
        await view.wait()


# =========================================
# Setup Cog
# =========================================

async def setup(bot: commands.Bot):
    """Ajoute le Cog Puissance4 au bot."""
    await bot.add_cog(Puissance4(bot))