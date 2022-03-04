import discord
from discord import Embed
from discord.ext import commands
from discord.utils import get

token = "dontyouthinkyouresocleverhuh"
server_id = 945500259868631100
server_name = "2022-ENEL220"
prefix = '!*'

# verification
verification_channel_id = 945500259868631100
welcome_role_id = 945500259868631100

# roles
roles_channel_id = verification_channel_id
roles = {
    945634624678289418: ("Intermediate", ""),
    945634698640625675: ("First Pro", ""),
    945634788130304051: ("Second Pro", ""),
    945634852630323250: ("Third Pro", ""),
    945634952366678077: ("Graduate", ""),
    945635135989096468: ("Teaching Staff", "")
                }

verifiable_roles = {}
mod_ping_channel_id = 928040388625858600

# continents
continents_channel_id = verification_channel_id
continents = {
    945634355101990965: "Electrical Engineering",
    945634440552546334: "Computer Engineering",
}

# mod_logging
logging_channel_id = 931728159840272434

# globals
COLOUR = discord.Color.from_rgb(65, 102, 145)
MAX_ITEMS_IN_EMBED = int(len(brands) / 2)


class RoleSelect(discord.ui.Select):
    # subclass of 'select', allowing for role manipulation
    def __init__(self, bot, roles, verifiable_roles, mod_ping_channel, server, server_id,
                 welcome_role, placeholder, logging_channel):
        self.logging_channel = logging_channel
        self.bot = bot
        self.user_roles = roles
        self.verifiable_user_roles = verifiable_roles
        self.verify_notification_target = mod_ping_channel
        self.server = server
        self.server_id = server_id
        self.welcome_role = welcome_role
        super(RoleSelect, self).__init__(placeholder=placeholder)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role = int(interaction.data['values'][0])
        guild = interaction.guild
        welcome_role_item = guild.get_role(self.welcome_role)
        await interaction.response.defer()
        guild_roles = await guild.fetch_roles()

        role_item = list(guild_roles)[[role.id for role in guild_roles].index(role)]

        role_name = role_item.name

        if role not in user.roles:
            if welcome_role_item in user.roles or len(set(user.roles).intersection(
                    set(guild.get_role(role_id) for role_id in
                        list(self.user_roles.keys()) +
                        list(self.verifiable_user_roles.keys())))) > 0:
                if role in self.verifiable_user_roles.keys():
                    # message role_moderator
                    mod_notification_channel = guild.get_channel(self.verify_notification_target)

                    await mod_notification_channel.send(
                        embed=Embed(
                            title=f"User '{user.name}' in {self.server} has requested the role "
                                  f"'{role_name}' which requires moderator verification.",
                            description='',
                            colour=COLOUR))

                    await interaction.followup.send(content=None,
                                                    embed=Embed(
                                                        title=f'Role Chosen: {role_name}',
                                                        description='A moderator will '
                                                                    'review your '
                                                                    'application and '
                                                                    'respond soon.',
                                                        colour=COLOUR),
                                                    ephemeral=True)

                elif role in self.user_roles.keys():
                    roles_managed = set()
                    for key in self.verifiable_user_roles.keys():
                        roles_managed.add(get(guild.roles, id=key))

                    for key in self.user_roles.keys():
                        roles_managed.add(get(guild.roles, id=key))

                    for role in roles_managed:
                        await user.remove_roles(role)

                    # grant the new role role_item
                    await user.add_roles(role_item)

                    await interaction.followup.send(content=None,
                                                    embed=Embed(
                                                        title=f'Role Chosen: {role_name}',
                                                        description='The role has been '
                                                                    'granted.',
                                                        colour=COLOUR),
                                                    ephemeral=True)
                    
            else:
                await interaction.followup.send(content=None,
                                                embed=Embed(
                                                    title="Verification Error",
                                                    description="You are not yet verified. "
                                                                "Please do so first.",
                                                    colour=COLOUR),
                                                ephemeral=True)

                
class ContinentSelect(discord.ui.Select):
    def __init__(self, bot, brand_roles, server, server_id, welcome_role, placeholder,
                 logging_channel):
        self.logging_channel = logging_channel
        self.bot = bot
        self.roles = brand_roles
        self.server = server
        self.server_id = server_id
        self.welcome_role = welcome_role
        super(ContinentSelect, self).__init__(placeholder=placeholder)

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        role_ids_chosen = interaction.data['values']
        await interaction.response.defer()

        roles_managed = set()
        for key in self.roles.keys():
            guild = await self.bot.fetch_guild(server_id)
            role = get(guild.roles, id=key)
            roles_managed.add(role)
        for role in set(roles_managed) & set(user.roles):
            await user.remove_roles(role)

        roles_to_add = set()
        for key in role_ids_chosen:
            guild = await self.bot.fetch_guild(server_id)
            role = get(guild.roles, id=int(key))
            roles_to_add.add(role)
        await interaction.followup.send(content=None,
                                        embed=Embed(
                                            title='Continent Roles set!',
                                            description='** **',
                                            colour=COLOUR),
                                        ephemeral=True)
        for role in roles_to_add:
            await user.add_roles(role)


