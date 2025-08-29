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
# Constantes du jeu
# =========================================

ROWS, COLS = 6, 7
EMPTY_CELL = "<:null:1405700337611837460>"
SPACER = "<:spacer:1408471845950324829>"

PIECES = {"p1": "🔴", "p2": "🔵"}
COLORS = {"p1": discord.Color(0xD22D39), "p2": discord.Color.blue()}
EMOJIS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]

THUMBNAIL_URL = "https://i.imgur.com/re2Z5fM.png"


def disable_all_buttons(view: discord.ui.View) -> None:
    """Désactive tous les boutons d'une view."""
    for child in view.children:
        if isinstance(child, discord.ui.Button):
            child.disabled = True


# =========================================
# Classe Board (logique du jeu)
# =========================================

class Board:
    def __init__(self):
        self.grid: list[list[str]] = [[EMPTY_CELL for _ in range(COLS)] for _ in range(ROWS)]

    def drop_piece(self, col: int, piece: str) -> bool:
        """Tente de placer un jeton dans la colonne donnée."""
        if not 0 <= col < COLS:
            return False
        for row in reversed(self.grid):
            if row[col] == EMPTY_CELL:
                row[col] = piece
                return True
        return False

    def check_win(self, piece: str) -> bool:
        """Vérifie si un joueur a aligné 4 jetons."""

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
        """Retourne True si le plateau est rempli (match nul)."""
        return all(self.grid[0][c] != EMPTY_CELL for c in range(COLS))


# =========================================
# Vue du jeu (logique Discord)
# =========================================

