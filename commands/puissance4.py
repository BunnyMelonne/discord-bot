# =========================================
# Importations
# =========================================

import discord
from discord.ext import commands
from typing import Optional, cast
from datetime import datetime, timedelta, timezone
import random
import asyncio

# =========================================
# Constantes du jeu
# =========================================

ROWS, COLS = 6, 7
EMPTY_CELL = "<:null:1405700337611837460>"
SPACER = "<:spacer:1408471845950324829>"
PIECES = {"p1": "🔴", "p2": "🔵"}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
COLORS = {"p1": discord.Color(0xD22D39), "p2": discord.Color.blue()}

def disable_all_buttons(view: discord.ui.View):
    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.disabled = True

# =========================================
# Classe Board
# =========================================

class Board:
    def __init__(self):
        self.grid: list[list[str]] = [[EMPTY_CELL for _ in range(COLS)] for _ in range(ROWS)]

    def drop_piece(self, col: int, piece: str) -> bool:
        if not 0 <= col < COLS:
            return False
        for row in reversed(self.grid):
            if row[col] == EMPTY_CELL:
                row[col] = piece
                return True
        return False

    def check_win(self, piece: str) -> bool:
        # Horizontale →
        for r in range(ROWS):
            for c in range(COLS - 3):
                if all(self.grid[r][c + i] == piece for i in range(4)):
                    return True
        # Verticale ↓
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
        return not any(cell == EMPTY_CELL for row in self.grid for cell in row)

# =========================================
# Vue du jeu
# =========================================

class Puissance4View(discord.ui.View):
    def __init__(self, p1: discord.Member, p2: discord.Member, scores: Optional[dict] = None):
        super().__init__(timeout=120)
        self.board = Board()
        self.players = [p1, p2]
        self.current_player = random.choice(self.players)
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.scores = scores or {p1.id: 0, p2.id: 0}
        self.message: Optional[discord.Message] = None
        self.last_move: Optional[int] = None
        self.winner: Optional[discord.Member] = None
        self.draw: bool = False
        self.timeout_expired: bool = False
        self.lock = asyncio.Lock()
        self.init_buttons()

    # -------------------------------
    # Validation des interactions
    # -------------------------------

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        user = interaction.user

        if (self.winner or self.draw) and user in self.players:
            return True

        if user == self.current_player:
            return True

        await interaction.response.send_message(
            "⏳ Vous ne pouvez pas interagir pour le moment.",
            ephemeral=True
        )
        return False

    # -------------------------------
    # Gestion des boutons
    # -------------------------------

    def init_buttons(self):
        self.clear_items()
        for i in range(COLS):
            row = 0 if i < 4 else 1
            self.add_item(Puissance4Button(i, self, row=row))
        self.update_buttons()

    def get_style(self) -> discord.ButtonStyle:
        if self.current_player == self.players[0]:
            return discord.ButtonStyle.danger
        return discord.ButtonStyle.primary

    def update_buttons(self):
        style = self.get_style()
        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board.grid[0][button.col] != EMPTY_CELL
                button.style = style

    def add_endgame_buttons(self):
        self.add_item(RejouerButton(self))
        self.add_item(ArreterButton(self))
    
    # -------------------------------
    # Affichage
    # -------------------------------

    def get_board_display(self) -> str:
        arrow_row = ["🔻" if self.last_move == i else SPACER for i in range(COLS)]
        lines = [" ".join(EMOJIS), " ".join(arrow_row)]
        lines += [" ".join(row) for row in self.board.grid]
        return "\n".join(lines)

    def get_status_message(self) -> str:
        if self.winner:
            message = f"🎉 {self.winner.mention} a gagné !"
            if self.timeout_expired:
                message += f"\n⏳ {self.current_player.mention} n'a pas joué à temps."
            return message

        if self.draw:
            return "🤝 Match nul !"

        return f"👉 Tour de : {self.current_player.mention}"
    
    def get_timeout_timestamp(self) -> str:
        if self.winner or self.draw or self.timeout_expired:
            return ""
        future_time = datetime.now(tz=timezone.utc) + timedelta(seconds=120)
        unix_ts = int(future_time.timestamp())
        return f"\n🕐 Fin du tour <t:{unix_ts}:R>"

    def get_score_display(self) -> str:
        p1, p2 = self.players
        return (
            f"**🏆 Victoires :**\n"
            f"{self.pieces[p1.id]} {p1.mention} : **{self.scores[p1.id]}**\n"
            f"{self.pieces[p2.id]} {p2.mention} : **{self.scores[p2.id]}**"
        )

    def get_color(self) -> discord.Color:
        if self.winner: 
            return discord.Color.green()
        if self.draw: 
            return discord.Color.greyple()
        return self.colors[self.current_player.id]

    def get_embed(self) -> discord.Embed:
        description = (
            f"{self.get_board_display()}\n\n"
            f"{self.get_status_message()}"
            f"{self.get_timeout_timestamp()}\n\n"
            f"{self.get_score_display()}"
        )
        embed = discord.Embed(
            title="✦━─ Puissance 4 ─━✦",
            description=description,
            color=self.get_color()
        ).set_thumbnail(url="https://i.imgur.com/re2Z5fM.png")
        return embed

    # -------------------------------
    # Gestion des tours
    # -------------------------------

    async def play_turn(self, col: int):
        async with self.lock:
            piece = self.pieces[self.current_player.id]
            if not self.board.drop_piece(col, piece):
                return

            self.last_move = col

            if self.check_game_end(piece):
                self.end_game()
            else:
                self.switch_turn()

            self.update_buttons()
            await self._update_view()

    def check_game_end(self, piece: str) -> bool:
        has_winner = self.board.check_win(piece)
        is_draw = self.board.is_full()

        if has_winner:
            self.winner = self.current_player
        elif is_draw:
            self.draw = True
        else:
            return False

        return True

    def end_game(self):
        if self.winner:
            self.scores[self.winner.id] += 1
        self.clear_items()
        self.add_endgame_buttons()

    def switch_turn(self):
        current_index = self.players.index(self.current_player)
        self.current_player = self.players[1 - current_index]

    async def _update_view(self):
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)

    # -------------------------------
    # Gestion du Timeout
    # -------------------------------

    async def on_timeout(self):
        self.stop()
        try:
            if not (self.winner or self.draw):
                self.winner = next(p for p in self.players if p != self.current_player)
                self.scores[self.winner.id] += 1
                self.timeout_expired = True

            disable_all_buttons(self)
            await self._update_view()
        except discord.NotFound:
            pass