def role_select(bot, user_roles, verifiable_user_roles, mod_channel, server_name, server_id,
                welcome_role_id, logging_channel):
    embed_description_string = "Use the drop-down to select a role, " \
                               "as appropriate."

    embed = discord.Embed(title='Set Your Role',
                          description=embed_description_string,
                          color=COLOUR
                          )
    embed.set_footer(text=("\u3000" * 300))

    for item in verifiable_user_roles.keys():
        embed.add_field(name=verifiable_user_roles[item][0],
                        value=' - ' + verifiable_user_roles[item][1] +
                              '\n- **This role requires verification by a moderator.**',
                        inline=False)

    for item in user_roles.keys():
        embed.add_field(name=user_roles[item][0],
                        value=' - ' + user_roles[item][1],
                        inline=False)

    role_select = RoleSelect(bot=bot, roles=user_roles, verifiable_roles=verifiable_user_roles,
                             mod_ping_channel=mod_channel,
                             server=server_name, server_id=server_id,
                             welcome_role=welcome_role_id,
                             placeholder='Pick a Role!',
                             logging_channel=logging_channel
                             )

    for item in verifiable_user_roles.keys():
        role_select.add_option(label=verifiable_user_roles[item][0],
                               value=item,
                               description='requires moderator approval.'
                               )

    for item in user_roles.keys():
        role_select.add_option(label=user_roles[item][0],
                               value=item,
                               description=''
                               )

    return discord.ui.View(role_select, timeout=None), embed


def continent_select(bot, continent_roles, server_name, server_id, logging_channel):
    embed_description_string = "Choose a degree!"

    embeds = []
    view = discord.ui.View(timeout=None)
    embed = discord.Embed(title='Degrees',
                          description=embed_description_string,
                          color=COLOUR
                          )

    embed.set_footer(text=("\u3000" * 300))
    for i in range(0, len(continent_roles), 2):
        embed.add_field(name=f"**{continent_roles[list(continent_roles.keys())[i]]}**",
                        value=f"**{continent_roles[list(continent_roles.keys())[i + 1]]}**",
                        inline=True)
    for i in range(0, len(continent_roles), MAX_ITEMS_IN_EMBED):
        continent_roles_slice = {}
        for key in list(continent_roles.keys())[i:i + MAX_ITEMS_IN_EMBED]:
            continent_roles_slice[key] = continent_roles[key]
        continent_select_menu = ContinentSelect(bot=bot,
                                                brand_roles=continent_roles_slice,
                                                server=server_name,
                                                server_id=server_id,
                                                welcome_role=welcome_role_id,
                                                placeholder="Choose from the available degrees!",
                                                logging_channel=logging_channel)

        for item in continent_roles_slice.keys():
            continent_select_menu.add_option(label=continent_roles_slice[item],
                                             value=item,
                                             description='')
        view.add_item(continent_select_menu)

    embeds.append(embed)

    return view, embeds


robot = commands.Bot(command_prefix=prefix,
                     case_insensitive=True)


@robot.event
async def on_ready():
    brands_channel = robot.get_channel(int(brands_channel_id))
    async for message in brands_channel.history(limit=200):
        if message.author == robot.user:
            await message.delete()

    continents_channel = robot.get_channel(int(continents_channel_id))
    async for message in continents_channel.history(limit=200):
        if message.author == robot.user:
            await message.delete()

    logging_channel = 0

    experience_roles_view, experience_roles_embed = role_select(bot=robot,
                                                                user_roles=roles,
                                                                verifiable_user_roles=
                                                                verifiable_roles,
                                                                mod_channel=mod_ping_channel_id,
                                                                server_name=server_name,
                                                                server_id=server_id,
                                                                welcome_role_id=welcome_role_id,
                                                                logging_channel=logging_channel
                                                                )
    
    continents_roles_view, continents_roles_embed = continent_select(bot=robot,
                                                                     continent_roles=continents,
                                                                     server_name=server_name,
                                                                     server_id=server_id,
                                                                     logging_channel=logging_channel
                                                                     )
    
    await roles_channel.send(embed=experience_roles_embed, view=experience_roles_view)
    await continents_channel.send(embeds=continents_roles_embed, view=continents_roles_view)


robot.run(token)
