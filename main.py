import discord
from config import TOKEN
from discord import app_commands
from discord.ext import commands
from pymongo.collection import ReturnDocument
from dbClass import UserDbSetup, GetMainUser, Team, ServerDBSetup, addMemberTeamPanel, buildEmbed, deleteTeamConfirmation, createTeamView
import datetime
import locale


bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())


class Bot(commands.Bot):

    def __init__(self):

        intents = discord.Intents.all()
        intents.message_content = True

        super().__init__(command_prefix=commands.when_mentioned_or('+'), intents=intents)

    async def setup_hook(self) -> None:
        self.add_view(addMemberTeamPanel())
        self.add_view(createTeamView())

    async def on_ready(self):

        # dbbot.botfiles.update_one({"botID":bot.user.id},{"$set":{"botname":bot.user.name}}, upsert=True)

        print("--------------------------------------------")
        print(f"{bot.user.name} est prêt à être utilisé!")
        print("--------------------------------------------")
        
        try:
            #SYNCRHONISATION DES COMMANDES SLASH / CONTEXT MENU
            # await syncGuilds(bot)
            synced= await bot.tree.sync()

            print(f"Synchronisé {len(synced)} commande(s)")
            print("--------------------------------------------")

        except Exception as e:
            print(e)

bot = Bot()



@bot.event
async def on_guild_join(guild:discord.Guild): #INITIALISATION DE LA DATABASE DU SERVEUR REJOINT 
    guildInstance = ServerDBSetup(server=guild)
    guildInstance.resolveDatabase()
    


@bot.event
async def on_member_join(member:discord.Member):
    userSetup = UserDbSetup(member)
    userSetup.setDefaultDB()

    
    
    


@bot.event
async def on_member_remove(member: discord.Member):

    userSetup = UserDbSetup(member)
    userSetup.Update(field="isInServer", content=False)


@bot.event
async def on_message(message:discord.Message): #EVENEMENT POUR CATCH TOUS LES MESSAGES
    # print(message.content)
    return


@bot.event
async def on_voice_state_update(member:discord.Member, before, after):
    
    guild:discord.Guild= member.guild
    channel = before.channel if before.channel is not None else after.channel
    
    if channel.id != 1213130829476143134:
        return
    
    if member.voice.channel.id == 1213130829476143134:
        salonVocal = await guild.create_voice_channel(name=f'Salon de {member.global_name}', user_limit=5, category= guild.get_channel(1020311168167972944))
        await member.move_to(salonVocal)
            
        if before.channel is None and after.channel is not None:
            print(f'{member} a rejoint un salon vocal.')
            
        if before.channel is not None and after.channel is None:
            print(f'{member} a quitté un salon vocal.')



"""@bot.tree.command(name="setup", description="Setup la configuration du serveur")
@app_commands.checks.has_permissions(administrator=True)
async def setupServer(interaction: discord.Interaction, channelBienvenue: discord.TextChannel, roleBienvenue:discord.Role, channelGeneral: discord.TextChannel):
"""


@bot.tree.command(name="setrank", description="Met à jour ton rank Valorant")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(rank =[
    discord.app_commands.Choice(name="Unranked", value="unranked"),
    discord.app_commands.Choice(name="Iron", value="iron"),
    discord.app_commands.Choice(name="Bronze", value="bronze"),
    discord.app_commands.Choice(name="Silver", value="silver"),
    discord.app_commands.Choice(name="Gold", value="gold"),
    discord.app_commands.Choice(name="Platinium", value="platinium"),
    discord.app_commands.Choice(name="Diamond", value="diamond"),
    discord.app_commands.Choice(name="Ascendant", value="ascendant"),
    discord.app_commands.Choice(name="Immortal", value="immortal"),
    discord.app_commands.Choice(name="Radiant", value="radiant")
])

@app_commands.choices(division =[
    discord.app_commands.Choice(name="1", value=1),
    discord.app_commands.Choice(name="2", value=2),
    discord.app_commands.Choice(name="3", value=3)
])
async def setRank(interaction: discord.Interaction, rank: discord.app_commands.Choice[str], division: discord.app_commands.Choice[int] = None):

    

    user = interaction.user
    choixRank = rank.value
    choixDivision = 0
    
    if division is not None:
        choixDivision = division.value
    
    if choixRank == "radiant" and choixDivision == 1 or 2 or 3 or None:
        await interaction.response.send_message(f"Ton rank a bien été mis à jour, tu es `radiant`", ephemeral=True)
        userDB = UserDbSetup(user=user)
        userDB.Update(field="rank", content=(choixRank,0))
        return
    
    if choixDivision == None: 
        choixDivision = 0
    
    userDB = UserDbSetup(user=user)
    userDB.Update(field="rank", content=(choixRank,choixDivision))
    await interaction.response.send_message(f"Ton rank a bien été mis a jour, tu es `{choixRank} {choixDivision}`", ephemeral=True)
    return


