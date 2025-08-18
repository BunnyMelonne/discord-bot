# =========================================
# Importations
# =========================================

import discord
from discord import app_commands
from discord.ext import commands
from typing import Optional, cast
import random
import asyncio

# =========================================
# Constantes du jeu
# =========================================

ROWS, COLS = 6, 7
EMPTY  = "<:null:1405700337611837460>"
PIECES = {"p1": "🔴", "p2": "🔵"}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]
COLORS = {"p1": discord.Color.red(), "p2": discord.Color.blue()}

# =========================================
# Classe Board
# =========================================

class Board:
    """Classe représentant la grille et les règles du jeu Puissance 4."""
    def __init__(self):
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    def drop_piece(self, col: int, piece: str) -> bool:
        """Place une pièce dans la colonne spécifiée."""
        if not 0 <= col < COLS:
            return False
        for row in reversed(self.grid):
            if row[col] == EMPTY:
                row[col] = piece
                return True
        return False

    def check_win(self, piece: str) -> bool:
        """Vérifie si un joueur a aligné 4 jetons."""
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

    def full(self) -> bool:
        """Vérifie si la grille est pleine."""
        return not any(cell == EMPTY for row in self.grid for cell in row)

    def display(self) -> str:
        """Retourne l'affichage complet de la grille."""
        lines = [" ".join(EMOJIS)]
        lines += [" ".join(row) for row in self.grid]
        return "\n".join(lines)

# =========================================
# Classe de la vue du jeu (View)
# =========================================

