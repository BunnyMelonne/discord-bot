# =========================================
# Importations
# =========================================

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, cast

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
    def __init__(self, p1: discord.Member, p2: discord.Member):
        super().__init__(timeout=300)
        self.board = create_board()
        self.players = [p1, p2]
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.turn = p1
        self.message: Optional[discord.Message] = None
        self.scores = {p1.id: 0, p2.id: 0}

        self.init_buttons()

    def init_buttons(self):
        """Réinitialise les boutons de colonnes."""
        self.clear_items()
        for i in range(COLS):
            row = 0 if i < 4 else 1
            self.add_item(Puissance4Button(i, self, row=row))
        self.update_buttons()

    def update_buttons(self):
        """Met à jour le style et l'état des boutons selon le tour et le plateau."""
        current_style = (
            discord.ButtonStyle.danger if self.turn == self.players[0] 
            else discord.ButtonStyle.primary
        )

        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board[0][button.col] != EMPTY
                button.style = current_style

    def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    def get_board_display(self):
        return display_board(self.board)

    def get_status_message(self, winner: Optional[discord.Member] = None, draw: bool = False):
        if winner:
            return f"🎉 {winner.mention} a gagné !"
        if draw:
            return "🤝 Match nul !"
        return f"Tour de : {self.pieces[self.turn.id]} {self.turn.mention}"

    def get_score_display(self):
        p1, p2 = self.players
        return (
            f"**🏆 Victoires :**\n"
            f"{self.pieces[p1.id]} {p1.mention} : **{self.scores[p1.id]}**\n"
            f"{self.pieces[p2.id]} {p2.mention} : **{self.scores[p2.id]}**"
        )

    def get_color(self, winner: Optional[discord.Member] = None, draw: bool = False):
        if winner:
            return discord.Color.green()
        if draw:
            return discord.Color.greyple()
        return self.colors[self.turn.id]

    def get_embed(self, winner: Optional[discord.Member] = None, draw: bool = False):
        description = (
            f"{self.get_board_display()}\n\n"
            f"{self.get_status_message(winner, draw)}\n\n"
            f"{self.get_score_display()}"
        )
        color = self.get_color(winner, draw)
        return (
            discord.Embed(title="✦━─ Puissance 4 ─━✦", description=description, color=color)
            .set_thumbnail(url="https://i.imgur.com/NjrISNE.png")
        )

    async def end_game(self, winner: Optional[discord.Member] = None):
        draw = not winner and board_full(self.board)

        if winner:
            self.scores[winner.id] += 1

        self.clear_items()
        self.add_item(RejouerButton(self))
        if self.message:
            await self.message.edit(embed=self.get_embed(winner=winner, draw=draw), view=self)

    async def switch_turn(self):
        self.turn = self.players[1 - self.players.index(self.turn)]
        self.update_buttons()
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)

    async def play_turn(self, col: int):
        piece = self.pieces[self.turn.id]
        if not drop_piece(self.board, col, piece):
            return

        if check_win(self.board, piece):
            await self.end_game(self.turn)
            return
        
        if board_full(self.board):
            await self.end_game()
            return

        await self.switch_turn()

    async def on_timeout(self):
        self.disable_all_buttons()
        if self.message:
            await self.message.edit(
                embed=self.get_embed().set_footer(text="⌛ Temps écoulé !"),
                view=self
            )
        self.stop()

    def reset_game(self):
        self.board = create_board()
        self.turn = self.players[0]
        self.init_buttons()

# =========================================
# Classe des boutons pour les colonnes
# =========================================

class Puissance4Button(discord.ui.Button):
    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        super().__init__(style=discord.ButtonStyle.secondary, emoji=EMOJIS[col], row=row)
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Gestion du clic sur le bouton."""
        if interaction.user != self.p4view.turn:
            await interaction.response.send_message("⏳ Ce n'est pas votre tour.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.p4view.play_turn(self.col)

# =========================================
# Classe du bouton pour Rejouer
# =========================================

class RejouerButton(discord.ui.Button):
    def __init__(self, game_view: Puissance4View):
        super().__init__(label="🔄 Rejouer", style=discord.ButtonStyle.success)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Gestion du clic sur le bouton Rejouer."""
        if interaction.user not in self.game_view.players:
            await interaction.response.send_message(
                "❌ Seuls les joueurs de la partie peuvent relancer le jeu.", 
                ephemeral=True
            )
            return

        self.game_view.reset_game()
        
        await interaction.response.edit_message(
            embed=self.game_view.get_embed(),
            view=self.game_view
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
            await interaction.response.send_message("❌ Impossible de jouer.", ephemeral=True)
            return
        view = Puissance4View(joueur1, joueur2)
        await interaction.response.send_message(embed=view.get_embed(), view=view)
        view.message = await interaction.original_response()

# =========================================
# Configuration du cog
# =========================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Puissance4(bot))