# =========================================
# Bouton du placement des jetons
# =========================================

class Puissance4Button(discord.ui.Button):
    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        super().__init__(emoji=EMOJIS[col], row=row)
        self.col = col
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.game_view.play_turn(self.col)

# =========================================
# Boutons pour rejouer ou annuler
# =========================================

class EndgameButton(discord.ui.Button):
    def __init__(self, game_view: Puissance4View, label: str, style: discord.ButtonStyle):
        super().__init__(label=label, style=style)
        self.game_view = game_view


class RejouerButton(EndgameButton):
    def __init__(self, game_view: Puissance4View):
        super().__init__(game_view, label="🔄 Rejouer", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        new_view = Puissance4View(*self.game_view.players, scores=self.game_view.scores)
        new_view.message = self.game_view.message
        self.game_view.stop()
        await interaction.response.edit_message(embed=new_view.get_embed(), view=new_view)


class ArreterButton(EndgameButton):
    def __init__(self, game_view: Puissance4View):
        super().__init__(game_view, label="🛑 Arrêter", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        self.game_view.stop()
        disable_all_buttons(self.game_view)
        await interaction.response.edit_message(view=self.game_view)
        await interaction.followup.send(f"🛑 {interaction.user.mention} a arrêté le jeu.")

# =========================================
# Confirmation View
# =========================================

class ConfirmationView(discord.ui.View):
    def __init__(self, player1: discord.Member, player2: discord.Member, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.player1, self.player2 = player1, player2
        self.confirmed: Optional[bool] = None
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.player2:
            await interaction.response.send_message(
                "❌ Seul l'adversaire invité peut cliquer.", 
                ephemeral=True
            )
            return False
        return True

    async def _handle_response(self, interaction: discord.Interaction):
        await interaction.response.defer()
        await self.finalize()

    async def finalize(self):
        self.stop()
        if not self.message:
            return
        
        if self.confirmed:
            view = Puissance4View(self.player1, self.player2)
            view.message = self.message
            embed = view.get_embed()
        else:
            view = self
            embed = self._get_rejection_embed()
            disable_all_buttons(self)

        await self.message.edit(content=None, embed=embed, view=view)

    def _get_rejection_embed(self):
        if self.confirmed is False:
            embed = discord.Embed(
                title="❌ Invitation refusée",
                description=f"{self.player2.mention} a décliné l'invitation.",
                color=discord.Color.red()
            )
        else:
            embed = discord.Embed(
                title="⌛ Invitation expirée",
                description=f"{self.player2.mention} n'a pas répondu à temps.",
                color=discord.Color.light_grey()
            )
        return embed

    async def on_timeout(self):
        await self.finalize()

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _):
        self.confirmed = True
        await self._handle_response(interaction)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _):
        self.confirmed = False
        await self._handle_response(interaction)


# =========================================
# Puissance 4
# =========================================

class Puissance4(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @discord.app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member):
        player1 = cast(discord.Member, interaction.user)
        player2 = cast(discord.Member, adversaire)

        if player1 == player2 or player1.bot or player2.bot:
            await interaction.response.send_message(
                "❌ Impossible de jouer contre cet utilisateur.", 
                ephemeral=True
            )
            return

        view = ConfirmationView(player1, player2)

        await interaction.response.send_message(
            content=f"{player2.mention}",
            embed=discord.Embed(
                title="Souhaitez-vous jouer au Puissance 4 ?",
                description=f"{player1.mention} souhaite faire une partie avec vous.",
                color=discord.Color.blurple()
            ),
            view=view
        )

        message = await interaction.original_response()
        view.message = await message.channel.fetch_message(message.id)

        await view.wait()

# =========================================
# Setup cog
# =========================================

async def setup(bot: commands.Bot):
    await bot.add_cog(Puissance4(bot))