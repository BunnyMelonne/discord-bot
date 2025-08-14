# ==========================
# Importations
# ==========================
import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, cast

# ==========================
# Constantes du jeu
# ==========================
ROWS, COLS = 6, 7  # Dimensions du plateau
PIECES = {"p1": "🔴", "p2": "🔵"}  # Émojis pour chaque joueur
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]  # Émojis des colonnes
COLORS = {"p1": discord.Color.red(), "p2": discord.Color.blue()}  # Couleurs des boutons des joueurs

# ==========================
# Fonctions utilitaires du jeu
# ==========================

def create_board():
    """Crée un plateau vide (6x7) avec des cercles blancs."""
    return [["⚪" for _ in range(COLS)] for _ in range(ROWS)]

def display_board(board):
    """Retourne une chaîne représentant le plateau avec les émojis des colonnes."""
    return "\n".join(" ".join(row) for row in board) + "\n" + " ".join(EMOJIS)

def drop_piece(board, col, piece):
    """Place un jeton dans la colonne choisie si possible. Retourne True si réussi."""
    if not 0 <= col < COLS:
        return False
    for row in reversed(board):
        if row[col] == "⚪":
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
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r + i][c - i] == piece for i in range(4)):
                return True
    return False

def board_full(board):
    """Vérifie si le plateau est rempli."""
    return all(cell != "⚪" for row in board for cell in row)

# ==========================
# Classe de la vue du jeu (View)
# ==========================

class Puissance4View(discord.ui.View):
    """
    Vue principale gérant l'état de la partie, les tours, et les interactions avec les boutons.
    """
    def __init__(self, p1: discord.Member, p2: discord.Member):
        super().__init__(timeout=300)
        self.board = create_board()
        self.players = [p1, p2]
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.turn = p1
        self.message: Optional[discord.Message] = None

        # Création des boutons pour chaque colonne
        for i in range(COLS):
            self.add_item(Puissance4Button(i, self))

        self.update_buttons()

    def update_buttons(self):
        """Met à jour le style et l'état des boutons selon le tour et le plateau."""
        current_style = (
            discord.ButtonStyle.danger if self.turn == self.players[0] 
            else discord.ButtonStyle.primary
        )

        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board[0][button.col] != "⚪"
                button.style = current_style

    def disable_all_buttons(self):
        """Désactive tous les boutons."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    def get_embed(self, winner: Optional[discord.Member] = None, draw: bool = False):
        """Crée un embed représentant l'état actuel de la partie."""
        description = display_board(self.board) + "\n\n" + (
            f"🎉 {winner.mention} a gagné !" if winner else
            "🤝 Match nul !" if draw else
            f"Tour de: {self.pieces[self.turn.id]} {self.turn.mention}"
        )

        color = (
            discord.Color.green() if winner else
            discord.Color.greyple() if draw else
            self.colors[self.turn.id]
        )

        return (
            discord.Embed(title="Puissance 4", description=description, color=color)
            .set_thumbnail(url="https://i.imgur.com/NjrISNE.png")
        )

    async def end_game(self, winner: Optional[discord.Member] = None):
        """Met fin à la partie et met à jour l'affichage."""
        self.disable_all_buttons()
        draw = not winner and board_full(self.board)
        if self.message:
            await self.message.edit(embed=self.get_embed(winner=winner, draw=draw), view=self)
        self.stop()

    async def switch_turn(self):
        """Change le joueur actif et met à jour les boutons."""
        self.turn = self.players[1] if self.turn == self.players[0] else self.players[0]
        self.update_buttons()
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)

    async def play_turn(self, col: int):
        """Joue un tour complet: placer le jeton, vérifier victoire, changement de tour."""
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

# ==========================
# Classe du bouton
# ==========================

class Puissance4Button(discord.ui.Button):
    """Bouton représentant une colonne où le joueur peut placer un jeton."""
    def __init__(self, col: int, game_view: Puissance4View):
        super().__init__(style=discord.ButtonStyle.secondary, emoji=EMOJIS[col])
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Gestion du clic sur le bouton."""
        if interaction.user != self.p4view.turn:
            await interaction.response.send_message("⏳ Ce n'est pas votre tour.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.p4view.play_turn(self.col)

# ==========================
# Cog Discord pour la commande
# ==========================

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

# ==========================
# Setup du Cog
# ==========================

async def setup(bot: commands.Bot):
    await bot.add_cog(Puissance4(bot))