class Puissance4View(discord.ui.View):
    """Vue Discord qui gère l'interface du Puissance 4 (boutons, affichage, tours)."""
    TURN_TIMEOUT = 120

    def __init__(self, p1: discord.Member, p2: discord.Member, scores: Optional[dict] = None):
        """Initialise une partie entre deux joueurs."""
        super().__init__(timeout=self.TURN_TIMEOUT)

        # Données jeu
        self.board = Board()
        self.players = [p1, p2]
        self.current_player = random.choice(self.players)
        self.pieces = {p1.id: PIECES["p1"], p2.id: PIECES["p2"]}
        self.colors = {p1.id: COLORS["p1"], p2.id: COLORS["p2"]}
        self.scores = scores or {p1.id: 0, p2.id: 0}

        # État partie
        self.message: Optional[discord.Message] = None
        self.last_move: Optional[int] = None
        self.winner: Optional[discord.Member] = None
        self.draw: bool = False
        self.timeout_expired: bool = False

        # Concurrence
        self.lock = asyncio.Lock()

        self._init_buttons()

    # -------------------------------
    # Gestion interactions
    # -------------------------------

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul le(s) bon(s) joueur(s) peut cliquer."""
        if interaction.user == self.current_player:
            return True
        
        await interaction.response.send_message(
            "⏳ Ce n'est pas ton tour.", ephemeral=True
        )
        return False

    # -------------------------------
    # Gestion des boutons
    # -------------------------------

    def _init_buttons(self) -> None:
        """Crée et ajoute les boutons pour chaque colonne."""
        self.clear_items()
        for i in range(COLS):
            self.add_item(Puissance4Button(i, self, row=0 if i < 4 else 1))
        self._update_buttons()

    def _update_buttons(self) -> None:
        """Met à jour l'état et le style des boutons en fonction du joueur courant."""
        style = (
            discord.ButtonStyle.danger
            if self.current_player == self.players[0]
            else discord.ButtonStyle.primary
        )
        for button in self.children:
            if isinstance(button, Puissance4Button):
                button.disabled = self.board.grid[0][button.col] != EMPTY_CELL
                button.style = style

    # -------------------------------
    # Affichage
    # -------------------------------

    def _get_board_display(self) -> str:
        """Retourne une représentation textuelle du plateau."""
        header = " ".join(EMOJIS)
        arrows = " ".join("🔻" if self.last_move == i else SPACER for i in range(COLS))
        grid_lines = [" ".join(row) for row in self.board.grid]
        return "\n".join([header, arrows] + grid_lines)

    def _get_status_message(self) -> str:
        """Retourne un message de statut (tour, victoire, égalité...)."""
        if self.winner:
            base = f"🎉 {self.winner.mention} a gagné !"
            if self.timeout_expired:
                base += f"\n⏳ {self.current_player.mention} n'a pas joué à temps."
            return base
        if self.draw:
            return "🤝 Match nul !"
        return f"👉 Tour de : {self.current_player.mention}"

    def _get_timeout_timestamp(self) -> str:
        """Retourne un texte indiquant le temps restant pour jouer."""
        if self.winner or self.draw:
            return ""
        future_time = datetime.now(tz=timezone.utc) + timedelta(seconds=self.TURN_TIMEOUT)
        return f"\n🕐 Fin du tour <t:{int(future_time.timestamp())}:R>"

    def _get_score_display(self) -> str:
        """Retourne l'affichage des scores des deux joueurs."""
        p1, p2 = self.players
        return (
            f"**🏆 Victoires :**\n"
            f"{self.pieces[p1.id]} {p1.mention} : **{self.scores[p1.id]}**\n"
            f"{self.pieces[p2.id]} {p2.mention} : **{self.scores[p2.id]}**"
        )

    def _get_color(self) -> discord.Color:
        """Retourne la couleur de l'embed selon l'état de la partie."""
        if self.winner:
            return discord.Color.green()
        if self.draw:
            return discord.Color.greyple()
        return self.colors[self.current_player.id]

    def get_embed(self) -> discord.Embed:
        """Construit et retourne l'embed principal du jeu."""
        description = (
            f"{self._get_board_display()}\n\n"
            f"{self._get_status_message()}"
            f"{self._get_timeout_timestamp()}\n\n"
            f"{self._get_score_display()}"
        )
        return (
            discord.Embed(description=description, color=self._get_color())
            .set_thumbnail(url=THUMBNAIL_URL)
        )

    # -------------------------------
    # Gestion des tours
    # -------------------------------

    async def play_turn(self, col: int) -> None:
        """Joue un tour : place un jeton et vérifie si la partie se termine."""
        async with self.lock:
            piece = self.pieces[self.current_player.id]
            if not self.board.drop_piece(col, piece):
                return

            self.last_move = col

            if self._check_game_end(piece):
                await self._end_game()
                return
            else:
                self._switch_turn()

            self._update_buttons()
            await self._refresh_message()

    def _check_game_end(self, piece: str) -> bool:
        """Vérifie si la partie est gagnée ou nulle."""
        if self.board.check_win(piece):
            self.winner = self.current_player
            return True
        if self.board.is_full():
            self.draw = True
            return True
        return False

    async def _end_game(self) -> None:
        """Met fin à la partie et ajoute les boutons de fin."""
        if self.winner:
            self.scores[self.winner.id] += 1
            
        self.stop()
        new_view = EndgameView(self, timeout=120)
        await self._refresh_message(view=new_view)

    def _switch_turn(self) -> None:
        """Passe au joueur suivant."""
        self.current_player = (
            self.players[1] if self.current_player == self.players[0] 
            else self.players[0]
        )

    async def _refresh_message(self, view: Optional[discord.ui.View] = None) -> None:
        """Met à jour le message Discord avec l'état actuel."""
        if self.message:
            try:
                await self.message.edit(embed=self.get_embed(), view=view or self)
            except discord.NotFound:
                pass

    # -------------------------------
    # Gestion du Timeout
    # -------------------------------

    async def on_timeout(self) -> None:
        """Gère le cas où un joueur n'a pas joué avant la fin du temps imparti."""
        async with self.lock:
            if not (self.winner or self.draw):
                self.winner = next(p for p in self.players if p != self.current_player)
                self.timeout_expired = True

            await self._end_game()

# =========================================
# Bouton du placement des jetons
# =========================================

class Puissance4Button(discord.ui.Button):
    """Bouton représentant une colonne du plateau."""

    def __init__(self, col: int, game_view: Puissance4View, row: int = 0):
        super().__init__(emoji=EMOJIS[col], row=row)
        self.col = col
        self.game_view = game_view

    async def callback(self, interaction: discord.Interaction):
        """Appelé lorsqu'un joueur clique sur une colonne."""
        await interaction.response.defer()
        await self.game_view.play_turn(self.col)

