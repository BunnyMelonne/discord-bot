import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional

# --- Constants ---
ROWS = 6
COLS = 7
PIECES = {"p1": "🔴", "p2": "🔵"}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

# --- Game Logic ---
def create_board():
    """Crée et retourne un plateau vide de Puissance 4."""
    return [["⚪" for _ in range(COLS)] for _ in range(ROWS)]

def display_board(board):
    """Retourne une représentation textuelle du plateau avec les pièces."""
    return "\n".join("".join(row) for row in board) + "\n" + "".join(EMOJIS)

def drop_piece(board, col, piece):
    """Place une pièce dans la colonne donnée. Retourne True si réussi, False sinon."""
    if not 0 <= col < COLS:
        return False
    for row in reversed(board):
        if row[col] == "⚪":
            row[col] = piece
            return True
    return False

def check_win(board, piece):
    """
    Vérifie si le joueur possédant le pion 'piece' a gagné.
    Retourne True si oui, False sinon.
    """
    # Horizontal
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True

    # Vertical
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True

    # Diagonale ↘
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True

    # Diagonale ↙
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r + i][c - i] == piece for i in range(4)):
                return True

    return False

def board_full(board):
    """Retourne True si le plateau est plein, False sinon."""
    return all(cell != "⚪" for row in board for cell in row)

# --- Discord UI ---
class Puissance4View(discord.ui.View):
    """Vue principale pour gérer une partie de Puissance 4 sur Discord."""
    def __init__(self, p1: discord.Member, p2: discord.Member):
        super().__init__(timeout=300)
        self.board = create_board()
        self.players = [p1, p2]
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.turn = p1
        self.message: Optional[discord.Message] = None

        for i in range(COLS):
            self.add_item(Puissance4Button(i, self))

    def disable_all_buttons(self):
        """Désactive tous les boutons du plateau."""
        for child in self.children:
            child.disabled = True  # type: ignore

    def get_embed(self):
        """Retourne un embed représentant l'état actuel du plateau."""
        piece_emoji = self.pieces[self.turn.id]
        return discord.Embed(
            title="Puissance 4",
            description=display_board(self.board),
            color=discord.Color.red() if self.turn == self.players[0] else discord.Color.blue()
        ).set_footer(text=f"C'est au tour de {piece_emoji} {self.turn.display_name}")

    async def handle_invalid_move(self, interaction: discord.Interaction):
        """Envoie un message si un joueur essaie de jouer dans une colonne invalide."""
        await interaction.followup.send("❌ Colonne pleine ou invalide !", ephemeral=True)

    async def end_game(self, title: str, color: discord.Color):
        """Termine la partie et met à jour l'embed."""
        self.disable_all_buttons()
        embed = discord.Embed(
            title=title,
            description=display_board(self.board),
            color=color
        )
        if self.message:
            await self.message.edit(embed=embed, view=self)
        self.stop()

    async def switch_turn(self):
        """Change le tour au joueur suivant et met à jour l'embed."""
        self.turn = self.players[1] if self.turn == self.players[0] else self.players[0]
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)  # type: ignore

    async def play_turn(self, col: int, interaction: discord.Interaction):
        """Gère le tour actuel d'un joueur."""
        piece = self.pieces[self.turn.id]

        if not drop_piece(self.board, col, piece):
            await self.handle_invalid_move(interaction)
            return

        if check_win(self.board, piece):
            await self.end_game("🎉 Victoire !", discord.Color.green())
            return

        if board_full(self.board):
            await self.end_game("🤝 Match nul", discord.Color.gold())
            return

        await self.switch_turn()

    async def on_timeout(self):
        """Gère la fin de partie si le temps est écoulé."""
        await self.end_game("⏳ Temps écoulé", discord.Color.dark_grey())

class Puissance4Button(discord.ui.Button):
    """Bouton représentant une colonne dans le plateau de Puissance 4."""
    def __init__(self, col: int, game_view: Puissance4View):
        super().__init__(style=discord.ButtonStyle.secondary, emoji=EMOJIS[col])
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Gère l'action lors du clic sur le bouton."""
        if interaction.user != self.p4view.turn:
            await interaction.response.send_message("⏳ Ce n'est pas votre tour.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.p4view.play_turn(self.col, interaction)

# --- Cog ---
class Puissance4(commands.Cog):
    """Cog pour gérer la commande /puissance4."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member):
        """Lance une partie entre l'utilisateur et son adversaire."""
        joueur1 = interaction.user
        joueur2 = adversaire
        if joueur1 == joueur2 or joueur1.bot or joueur2.bot:
            await interaction.response.send_message("❌ Impossible de jouer.", ephemeral=True)
            return

        view = Puissance4View(joueur1, joueur2) # type: ignore
        await interaction.response.send_message(embed=view.get_embed(), view=view)
        view.message = await interaction.original_response()

async def setup(bot: commands.Bot):
    """Ajoute le cog Puissance4 au bot."""
    await bot.add_cog(Puissance4(bot))