@bot.tree.command(name="findmate", description="Trouve un mate à travers les joueurs libres du serveur")
@app_commands.guild_only()
async def findmate(interaction: discord.Interaction):

    userDB = UserDbSetup(user=interaction.user)
    embed = buildEmbed(title=f"Résultat de ta recherche ({userDB.getRank()})", content=userDB.findMate(guild=interaction.guild),guild = interaction.guild)
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="rank", description="Renvoie le rank d'un utilisateur")
@app_commands.guild_only()
async def rank(interaction: discord.Interaction, cible:discord.User= None):

    utilisateur = interaction.user
    
    if cible != None:
        utilisateur = cible

    userClass = UserDbSetup(user=utilisateur)
    await interaction.response.send_message(userClass.getRank(), ephemeral=True)


@bot.tree.command(name="profile", description="Renvoie le profil d'un utilisateur")
@app_commands.guild_only()
async def profile(interaction: discord.Interaction, user:discord.User= None):

    utilisateur = interaction.user
    cible = False

    if user != None:
        utilisateur= user
        cible = True

    userClass = UserDbSetup(user=utilisateur)
    await interaction.response.send_message(userClass.getProfile(cible= cible), ephemeral=True)



@bot.tree.command(name="config", description="Config le serveur")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def config(interaction:discord.Interaction, teampanelchannel: discord.TextChannel, gamevccategorie:discord.CategoryChannel = None):

    guild= interaction.guild
    serverInstance = ServerDBSetup(server=guild)
    if gamevccategorie:
        serverInstance.updateServerDBList(listName="gamesVcCategories",elt=gamevccategorie.id, action="$addToSet") #$addToSet permet d'ajouter seulement si l'elt n'est pas dans la liste
    
    await teampanelchannel.send(view=addMemberTeamPanel())
    await interaction.response.send_message("les données ont bien été prises en comptes.", ephemeral=True)



