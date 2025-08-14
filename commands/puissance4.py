import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, cast

ROWS, COLS = 6, 7
PIECES = {"p1": "🔴", "p2": "🔵"}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
COLORS = {"p1": discord.Color.red(), "p2": discord.Color.blue()}

def create_board():
    return [["⚪" for _ in range(COLS)] for _ in range(ROWS)]

def display_board(board):
    return "\n".join(" ".join(row) for row in board) + "\n" + " ".join(EMOJIS)

def drop_piece(board, col, piece):
    if not 0 <= col < COLS:
        return False
    for row in reversed(board):
        if row[col] == "⚪":
            row[col] = piece
            return True
    return False

def check_win(board, piece):
    for r in range(ROWS):
        for c in range(COLS - 3):
            if all(board[r][c + i] == piece for i in range(4)):
                return True
            
    for r in range(ROWS - 3):
        for c in range(COLS):
            if all(board[r + i][c] == piece for i in range(4)):
                return True
            
    for r in range(ROWS - 3):
        for c in range(COLS - 3):
            if all(board[r + i][c + i] == piece for i in range(4)):
                return True
            
    for r in range(ROWS - 3):
        for c in range(3, COLS):
            if all(board[r + i][c - i] == piece for i in range(4)):
                return True
            
    return False

def board_full(board):
    return all(cell != "⚪" for row in board for cell in row)

class Puissance4View(discord.ui.View):
    def __init__(self, p1: discord.Member, p2: discord.Member):
        super().__init__(timeout=300)
        self.board = create_board()
        self.players = [p1, p2]
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.turn = p1
        self.message: Optional[discord.Message] = None

        for i in range(COLS):
            self.add_item(Puissance4Button(i, self))

        self.update_buttons()

    def update_buttons(self):
        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board[0][button.col] != "⚪"

                if self.turn == self.players[0]:
                    button.style = discord.ButtonStyle.danger 
                else:
                    button.style = discord.ButtonStyle.primary

    def disable_all_buttons(self):
        for child in self.children:
            child.disabled = True # type: ignore

    def get_embed(self, winner: Optional[discord.Member] = None, draw: bool = False):
        description = display_board(self.board) + "\n\n"

        if winner:
            description += f"🎉 {winner.mention} a gagné !"
        elif draw:
            description += "🤝 Match nul !"
        else:
            piece_emoji = self.pieces[self.turn.id]
            description += f"Tour de: {piece_emoji} {self.turn.mention}"

        return discord.Embed(
            title="Puissance 4",
            description=description,
            color=self.colors[winner.id if winner else self.turn.id]
        ).set_thumbnail(url="https://i.imgur.com/NjrISNE.png")

    async def handle_invalid_move(self, interaction: discord.Interaction):
        await interaction.followup.send("❌ Colonne pleine ou invalide !", ephemeral=True)

    async def end_game(self, winner: Optional[discord.Member] = None):
        self.disable_all_buttons()

        if winner:
            embed = self.get_embed(winner)
        else:
            embed = self.get_embed(draw=board_full(self.board))

        if self.message:
            await self.message.edit(embed=embed, view=self)

        self.stop()

    async def switch_turn(self):
        self.turn = self.players[1] if self.turn == self.players[0] else self.players[0]
        self.update_buttons()
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)

    async def play_turn(self, col: int, interaction: discord.Interaction):
        piece = self.pieces[self.turn.id]
        if not drop_piece(self.board, col, piece):
            await self.handle_invalid_move(interaction)
            return

        self.update_buttons()

        if check_win(self.board, piece):
            await self.end_game(self.turn)
            return
        
        if board_full(self.board):
            await self.end_game()
            return
        
        await self.switch_turn()

    async def on_timeout(self):
        if self.message:
            await self.end_game()
            await self.message.channel.send("⌛ Temps écoulé, la partie est terminée !")
        else:
            self.stop()

class Puissance4Button(discord.ui.Button):
    def __init__(self, col: int, game_view: Puissance4View):
        super().__init__(style=discord.ButtonStyle.secondary, emoji=EMOJIS[col])
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction):
        if interaction.user != self.p4view.turn:
            await interaction.response.send_message("⏳ Ce n'est pas votre tour.", ephemeral=True)
            return
        await interaction.response.defer()
        await self.p4view.play_turn(self.col, interaction)

class Puissance4(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member):
        joueur1 = cast(discord.Member, interaction.user)
        joueur2 = adversaire
        if joueur1 == joueur2 or joueur1.bot or joueur2.bot:
            await interaction.response.send_message("❌ Impossible de jouer.", ephemeral=True)
            return
        view = Puissance4View(joueur1, joueur2)
        await interaction.response.send_message(embed=view.get_embed(), view=view)
        view.message = await interaction.original_response()

async def setup(bot: commands.Bot):
    await bot.add_cog(Puissance4(bot))