# =========================================
# Boutons pour rejouer ou annuler
# =========================================

class EndgameView(discord.ui.View):
    """Vue affichée à la fin de la partie (boutons Rejouer/Arrêter)."""

    def __init__(self, game_view: Puissance4View, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.game_view = game_view
        self.add_item(RejouerButton())
        self.add_item(ArreterButton())

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Autorise uniquement les joueurs de la partie à cliquer."""
        if interaction.user in self.game_view.players:
            return True
        await interaction.response.send_message(
            "🚫 Tu ne participes pas à cette partie.",
            ephemeral=True
        )
        return False

    async def on_timeout(self) -> None:
        """Désactive les boutons Rejouer/Arrêter en cas de timeout."""
        disable_all_buttons(self)
        if self.game_view.message:
            try:
                await self.game_view.message.edit(view=self)
            except discord.NotFound:
                pass


class RejouerButton(discord.ui.Button):
    """Bouton permettant de relancer une partie avec les mêmes joueurs."""
    def __init__(self):
        super().__init__(label="🔄 Rejouer", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction) -> None:
        """Réinitialise la partie et redémarre le jeu."""
        if isinstance(self.view, EndgameView):
            self.view.stop()
            game_view = self.view.game_view
            new_view = Puissance4View(*game_view.players, scores=game_view.scores)
            new_view.message = game_view.message
            await interaction.response.edit_message(embed=new_view.get_embed(), view=new_view)


class ArreterButton(discord.ui.Button):
    """Bouton permettant d'arrêter complètement la partie."""
    def __init__(self):
        super().__init__(label="🛑 Arrêter", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction) -> None:
        """Arrête la partie et désactive les boutons."""
        if isinstance(self.view, EndgameView):
            self.view.stop()
            disable_all_buttons(self.view)
            await interaction.response.edit_message(view=self.view)
            await interaction.followup.send(f"🛑 {interaction.user.mention} a arrêté le jeu.")

# =========================================
# Confirmation View
# =========================================

class ConfirmationView(discord.ui.View):
    """Vue pour gérer l'acceptation ou le refus d'une invitation du jeu."""

    def __init__(self, player1: discord.Member, player2: discord.Member, timeout: int = 120):
        super().__init__(timeout=timeout)
        self.player1, self.player2 = player1, player2
        self.confirmed: Optional[bool] = None
        self.message: Optional[discord.Message] = None

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        """Vérifie que seul l'adversaire invité peut répondre."""
        if interaction.user != self.player2:
            await interaction.response.send_message(
                "❌ Seul l'adversaire invité peut cliquer.", 
                ephemeral=True
            )
            return False
        return True

    async def _handle_response(self, interaction: discord.Interaction) -> None:
        """Gère la réponse (oui/non) à l'invitation."""
        await interaction.response.defer()
        await self.finalize()

    async def finalize(self) -> None:
        """Finalise la vue selon la réponse donnée ou l'expiration."""
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

    def _get_rejection_embed(self) -> discord.Embed:
        """Construit un embed pour le refus ou l'expiration."""
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
        """Appelé si l'adversaire ne répond pas dans le temps imparti."""
        await self.finalize()

    @discord.ui.button(label="✅ Confirmer", style=discord.ButtonStyle.success)
    async def confirm(self, interaction: discord.Interaction, _) -> None:
        """Gére la confirmation de l'invitation"""
        self.confirmed = True
        await self._handle_response(interaction)

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.danger)
    async def cancel(self, interaction: discord.Interaction, _) -> None:
        """Gére le refus de l'invitation"""
        self.confirmed = False
        await self._handle_response(interaction)


# =========================================
# Puissance 4
# =========================================

class Puissance4(commands.Cog):
    """Extension (Cog) contenant la commande pour lancer une partie de Puissance 4."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @discord.app_commands.command(name="puissance4", description="Lance une partie de Puissance 4.")
    @discord.app_commands.describe(adversaire="L'utilisateur que vous souhaitez affronter.")
    async def p4(self, interaction: discord.Interaction, adversaire: discord.Member) -> None:
        """Commande principale pour inviter un adversaire et démarrer une partie."""
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
    """Ajoute le cog Puissance 4 au bot."""
    await bot.add_cog(Puissance4(bot))