@bot.tree.command(name="setownerchannel", description="Définit le salon des notifications des owners des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setownerchannel(interaction: discord.Interaction, teamownerrole: discord.Role, teamownercategory: discord.CategoryChannel):

    guild = interaction.guild
    teamChannel = await interaction.guild.create_text_channel(name='👑・Team owners', category=teamownercategory)

    await teamChannel.set_permissions(teamownerrole,read_messages=True,send_messages=False, read_message_history =True)
    await teamChannel.set_permissions(guild.default_role, view_channel=False, read_messages=False, connect=False, send_messages=False)

    serverInstance = ServerDBSetup(server=interaction.guild)
    serverInstance.Update("salonTeamOwner", teamChannel.id)

    await interaction.response.send_message(f"Le salon `{teamChannel.name}` a bien été défini comme salon pour envoyer les notifications aux owners.")



@bot.tree.command(name="setteamcategory", description="Définit le salon des vocs des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setteamcategory(interaction: discord.Interaction, teamcategory: discord.CategoryChannel):

    guild = interaction.guild
    serverInstance = ServerDBSetup(server=guild)
    serverInstance.Update("teamCategory", teamcategory.id)

    await interaction.response.send_message(f"La catégorie `{teamcategory.name}` a bien été défini comme salon pour accueilir les vocs des teams.")

@bot.tree.command(name="setnotifchannel", description="Définit le salon des notifications des teams")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setownerchannel(interaction: discord.Interaction, notifchannel : discord.TextChannel):

    serverInstance = ServerDBSetup(server=interaction.guild)
    serverInstance.Update("notifChannel", notifchannel.id)

    await interaction.response.send_message(f"Le salon `{notifchannel.name}` a bien été défini comme salon pour envoyer les notifications aux membres des teams!", ephemeral=True)


@bot.tree.command(name="ping", description="Renvoie la latence du bot")
async def ping(interaction:discord.Interaction):
    await interaction.response.send_message(f"Pong! Latence: {bot.latency*1000:.2f}ms")


@bot.tree.command(name="help", description="Commande d'aide du bot")
async def help(interaction:discord.Interaction):

    embed = discord.Embed(title="Commandes du bot")
    listeCommands = bot.tree.get_commands()

    for command in listeCommands:
        commandName = command.name
        print(command.checks)
        if "has_permissions" in str(command.checks):
            commandName += " - Administrateur"

        embed.add_field(name=commandName, value=command.description, inline=False)

    embed.set_footer(text=interaction.guild.name, icon_url=interaction.guild.icon)
    await interaction.response.send_message(embed=embed)



@bot.tree.command(name="createteam", description="Crée ta propre team!")
@app_commands.guild_only()
async def createteam(interaction: discord.Interaction, teamname:str, teamtag:str):

    teamInstance = Team(user=interaction.user ,teamName=teamname,teamTag=teamtag, server=interaction.guild)
    userInstance = UserDbSetup(user=interaction.user)
    await interaction.response.send_message(await teamInstance.CreateTeam())


@bot.tree.command(name="setdisponible", description="Définis ta disponibilité")
@app_commands.guild_only()
async def setdispo(interaction: discord.Interaction):
    
    userInstance = UserDbSetup(user=interaction.user)
    await interaction.response.send_message(userInstance.SetDisponible(), ephemeral=True)


@bot.tree.command(name="setmain", description="Définis ton perso préféré!")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
@app_commands.choices(main =[
    discord.app_commands.Choice(name="Astra", value="astra"),
    discord.app_commands.Choice(name="Breach", value="breach"),
    discord.app_commands.Choice(name="Brimstone", value="brimstone"),
    discord.app_commands.Choice(name="Chamber", value="chamber"),
    discord.app_commands.Choice(name="Cypher", value="cypher"),
    discord.app_commands.Choice(name="Fade", value="fade"),
    discord.app_commands.Choice(name="Gekko", value="gekko"),
    discord.app_commands.Choice(name="Harbor", value="harbor"),
    discord.app_commands.Choice(name="Iso", value="iso"),
    discord.app_commands.Choice(name="Jett", value="jett"),
    discord.app_commands.Choice(name="KAYO", value="kayo"),
    discord.app_commands.Choice(name="Killjoy", value="killjoy"),
    discord.app_commands.Choice(name="Neon", value="Neon"),
    discord.app_commands.Choice(name="Omen", value="omen"),
    discord.app_commands.Choice(name="Pheonix", value="pheonix"),
    discord.app_commands.Choice(name="Raze", value="raze"),
    discord.app_commands.Choice(name="Reyna", value="reyna"),
    discord.app_commands.Choice(name="Sage", value="sage"),
    discord.app_commands.Choice(name="Skye", value="skye"),
    discord.app_commands.Choice(name="Sova", value="sova"),
    discord.app_commands.Choice(name="Viper", value="viper"),
    discord.app_commands.Choice(name="Yoru", value="yoru")
])
async def setmain(interaction: discord.Interaction, main: discord.app_commands.Choice[str]):

    userInstance = UserDbSetup(user=interaction.user)
    userInstance.Update("main", main.value)
    await interaction.response.send_message(f"Ton main est maintenant `{main.name}`!", ephemeral=True)




@bot.tree.command(name="resolveserverdb", description="Résout les pbs de la base de donnée du serveur")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def resolvedb(interaction:discord.Interaction):

    serverClass = ServerDBSetup(server=interaction.guild)
    result = serverClass.resolveDatabase()
    await interaction.response.send_message(f"La db de `{interaction.guild.name}` a bien été résolue.", ephemeral=True)



@bot.tree.command(name="resolvememberdb", description="Résout les pbs de la base de donnée d'un utilisateur")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def resolvedb(interaction:discord.Interaction, cible: discord.Member = None):

    utilisateur = GetMainUser(interaction.user, cibleUser=cible)
    userClass = UserDbSetup(user=utilisateur)
    result = userClass.resolveDatabase()
    await interaction.response.send_message(f"La db de `{utilisateur.mention}` a bien été résolue.", ephemeral=True)
    



@bot.tree.command(name="teamlist", description="Affiche toutes les teams du serveur")
@app_commands.guild_only()
async def teamlist(interaction: discord.Interaction):

    guild = interaction.guild
    teamInstance = Team(user=None, teamTag=None, server=interaction.guild)
    teamListEmbed = discord.Embed(title=f"Liste des teams", description= teamInstance.TeamList())
    teamListEmbed.set_footer(text=guild.name, icon_url=guild.icon)
    await interaction.response.send_message(embed= teamListEmbed)



@bot.tree.command(name="myteam", description="Affiche les informations de ta team")
@app_commands.guild_only()
async def myteam(interaction: discord.Interaction):

    userInstance = UserDbSetup(user=interaction.user)
    team = userInstance.MyTeam(server=interaction.guild)
    responseEmbed = discord.Embed(title=f"{team[2].capitalize()} - {team[0]}", description=team[1], timestamp=datetime.datetime.now())
    responseEmbed.set_footer(icon_url=interaction.guild.icon, text=interaction.guild.name)

    await interaction.response.send_message(embed=responseEmbed, ephemeral=True)


@bot.tree.command(name="mate", description="Crée une invite dans ton salon vocal")
@app_commands.guild_only()
async def mate(interaction: discord.Interaction, message:str = None):

    user = interaction.user

    if interaction.channel.category.id != 1020311165705916467:
        await interaction.response.send_message(f"Rends toi dans la catégorie 'Recherche Mate' pour utiliser cette commande!", ephemeral=True)
        return

    if user.voice is None:
        await interaction.response.send_message("Tu n'es pas dans un salon vocal!", ephemeral=True)
        return        
    
    if message is not None:
        await interaction.response.send_message(f"--> `{message}` - {user.voice.channel.jump_url}")
        return
    else:
        await interaction.response.send_message(f"--> **{user.voice.channel.jump_url}**",suppress_embeds=True)



@bot.tree.command(name="jointeam", description="Formule une demande pour rejoindre une team")
@app_commands.guild_only()
async def jointeam(interaction: discord.Interaction, teamtag:str):

    userInstance = UserDbSetup(user=interaction.user)
    teamInstance = Team(user=interaction.user, teamTag=teamtag.upper(), server=interaction.guild)

    msg= None
    teamOwnerID = 154

    if userInstance.isTeamOwner():
        msg = f"Tu es le propriétaire de {userInstance.getTeamTag()}. Pour rejoindre une team, il faut que tu quitte le serveur pour supprimer ton actuelle team..."

    elif userInstance.isInTeam():
        msg = f"Tu ne peux pas rejoindre d'autre team tant que tu es dans la team {userInstance.getTeamTag()}. Fais /leaveteam pour la quitter"

    elif not teamInstance.isValidTeamTag():
        msg = f"Désolé, la team {teamtag.upper()} n'existe pas"

    elif teamInstance.isFullTeam():
        msg = f"Cette team est déjà pleine (5/5)"

    else:
        teamName = teamInstance.getTeamName()
        teamOwnerID = await teamInstance.getTeamOwner()
        teamOwner = bot.get_user(teamOwnerID)
        team = teamName.capitalize()

        msg = f"La demande pour rejoindre la team {team} a bien été envoyée à son propriétaire."
        await teamInstance.invitationOwnerNewMember(guild=interaction.guild, teamOwner=teamOwner, teamTag=teamtag)

    await interaction.response.send_message(msg)




@bot.tree.command(name="leaveteam", description="Quitte ta team actuelle")
@app_commands.guild_only()
async def leaveteam(interaction: discord.Interaction):

    userInstance = UserDbSetup(user= interaction.user)
    if not userInstance.isInTeam():
        await interaction.response.send_message("Tu n'es pas dans une équipe!", ephemeral=True)
        return
    
    if userInstance.isTeamOwner():
        await interaction.response.send_message("Tu ne peux pas quitter une team que tu as créée!", ephemeral=True)
        return
    
    tag = userInstance.getTeamTag()

    teamInstance = Team(user=interaction.user, teamTag=tag, server=interaction.guild)
    
    await teamInstance.memberLeaveTeam()
    await interaction.response.send_message(f"Tu as bien quitté la team {tag}", ephemeral=True)



@bot.tree.command(name="deleteteam", description="Supprime la team si tu en es propriétaire")
@app_commands.guild_only()
async def deleteteam(interaction: discord.Interaction):

    userInstance =UserDbSetup(user=interaction.user)

    if userInstance.isTeamOwner():
        teamTag= userInstance.getTeamTag()
        await interaction.response.send_message(view=deleteTeamConfirmation(teamTag=teamTag, server=interaction.guild, teamOwner=interaction.user))

    else:
        await interaction.response.send_message("Tu n'es pas owner d'une quelconque team, tu ne peux donc pas en supprimer une!", ephemeral=True)



@bot.tree.command(name="setcreateteammodal", description="Envoie le modal de création de team")
@app_commands.guild_only()
@app_commands.checks.has_permissions(administrator=True)
async def setcreateteammodal(interaction:discord.Interaction, createteamchannel: discord.TextChannel):

    await createteamchannel.send(view=createTeamView())
    await interaction.response.send_message(f"Le salon {createteamchannel.name} a bien été défini comme salon de création de teams!", ephemeral=True)



bot.run(TOKEN)