class Puissance4View(discord.ui.View):
    """Vue pour le jeu Puissance 4."""
    def __init__(self, p1: discord.Member, p2: discord.Member, scores: Optional[dict] = None):
        super().__init__(timeout=300)
        self.board = Board()
        self.players = [p1, p2]
        self.current_player = random.choice(self.players)
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.scores = scores or {p1.id: 0, p2.id: 0}
        self.message: Optional[discord.Message] = None
        self.last_move: Optional[int] = None
        self.winner: Optional[discord.Member] = None
        self.endgame: bool = False
        self.draw: bool = False
        self.lock = asyncio.Lock()
        self.init_buttons()

    # -------------------------------
    # Validation du joueur
    # -------------------------------

    async def ensure_player(self, interaction: discord.Interaction, require_turn: bool = False) -> bool:
        """Vérifie si l'utilisateur est joueur et si c'est son tour si requis."""
        user = interaction.user
        if user not in self.players:
            msg = "❌ Vous n'êtes pas un joueur de cette partie."
        elif require_turn and user != self.current_player:
            msg = "⏳ Ce n'est pas votre tour."
        else:
            return True

        await interaction.response.send_message(msg, ephemeral=True)
        return False

    # -------------------------------
    # Gestion boutons
    # -------------------------------

    def init_buttons(self) -> None:
        """Initialise les boutons pour chaque colonne."""
        self.clear_items()
        for i in range(COLS):
            self.add_item(Puissance4Button(i, self, row=i // 4))
        self.update_buttons()

    def get_style(self) -> discord.ButtonStyle:
        """Retourne le style du bouton selon le joueur actuel."""
        if self.current_player == self.players[0]:
            return discord.ButtonStyle.danger
        return discord.ButtonStyle.primary

    def update_buttons(self) -> None:
        """Met à jour l'état des boutons en fonction de la grille."""
        style = self.get_style()
        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board.grid[0][button.col] != EMPTY
                button.style = style

    def disable_all_buttons(self) -> None:
        """Désactive tous les boutons."""
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    def add_endgame_buttons(self) -> None:
        """Ajoute les boutons de fin de partie."""
        self.add_item(RejouerButton(self))
        self.add_item(ArreterButton(self))

    # -------------------------------
    # Affichage et statut
    # -------------------------------

    def get_board_display(self) -> str:
        """Retourne l'affichage complet de la grille avec dernier coup."""
        display = ""
        if self.last_move is not None:
            display += f"Dernier coup : {EMOJIS[self.last_move]}\n\n"
        display += self.board.display()
        return display

    def get_status_message(self) -> str:
        """Retourne le message de statut du jeu."""
        if self.winner: 
            return f"🎉 {self.winner.mention} a gagné !"
        if self.draw: 
            return "🤝 Match nul !"
        return f"Tour de : {self.pieces[self.current_player.id]} {self.current_player.mention}"

    def get_score_display(self) -> str:
        """Retourne l'affichage des scores des joueurs."""
        p1, p2 = self.players
        return (
            f"**🏆 Victoires :**\n"
            f"{self.pieces[p1.id]} {p1.mention} : **{self.scores[p1.id]}**\n"
            f"{self.pieces[p2.id]} {p2.mention} : **{self.scores[p2.id]}**"
        )

    def get_color(self) -> discord.Color:
        """Retourne la couleur de l'embed selon l'état du jeu."""
        if self.winner: 
            return discord.Color.green()
        if self.draw: 
            return discord.Color.greyple()
        return self.colors[self.current_player.id]

    def get_embed(self) -> discord.Embed:
        """Crée l'embed pour afficher l'état du jeu."""
        description = (
            f"{self.get_board_display()}\n\n"
            f"{self.get_status_message()}\n\n"
            f"{self.get_score_display()}"
        )
        return discord.Embed(
            title="✦━─ Puissance 4 ─━✦", 
            description=description, 
            color=self.get_color()
        ).set_thumbnail(url="https://i.imgur.com/NjrISNE.png")
    
    # -------------------------------
    # Gestion des tours
    # -------------------------------

    async def play_turn(self, col: int) -> None:
        """Joue un tour pour le joueur actuel."""
        async with self.lock:
            piece = self.pieces[self.current_player.id]
            if not self.board.drop_piece(col, piece):
                return

            self.last_move = col

            if self.check_game_end(piece):
                self.end_game()
            else:
                self.switch_turn()

            await self._update_view()

    def check_game_end(self, piece: str) -> bool:
        """Vérifie si la partie est terminée."""
        if self.board.check_win(piece):
            self.winner = self.current_player
            return True
        if self.board.full():
            self.draw = True
            return True
        return False

    def end_game(self) -> None:
        """Termine la partie et met à jour les scores."""
        if self.winner:
            self.scores[self.winner.id] += 1
        self.endgame = True
        self.clear_items()
        self.add_endgame_buttons()

    def switch_turn(self) -> None:
        """Change le tour du joueur."""
        self.current_player = self.players[1 - self.players.index(self.current_player)]
        self.update_buttons()

    async def _update_view(self) -> None:
        if self.message:
            await self.message.edit(embed=self.get_embed(), view=self)

    async def on_timeout(self) -> None:
        """Gère le timeout de la vue."""
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
# Classe des boutons
# =========================================

class Puissance4Button(discord.ui.Button):
    """Bouton pour jouer un coup dans Puissance 4."""
    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        super().__init__(emoji=EMOJIS[col], row=row)
        self.col = col
        self.p4view = game_view

    async def callback(self, interaction: discord.Interaction) -> None:
        if not await self.p4view.ensure_player(interaction, require_turn=True):
            return
        
        if self.p4view.endgame:
            await interaction.response.send_message(
                "🚫 La partie est terminée.", 
                ephemeral=True
            )
            return
        
        await interaction.response.defer()
        await self.p4view.play_turn(self.col)

class RejouerButton(discord.ui.Button):
    """Bouton pour rejouer une partie de Puissance 4."""
    def __init__(self, game_view: Puissance4View):
        super().__init__(label="🔄 Rejouer", style=discord.ButtonStyle.success)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction) -> None:
        if not await self.game_view.ensure_player(interaction):
            return

        self.game_view.stop()

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

class ArreterButton(discord.ui.Button):
    """Bouton pour arrêter la partie de Puissance 4."""
    def __init__(self, game_view: Puissance4View):
        super().__init__(label="⏹️ Arrêter", style=discord.ButtonStyle.danger)
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction) -> None:
        if not await self.game_view.ensure_player(interaction):
            return
        
        if self.game_view.message:
            await interaction.response.edit_message(
                embed=discord.Embed(
                    title="✦━─ Puissance 4 ─━✦",
                    description=f"⏹️ La partie a été arrêtée par {interaction.user.mention}.",
                    color=discord.Color.dark_grey()
                ).set_thumbnail(url="https://i.imgur.com/NjrISNE.png"),
                view=None
            )

        self.game_view.stop()

# =========================================
# Cog Discord
# =========================================

class Puissance4(commands.Cog):
    """Cog pour le jeu Puissance 4."""
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member) -> None:
        joueur1 = cast(discord.Member, interaction.user)
        joueur2 = adversaire

        if joueur1 == joueur2 or joueur1.bot or joueur2.bot:
            await interaction.response.send_message(
                "❌ Impossible de jouer.", 
                ephemeral=True
            )
            return

        view = Puissance4View(joueur1, joueur2)
        await interaction.response.send_message(embed=view.get_embed(), view=view)
        message = await interaction.original_response()
        view.message = await message.channel.fetch_message(message.id)


# =========================================
# Setup du cog
# =========================================

async def setup(bot: commands.Bot):
    """Fonction pour ajouter le cog à l'instance du bot."""
    await bot.add_cog(Puissance4(bot))
