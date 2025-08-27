import discord
from discord import app_commands, ui
from discord.ext import commands
from discord.ui import UserSelect

# -------------------- Sélecteurs --------------------

class MyMemberSelect(ui.ActionRow):
    def __init__(self):
        super().__init__()
        self.select: UserSelect = UserSelect(
            placeholder="Choisis un membre...",
            min_values=1,
            max_values=1
        )
        self.select.callback = self.select_callback
        self.add_item(self.select)

    async def select_callback(self, interaction: discord.Interaction):
        users: list[discord.Member | discord.User] = self.select.values
        selected_users = [f"Name: {user.name}, ID: {user.id}" for user in users]
        await interaction.response.send_message(
            f"{interaction.user.mention} a sélectionné :\n" + "\n".join(selected_users),
            ephemeral=True
        )

class MySelect(ui.ActionRow):
    @ui.select(
        placeholder="Choisis une option...",
        options=[
            discord.SelectOption(label="Option 1", value="1"),
            discord.SelectOption(label="Option 2", value="2"),
            discord.SelectOption(label="Option 3", value="3")
        ]
    )
    async def select_callback(self, interaction: discord.Interaction, select: ui.Select):
        await interaction.response.send_message(f"Tu as choisi {select.values[0]} !", ephemeral=True)

# -------------------- Boutons --------------------

class MyButtons(ui.ActionRow):
    @ui.button(label="Premier", style=discord.ButtonStyle.primary)
    async def first_button(self, interaction: discord.Interaction, _):
        await interaction.response.send_message("Tu as cliqué sur le premier bouton !", ephemeral=True)

    @ui.button(label="Deuxième", style=discord.ButtonStyle.success)
    async def second_button(self, interaction: discord.Interaction, _):
        await interaction.response.send_message("Tu as cliqué sur le deuxième bouton !", ephemeral=True)

# -------------------- Containers --------------------

class ContainerButtons(ui.Container):
    separator = ui.Separator(spacing=discord.SeparatorSpacing.large)
    text = ui.TextDisplay("Ceci est deux boutons !")
    buttons = MyButtons()

class ContainerMenu(ui.Container):
    separator = ui.Separator(spacing=discord.SeparatorSpacing.large)
    text = ui.TextDisplay("Ceci est un menu !")
    menu = MySelect()

class ContainerMember(ui.Container):
    separator = ui.Separator(spacing=discord.SeparatorSpacing.large)
    text = ui.TextDisplay("Ceci est un menu de membres !")
    member_menu = MyMemberSelect()

class ContainerGallery(ui.Container):
    separator = ui.Separator(spacing=discord.SeparatorSpacing.large)
    text = ui.TextDisplay("Voici une galerie média !")

    def __init__(self):
        super().__init__()
        gallery = discord.ui.MediaGallery(
            discord.MediaGalleryItem("https://i.imgur.com/a3y3tzj.jpeg"),
            discord.MediaGalleryItem("https://i.imgur.com/jni6AF6.jpeg")
        )
        self.add_item(gallery)

# -------------------- Vue principale --------------------

class MyView(ui.LayoutView):
    def __init__(self):
        super().__init__()
        self.add_item(ContainerButtons())
        self.add_item(ContainerMenu())
        self.add_item(ContainerMember())
        self.add_item(ContainerGallery())

# -------------------- Cog --------------------

class TestCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="components_v2", description="Test d'une layout avancée")
    async def testcontainer(self, interaction: discord.Interaction):
        view = MyView()
        await interaction.response.send_message(view=view)

# -------------------- Setup --------------------

async def setup(bot):
    await bot.add_cog(TestCog(bot))