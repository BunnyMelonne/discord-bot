# =========================================
# Importations
# =========================================

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, cast
import random

# =========================================
# Constantes du jeu
# =========================================

ROWS, COLS = 6, 7
EMPTY  = "<:null:1405700337611837460>"
PIECES = {"p1": "🔴", "p2": "🔵"}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
COLORS = {"p1": discord.Color.red(), "p2": discord.Color.blue()}

# =========================================
# Fonctions utilitaires du jeu 
# =========================================

def create_board():
    """Crée un plateau vide (6x7) avec des cercles blancs."""
    return [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

def display_board(board):
    """Retourne une chaîne représentant le plateau avec les émojis des colonnes."""
    return "\n".join(" ".join(row) for row in board) + "\n" + " ".join(EMOJIS)

def drop_piece(board, col, piece):
    """Place un jeton dans la colonne choisie si possible. Retourne True si réussi."""
    if not 0 <= col < COLS:
        return False
    for row in reversed(board):
        if row[col] == EMPTY:
            row[col] = piece
            return True
    return False

def check_win(board, piece):
    """Vérifie si un joueur a aligné 4 jetons."""

    # Vérification horizontale
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
            
    # Vérification verticale
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
            
    # Vérification diagonale descendante
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
            
    # Vérification diagonale ascendante
    for r in range(3, ROWS):
        for c in range(COLS - 3):
            if all(board[r - i][c + i] == piece for i in range(4)):
                return True
            
    return False

def board_full(board):
    """Vérifie si le plateau est rempli."""
    return all(cell != EMPTY for row in board for cell in row)

# =========================================
# Classe de la vue du jeu (View)
# =========================================

class Puissance4View(discord.ui.View):
    """Vue pour gérer l'interaction du jeu Puissance 4."""
    def __init__(self, p1: discord.Member, p2: discord.Member, scores: Optional[dict] = None):
        super().__init__(timeout=300)
        self.board = create_board()
        self.players = [p1, p2]
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.turn = random.choice(self.players)
        self.message: Optional[discord.Message] = None
        self.scores = scores or {p1.id: 0, p2.id: 0}
        self.endgame = False

        self.init_buttons()

    def init_buttons(self):
        """Réinitialise les boutons de colonnes."""
        self.clear_items()
        for i in range(COLS):
            row = 0 if i < 4 else 1
            self.add_item(Puissance4Button(i, self, row=row))
        self.update_buttons()

    def get_style(self):
        """Retourne le style du bouton selon le joueur actuel."""
        if self.turn == self.players[0]:
            return discord.ButtonStyle.danger
        return discord.ButtonStyle.primary

    def update_buttons(self):
        """Met à jour le style et l'état des boutons selon le tour et le plateau."""
        style = self.get_style()
        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board[0][button.col] != EMPTY
                button.style = style

    def disable_all_buttons(self):
        """Désactive tous les boutons."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    def get_board_display(self):
        """Retourne une représentation textuelle du plateau."""
        return display_board(self.board)

    def get_status_message(self, winner: Optional[discord.Member] = None, draw: bool = False):
        """Retourne un message de statut selon l'état du jeu."""
        if winner:
            return f"🎉 {winner.mention} a gagné !"
        if draw:
            return "🤝 Match nul !"
        return f"Tour de : {self.pieces[self.turn.id]} {self.turn.mention}"

    def get_score_display(self):
        """Retourne l'affichage des scores des joueurs."""
        p1, p2 = self.players
        return (
            f"**🏆 Victoires :**\n"
            f"{self.pieces[p1.id]} {p1.mention} : **{self.scores[p1.id]}**\n"
            f"{self.pieces[p2.id]} {p2.mention} : **{self.scores[p2.id]}**"
        )

    def get_color(self, winner: Optional[discord.Member] = None, draw: bool = False):
        """Retourne la couleur de l'embed selon l'état du jeu."""
        if winner:
            return discord.Color.green()
        if draw:
            return discord.Color.greyple()
        return self.colors[self.turn.id]

    def get_embed(self, winner: Optional[discord.Member] = None, draw: bool = False):
        """Retourne l'embed à afficher pour le jeu."""
        description = (
            f"{self.get_board_display()}\n\n"
            f"{self.get_status_message(winner, draw)}\n\n"
            f"{self.get_score_display()}"
        )
        color = self.get_color(winner, draw)
        return (
            discord.Embed(
                title="✦━─ Puissance 4 ─━✦", 
                description=description, 
                color=color
            )
            .set_thumbnail(url="https://i.imgur.com/NjrISNE.png")
        )

    async def end_game(self, winner: Optional[discord.Member] = None, draw: bool = False):
        """Termine la partie et met à jour l'embed."""
        if winner:
            self.scores[winner.id] += 1

        self.endgame = True
        self.clear_items()
        self.add_item(RejouerButton(self))

        if self.message:
            await self.message.edit(
                embed=self.get_embed(winner=winner, draw=draw), 
                view=self
            )

    async def switch_turn(self):
        """Change le tour au joueur suivant."""
        self.turn = self.players[1 - self.players.index(self.turn)]
        self.update_buttons()
        if self.message:
            await self.message.edit(
                embed=self.get_embed(), 
                view=self
            )

    async def play_turn(self, col: int):
        """Joue un tour pour le joueur actuel."""
        piece = self.pieces[self.turn.id]
        if not drop_piece(self.board, col, piece):
            return

        if check_win(self.board, piece):
            await self.end_game(winner=self.turn)
        elif board_full(self.board):
            await self.end_game(draw=True)
        else:
            await self.switch_turn()

    async def on_timeout(self):
        """Action à effectuer lorsque le temps est écoulé."""
        self.disable_all_buttons()

        if self.message:
            await self.message.edit(view=self)
            if not self.endgame:
                await self.message.channel.send(
                    "⌛ Temps écoulé ! La partie est terminée.",
                    reference=self.message
                )

        self.stop()

# =========================================
# Classe des boutons pour les colonnes
# =========================================

class Puissance4Button(discord.ui.Button):
    """Bouton pour jouer dans une colonne spécifique."""
    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        super().__init__(emoji=EMOJIS[col], row=row)
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Gestion du clic sur le bouton."""

        if self.p4view.endgame:
            await interaction.response.send_message(
                "🚫 La partie est terminée.", 
                ephemeral=True
            )
            return

        if interaction.user != self.p4view.turn:
            await interaction.response.send_message(
                "⏳ Ce n'est pas votre tour.", 
                ephemeral=True
            )
            return

        await interaction.response.defer()
        await self.p4view.play_turn(self.col)

# =========================================
# Classe du bouton pour Rejouer
# =========================================

class RejouerButton(discord.ui.Button):
    """Bouton pour relancer une partie de Puissance 4."""
    def __init__(self, game_view: Puissance4View):
        super().__init__(label="🔄 Rejouer", style=discord.ButtonStyle.success)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user not in self.game_view.players:
            await interaction.response.send_message(
                "❌ Seuls les joueurs de la partie peuvent relancer le jeu.", 
                ephemeral=True
            )
            return

        new_view = Puissance4View(
            self.game_view.players[0],
            self.game_view.players[1],
            scores=self.game_view.scores
        )
        new_view.message = self.game_view.message

        await interaction.response.edit_message(
            embed=new_view.get_embed(),
            view=new_view
        )

# =========================================
# Cog Discord pour la commande /puissance4
# =========================================

class Puissance4(commands.Cog):
    """Cog pour gérer la commande /puissance4."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member):
        """Commande slash pour lancer une partie entre deux joueurs."""
        joueur1 = cast(discord.Member, interaction.user)
        joueur2 = adversaire
        if joueur1 == joueur2 or joueur1.bot or joueur2.bot:
            await interaction.response.send_message(
                "❌ Impossible de jouer.", 
                ephemeral=True
            )
            return
        
        view = Puissance4View(joueur1, joueur2)
        await interaction.response.send_message(
            embed=view.get_embed(), 
            view=view
        )
        view.message = await interaction.original_response()

# =========================================
# Configuration du cog
# =========================================

async def setup(bot: commands.Bot):
    """Ajoute le cog Puissance4 au bot."""
    await bot.add_cog(Puissance4(bot))
