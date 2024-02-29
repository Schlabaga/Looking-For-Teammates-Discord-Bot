from config import dbBot, dbServer, dbUser
import discord
import datetime as dt
from discord.ext import commands
from discord import ui

validEmoji = "✅"
nonValidEmoji = "❎" 

def buildEmbed(title:str, content:str, guild: discord.Guild,imageurl = None, thumbnailurl = None):

    embedResult = discord.Embed(title=title.capitalize(), description= content, timestamp=dt.datetime.now())
    embedResult.set_image(url=imageurl)
    embedResult.set_thumbnail(url=thumbnailurl)
    embedResult.set_footer(text=guild.name, icon_url=guild.icon)
    return embedResult

def IsConcernedUser(cibleUser:discord.Member, interactionUser:discord.Member):

    if cibleUser.id == interactionUser.id:
        return True
    
    return False


class DecisionTeamOwner(discord.ui.View):

    def __init__(self, teamTag, memberUser: discord.Member, ownerUser: discord.User, server: discord.Guild, NotifChannel):
        super().__init__(timeout=3600)
        self.teamTag = teamTag.upper()
        self.memberUser = memberUser
        self.ownerUser = ownerUser
        self.server = server
        self.NotifChannel = self.server.get_channel(NotifChannel)

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, emoji=validEmoji)
    async def on_accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if interaction.user != self.ownerUser:
            await interaction.response.send_message(f"Tu n'es pas concerné(e) par cette demande, désolé!", ephemeral=True)
            return

        teamInstance = Team(user=self.memberUser, teamTag=self.teamTag, server=self.server)

        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)
        guild = interaction.guild

        await teamInstance.memberJoinTeam()

        embed = discord.Embed(title="Bravo!", description=f"{self.memberUser.mention} devient membre de la team {self.teamTag}!", 
                              timestamp=dt.datetime.now())
        # embed.set_footer(text=guild.name, icon_url=guild.icon)
        

        messageChannel = await self.NotifChannel.send(content= self.memberUser.mention,embed=embed)
        message = await interaction.response.send_message(embed=embed)


    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, emoji=nonValidEmoji)
    async def on_deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.ownerUser:
            await interaction.response.send_message(f"Tu n'es pas concerné(e) par cette demande, désolé!", ephemeral=True)
            return

        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)

        guild = interaction.guild

        embed = discord.Embed(title="Oups, desolé... :/", description=f"{self.teamTag} refusé {interaction.user.mention} ta demande d'intégration... La prochaine fois sera la bonne!",
                              timestamp= dt.datetime.now())
        # embed.set_footer(icon_url=guild.icon, text=guild.name)

        await interaction.response.send_message(embed=embed)


class decisionTeamMember(discord.ui.View):

    def __init__(self, teamTag, memberUser: discord.Member, NotifChannel: discord.TextChannel):
        super().__init__(timeout=3600)
        self.teamTag = teamTag
        self.memberUser = memberUser
        self.server = memberUser.guild
        self.NotifChannel = self.server.get_channel(NotifChannel)

    @discord.ui.button(label="Accepter", style=discord.ButtonStyle.green, emoji=validEmoji)
    async def on_accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        if interaction.user != self.memberUser:
            await interaction.response.send_message("Tu n'es pas concerné(e) par cette invitation, désolé!", ephemeral=True)
            return

        teamInstance = Team(user=interaction.user, teamTag=self.teamTag, server=self.server)

        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)
        await teamInstance.memberJoinTeam()

        embed = discord.Embed(title="Bravo!", description=f"{interaction.user.mention} a accepté l'invitation de la team {self.teamTag} et en fait maintenant partie!", timestamp=dt.datetime.now())

        message = await interaction.response.send_message(f"Bravo, tu fais maintenant partie de la team {self.teamTag}!", ephemeral=True)
        messageNotif = await self.NotifChannel.send(embed=embed)



    @discord.ui.button(label="Refuser", style=discord.ButtonStyle.red, emoji=nonValidEmoji)
    async def boutonrefuser(self, interaction: discord.Interaction, button: discord.ui.Button):

        if interaction.user != self.memberUser:
            await interaction.response.send_message("Tu n'es pas concerné(e) par cette invitation, désolé!", ephemeral=True)
            return

        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)

        guild = interaction.guild

        embed = discord.Embed(title="Oups, desolé... :/", description=f"La demande d'intégration de la team {self.teamTag} a été refusée par {interaction.user.mention}!")
        embed.set_footer(icon_url=guild.icon, text=guild.name)
        
        await interaction.response.send_message(embed=embed)



class deleteTeamConfirmation(discord.ui.View):

    def __init__(self, teamTag, server: discord.Guild, teamOwner = discord.Member):
        super().__init__(timeout=3600)
        self.teamTag = teamTag
        self.server = server
        self.teamOwner = teamOwner


    @discord.ui.button(label="Oui, je suis sûr(e)!", style=discord.ButtonStyle.green, emoji=validEmoji)
    async def on_accept_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not IsConcernedUser(cibleUser=self.teamOwner, interactionUser=interaction.user):
            await interaction.response.send_message("Tu n'es pas concerné par cette interaction, désolé!", ephemeral=True)
            return
        
        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)
        guild = interaction.guild

        teamInstance = Team(user=interaction.user, teamTag=self.teamTag, server=self.server)

        await teamInstance.deleteTeam()

        embed = discord.Embed(title="La fin d'une aventure...", description=f"La team {self.teamTag} vient d'être supprimée :(", 
                              timestamp=dt.datetime.now())
        embed.set_footer(text=guild.name, icon_url=guild.icon)

        # notifs = await bot.get_channel()
        # messageChannel = await notifs.send(embed=embed)
        message = await interaction.response.send_message(embed=embed)



    @discord.ui.button(label="Tout compte fait... Non!", style=discord.ButtonStyle.red, emoji=nonValidEmoji)
    async def on_deny_button(self, interaction: discord.Interaction, button: discord.ui.Button):

        if not IsConcernedUser(cibleUser=self.teamOwner, interactionUser=interaction.user):

            await interaction.response.send_message("Tu n'es pas concerné par cette interaction, désolé!", ephemeral=True)
            return

        self.children[0].disabled = True
        self.children[1].disabled = True

        await interaction.message.edit(view=self)

        guild = interaction.guild

        embed = discord.Embed(title="Ouf! Quel soulagement!", description=f"Ta team ne sera pas supprimée!",
                              timestamp= dt.datetime.now())
        embed.set_footer(icon_url=guild.icon, text=guild.name)

        await interaction.response.send_message(embed=embed, ephemeral=True)


class addMemberTeamPanel(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.select(
        cls=discord.ui.UserSelect,
        max_values=1,
        custom_id="persistent_view:userSelect",
        placeholder='Qui veux-tu ajouter à ta team?',
    )

    async def user_select(self, interaction: discord.Interaction, cibleListe: discord.ui.UserSelect) -> None:

        ownerInstance = UserDbSetup(user = interaction.user)
        cibleInstance = UserDbSetup(user = cibleListe.values[0])
        serverInstance = ServerDBSetup(server=interaction.guild)

        if cibleListe.values[0].bot:
            await interaction.response.send_message("Cet utilisateur est un robot, il ne peut pas rejoindre de team!", ephemeral=True)
            return

        if not ownerInstance.isInTeam():
            await interaction.response.send_message("Tu n'es pas dans une team, tu peux en créer une en faisant </createteam:1090677079005212762>", ephemeral=True)
            return
        
        if not ownerInstance.isTeamOwner():
            await interaction.response.send_message("Tu n'es pas l'owner de ta team, tu peux malgré tout en créer une en faisant </createteam:1090677079005212762>", ephemeral=True)
            return        
        
        teamInstance = Team(user=interaction.user,teamTag= ownerInstance.getTeamTag(), server=interaction.guild)

        if teamInstance.isFullTeam():
            await interaction.response.send_message("Ta team a atteint sa capacité maximale (5 membres)!", ephemeral=True)
            return
        
        msg =await interaction.response.send_message(f"Hey {cibleListe.values[0].mention}, on t'a invité à rejoindre la team {ownerInstance.getTeamTag()}",
                                                      view=decisionTeamMember(teamTag=ownerInstance.getTeamTag(), memberUser=cibleListe.values[0], NotifChannel=await serverInstance.getNotifChannel()))



class createTeamModal(ui.Modal, title= "Crée ta team!"):

    def __init__(self):
        super().__init__(timeout=None)
        self.custom_id= "persistent_view:createteammodal"
        
    teamName = ui.TextInput(label='Nom de la team', style=discord.TextStyle.short, placeholder="Trouve un nom original", min_length=5, max_length= 15)
    teamTag = ui.TextInput(label='Tag de la team', style=discord.TextStyle.short, placeholder="Le tag de ta team", max_length=5, min_length=3)
    teamDescription = ui.TextInput(label='Présentation de la team', style=discord.TextStyle.short, placeholder="La description de ta team", max_length=150, min_length=30)

    async def on_submit(self, interaction: discord.Interaction):

        guild= interaction.guild
        utilisateur = interaction.user
        embedResponse=discord.Embed(title=f'Team de {utilisateur.name}')
        embedResponse.set_footer(text=guild.name,icon_url=guild.icon)
        embedResponse.add_field(name='Nom de ta team',value=self.teamName)
        embedResponse.add_field(name="Tag de la team",value=self.teamTag)
        # embedResponse.add_field(name="Description",value=self.description)
        # embedResponse.set_thumbnail(url=interaction.user.avatar)

        teamInstance = Team(user=interaction.user, teamTag=self.teamTag.value.upper(), teamName=self.teamName.value.lower(), server=interaction.guild)
        msg = await teamInstance.CreateTeam()

        await interaction.response.send_message(content=msg, ephemeral=True)



class createTeamView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cooldown = commands.CooldownMapping.from_cooldown(3,60, commands.BucketType.member)


    @discord.ui.button(label="Créer une team", style= discord.ButtonStyle.green, custom_id= "persistent_view:green",emoji= "🚀")
    async def boutoninscription(self, interaction: discord.Interaction, button: discord.ui.Button):

        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)

        else:
            await interaction.response.send_modal(createTeamModal())
        

    @discord.ui.button(label="Quitter ma team", style= discord.ButtonStyle.blurple, custom_id= "persistent_view:gray",emoji= "⚠️")
    async def boutonleave(self, interaction: discord.Interaction, button: discord.ui.Button):
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        view = None

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)

        else:
            utilisateur = interaction.user
            userInstance= UserDbSetup(user=utilisateur)
            teamInstance = Team(user=utilisateur, teamTag= userInstance.getTeamTag(), server=interaction.guild) 

            if not userInstance.isInTeam():
                msg= f"Tu n'es pas dans une team! Fais </jointeam:1090990838131200091> pour rejoindre une team!"
                

            elif userInstance.isTeamOwner():
                msg = f"Tu ne peux pas quitter ta propre team."
            
            else:
                msg = f"{await teamInstance.memberLeaveTeam()}"
            

            await interaction.response.send_message(msg, ephemeral=True)


    @discord.ui.button(label="Supprimer ma team", style= discord.ButtonStyle.gray, custom_id= "persistent_view:red",emoji= "🔐")
    async def boutonsupp(self, interaction: discord.Interaction, button: discord.ui.Button):
        
        utilisateur = interaction.user
        guild = interaction.guild
        bucket = self.cooldown.get_bucket(interaction.message)
        retry = bucket.update_rate_limit()
        view = None

        if retry:
            await interaction.response.send_message(f"Tu es en **cooldown**, rééssaye dans `{round(retry,1)} secondes`", ephemeral=True)

        else:

            userInstance= UserDbSetup(user=utilisateur)
            serverInstance = ServerDBSetup(server=guild)
            ownerChannel = guild.get_channel(serverInstance.getOwnerChannel())

            if not userInstance.isInTeam():
                msg = f"Tu n'es pas dans une team! Fais </jointeam:1090990838131200091> pour rejoindre une team!"
                
            if not userInstance.isTeamOwner():
                msg = f"Tu n'es pas l'owner de ta team, tu peux en créer une en faisant </createteam:1090677079005212762>"
            else:
                msg= f"Je t'invite à me suivre dans le salon <#{ownerChannel.id}>!"
                view = deleteTeamConfirmation(teamTag= userInstance.getTeamTag(), server=interaction.guild, teamOwner = utilisateur)
                await ownerChannel.send(f"{utilisateur.mention}, es-tu sûr de vouloir supprimer ta team?", view= view)

            try:
                await interaction.response.send_message(msg, ephemeral=True)
                

            except AttributeError:

                pass
            






UserDefaultDict=  {"rank":None, "main":None, "available":False, "team":None, "teamOwner":False, "isInServer":True, "pending":False, "profile": False}

bot = commands.Bot(command_prefix="+", intents= discord.Intents.all())


class Create5Stack(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)


    @discord.ui.select(
        cls=discord.ui.UserSelect,
        max_values=5,
        custom_id="persistent_view:userSelect",
        placeholder='Qui veux-tu ajouter à ta 5 stack?',
    )

    async def user_select(self, interaction: discord.Interaction, cibleListe: discord.ui.UserSelect) -> None:

        print(cibleListe.values)
        # for cible in cibleListe:
            
        #     dbServer.teams.update_one({'userID': self.ci}, {'$push': {'likeurs': likeurID}}, upsert = True)


def UserEditDefaultDict(field, value):

    variableDict = UserDefaultDict
    variableDict[field] = value
    return variableDict 


def buildDict(**kwargs):

    return kwargs


def GetMainUser(interactionUser, cibleUser):

    if cibleUser != None:
        return cibleUser

    return interactionUser


class UserDbSetup:

    def __init__(self, user:discord.User):

        self.user = user
        self.db = dbUser.user.find_one({"userID":self.user.id})

        if self.db == None:

            self.IfNoDBCreateOne()
            self.db = dbUser.user.find_one({"userID":self.user.id})



    def Update(self, field:str, content):
        dbUser.user.update_one({"userID":self.user.id}, {"$set":{field:content}}, upsert=True)
        


    def IfNoDBCreateOne(self):

        UserEditDefaultDict(field="userName", value=self.user.name)

        if self.db == None:
            self.db = dbUser.user.update_one({"userID":self.user.id}, {"$set":UserDefaultDict},upsert=True)

        dbUpdated = dbUser.user.find_one({"userID":self.user.id})
    
        return dbUpdated


    def IfFieldInDatabase(self,field):

        if field in self.db:
            
            if self.db[field] != None:

                return self.db[field]
                
        return "Donnée non renseignée"


    def CheckIfFieldExists(self, field):

        if field in self.db:
            return True
        else: 
            return False


    def getRank(self):

        if self.user.bot:
            return "Les bots ne jouent pas aux jeux vidéo!"
        
        db = self.IfNoDBCreateOne()

        rank = self.IfFieldInDatabase(field="rank")

        if isinstance(rank,list):

            return f"`{rank[0].capitalize()} {rank[1]}`"
        
        else:
            return "`Rank non renseigné`"


    def getProfile(self, cible):

        db = self.IfNoDBCreateOne()
        profileVerif = self.IfFieldInDatabase("profile")
        content = ""

        if profileVerif is not str:

            if self.CheckIfFieldExists(field="profile"):
                
                for info in db:
                    content = f"{content}\n・{info.capitalize()}: {db[info]}"

            else:

                return "Cet utilisateur n'a pas encore créé son profil!" 
                       
        else:

            return profileVerif


    def resolveDatabase(self):

        variableDict = UserEditDefaultDict(field="userName", value=self.user.name)

        if self.db: 
            for cle in UserDefaultDict:
                if cle in self.db:
                    pass
                else:

                    self.Update(field= cle , content=variableDict[cle])
        else:
            dbUser.user.update_one({"userID":self.user.id},{"$set":variableDict}, upsert=True)


    def setDefaultDB(self):
    
        variableDict = UserEditDefaultDict(field="userName", value=self.user.name)

        if not self.db:
            dbUser.user.update_one({"userID":self.user.id},{"$set":variableDict}, upsert=True)

        else:

            self.resolveDatabase()


    def SetDisponible(self):
        
        dispo = self.db["available"]
        dbUser.user.update_one({"userID":self.user.id},{"$set":{"available":not dispo}},upsert=True)
        resultat = ""

        if dispo == True:
            resultat = "non"

        return f"Tu es maintenant {resultat} disponible"
    

    def isTeamOwner(self):

        if self.CheckIfFieldExists("teamOwner"):

            return self.db["teamOwner"]

        return False


    def isInTeam(self):

        if self.CheckIfFieldExists("team"):
            team = self.db["team"]

            if team != None:
                return True            

        return False


    def hasSpecifiedRank(self):

        if "rank" in self.db:

            if self.db["rank"] != None:
                return True
        
        return False


    def getRankList(self):
        
        rank = self.IfFieldInDatabase(field="rank")

        if isinstance(rank,list):

            return rank
        
        else:
            return None


    def findMate(self, guild: discord.Guild):

        chaineMates = ""

        self.Update(field="available", content=True)

        rankList = self.getRankList()

        if not self.hasSpecifiedRank():
            return "Tu n'as pas spécifié ton rank, fais </setrank:1088904049799213056> pour le faire!"

        if rankList:
            listeDispos = dbUser.user.find({"available":True, "rank":{"$in":[rankList[0]]}})        

        
        for i in listeDispos:
            if i["userID"] != self.user.id:
                userID = i["userID"] 
                userReady = guild.get_member(userID)
                chaineMates = f"{chaineMates}\n・{userReady.mention}{self.getMain(i)}"

        if chaineMates == "":

            return "Aucun membre ne correspond à ta recherche, désolé!"

        return chaineMates
    

    def getMain(self, db):

        if "main" in db:

            if db["main"] != None:
                main = db["main"]
                return f" - {main}"

        return " "
    
    def getTeamTag(self):
        
        if self.IfFieldInDatabase(field="team"):

            return self.db["team"]
        
        return None
    


    def MyTeam(self, server: discord.Guild):

        if self.isInTeam():

            teamTag = self.getTeamTag()
            teamInstance = Team(user= self.user, teamTag=teamTag, server= server)
            return (teamTag,teamInstance.getTeamMembers())

        return ("Tu n'es pas dans une team!","Fais </jointeam:1090990838131200091> pour rejoindre une team!")


    def JoinTeam(self):

        if self.isInTeam():
            return "Tu es déjà dans une team! fais </leaveteam:1091367598102417538> pour la quitter!"
        
        else:
            teamInstance = Team(user=self.user, teamTag= self.getTeamTag())
            if not teamInstance.isFullTeam():
                return True 
            
            else:
                return False

    

ServerDefaultDict=  {"salonTeamOwner":None, "roleTeamOwner":None, "teamenabled":True, "teamCategory":None}


def ServerEditDefaultDict(field, value):

    variableDict = ServerDefaultDict
    variableDict[field] = value
    return variableDict 


class ServerDBSetup:

    def __init__(self, server: discord.Guild):

        self.server = server
        self.dbServeur= dbServer.server.find_one({"serverID":self.server.id})


    def Update(self, field:str, content):
        
        dbServer.server.update_one({"serverID":self.server.id}, {"$set":{field:content}}, upsert=True)

    def CheckIfFieldExists(self, field):

        if field in self.dbServeur:
            return True
        else: 
            return False


    def resolveDatabase(self):

        variableDict = ServerEditDefaultDict(field="serverName", value=self.server.name)

        if self.dbServeur: 

            for cle in ServerDefaultDict:

                if cle in self.dbServeur:
                    pass
                else:

                    self.Update(field= cle , content=variableDict[cle])
        else:

            dbServer.server.update_one({"serverID":self.server.id},{"$set":variableDict}, upsert=True)


        
    def isTeamEnabled(self):
        
        permission = self.CheckIfFieldExists(field="teamenabled")

        if permission == True:
            return True
        
        return False
    
    def isDisponible(self, rank:str, user):
        listeDispo = dbUser.user.find({"rank":rank, "available":True})

        # for Member in listeDispo:


    def getOwnerChannel(self):
        return self.dbServeur["salonTeamOwner"]
    
    
    def getOwnerRole(self):
        return self.dbServeur["roleTeamOwner"]


    async def getNotifChannel(self):
        return self.dbServeur["notifChannel"]
    
    def getTeamCategory(self):
        return self.dbServeur["teamCategory"]



TeamDefaultDict = {}

class Team:

    def __init__(self, user: discord.User, teamTag, server: discord.Guild = None, teamName = None):

        self.server = server
        self.user = user
        self.db = dbServer.teams.find_one({"teamTag":teamTag.upper()})
        self.teamName = teamName
        self.teamTag = teamTag.upper()


    def isFullTeam(self):

        nb = len(self.db["teamMembers"])
        if nb >= 5: #A CHANGER
            return True
        return False
        
    def IsTeamOpened(self):
        return self.db['opened']


    def ifAlreadyExists(self):
        if self.db:
            return True
        else:
            return False
        

    def CheckIfValidNameAndTag(self):

        if self.teamName.isalpha() and self.teamTag.isalpha() and len(self.teamTag) <= 5 and len(self.teamName)<= 15:
            return True
        
        return False

    def TeamList(self):

        teamChain = ""
        
        listeFiles = dbServer.teams.find({})

        if listeFiles == {}:

            return "Il n'y a aucune team à afficher!"

        for i in listeFiles:

            teamName = i["teamName"].capitalize()
            teamTag = i["teamTag"].upper()
            teamOwner = self.server.get_member(i["teamOwner"])
            teamCapacite = len(i["teamMembers"])
            teamChain = f"{teamChain}\n・`{teamName}` - {teamOwner.mention} - {teamTag} `({teamCapacite}/5)`"

        return teamChain


    def CreateTeamDB(self, teamDict):
        dbServer.teams.update_one({"teamTag":self.teamTag.upper()},{"$set":teamDict}, upsert=True)
        # dbServer.teams.update_one({"teamRole":self.teamTag.upper()},{"$set":teamDict}, upsert=True)
        dbUser.user.update_one({"userID":self.user.id},{"$set":{"team":self.teamTag.upper(),"teamOwner":True}}, upsert=True)
        
    def deleteTeamDB(self):
        dbServer.teams.delete_one({"teamTag":self.teamTag.upper()})
        dbUser.user.update_many({"team":self.teamTag.upper()}, {"$set": {"team": None, "teamOwner":False}})

    async def deleteTeam(self):

        for i in dbUser.user.find({"team":self.teamTag.upper()}):
            print(i)
            memberID = i["userID"]
            userNick = self.server.get_member(memberID)
            newNickName = userNick.name.replace(f'[{self.teamTag}]', "")
            try:
                await userNick.edit(nick=newNickName)
            except:
                pass

        roleBase  = await self.getTeamRole()
        channelBase = await self.getTeamChannel()
        teamRole = self.server.get_role(roleBase)
        teamChannel = self.server.get_channel(channelBase)

        await teamRole.delete()
        await teamChannel.delete()

        self.deleteTeamDB()

        return f"La team {self.teamTag} a bien été supprimée!"

    async def CreateTeam(self):

        userInstance = UserDbSetup(user=self.user)
        isInTeam = userInstance.isInTeam()

        if isInTeam == True:
            return f"Tu es déjà dans une team. Pour la quitter, fais </leaveteam:1091367598102417538>, ensuite, tu pourras rejoindre une autre team!"
        
        else:
            if self.ifAlreadyExists():
                return "Une autre team utilise déjà ce tag!"
            
            verifName = self.CheckIfValidNameAndTag()

            if verifName ==True:
                servInstance = ServerDBSetup(server=self.server)

                if servInstance.isTeamEnabled():

                    teamRole : discord.Role = await self.createAndAssignTeamRole()
                    teamChannel : discord.VoiceChannel = await self.createTeamChannel(teamRole=teamRole)

                    result = self.CreateTeamDB(teamDict={"teamName":self.teamName.lower(),"teamOwner":self.user.id, 
                                                         "teamMembers": [(self.user.name,self.user.id, dt.datetime.today())], "teamRole": teamRole.id, "teamChannel":teamChannel.id})
                    await self.addTeamTagNickname()
                    return f"La team {self.teamTag} a bien été créée!" 

                else:
                    return "La création de team est désactivée pour le moment, désolé!"

            else:
                return "1. Le nom et le tag de la team ne doivent contenir que des lettres (pas d'espace etc)\n2. La longueur du tag doit être inférieure à 5 caractères et celle du nom de la team doit être inférieure à 15 caractères"


    async def assignTeamRole(self):

        teamRoleID= self.getTeamRole()
        teamRole = self.server.get_role(teamRoleID)
        userId = self.user.id
        member:discord.Member = self.server.get_member(userId)
        await member.add_roles(teamRole)
        return teamRole
    

    async def createAndAssignTeamRole(self):

        teamRole = await self.server.create_role(name=f"🛡️・{self.teamName.capitalize()}")
        userId = self.user.id
        member:discord.Member = self.server.get_member(userId)
        await member.add_roles(teamRole)
        return teamRole
    
    async def createTeamChannel(self, teamRole):

        channel = await self.server.create_voice_channel(name=f"🍇{self.teamName.capitalize()}", user_limit=5)
        await channel.set_permissions(teamRole, connect = True, speak = True, stream = True)
        await channel.set_permissions(self.server.default_role, view_channel=True, read_messages=False, connect=False, send_messages=False)

        return channel

    def getTeamName(self):
        return self.db["teamName"]

    def getTeamMembers(self):

        listeMembres=  ""
        nb = 0

        for member in self.db["teamMembers"]:

            memberFound = self.server.get_member(member[1])
            userInstance = UserDbSetup(user = memberFound)
            nb+=1
            
            dateExacte = member[2]

            listeMembres = f"{listeMembres}\n{nb}. {memberFound.mention} - {userInstance.getRank()} - {dateExacte.date()}"
 
        return listeMembres
        
    async def memberJoinTeam(self):

        userInstance = UserDbSetup(user= self.user)
        userInstance.Update("team", self.teamTag)
        dbServer.teams.update_one({"teamTag":self.teamTag},{'$push': {'teamMembers':(self.user.name,self.user.id, dt.datetime.today())}}, upsert = True)
        await self.assignTeamRole()
        await self.addTeamTagNickname()
    
    async def sendNotifToServer(self,notif):
        
        serverInstance = ServerDBSetup(server=self.server)
        NotifChannelID =await serverInstance.getNotifChannel()
        notifChannel = self.server.get_channel(NotifChannelID)
        await notifChannel.send(notif)
        


    async def memberLeaveTeam(self):
        userInstance = UserDbSetup(user= self.user)
        userInstance.Update("team", None)
        await self.removeTeamTagNickname()
        await self.removeTeamRole()
        await self.sendNotifToServer(f"{self.user.mention} a quitté la team {self.teamTag} :(")
        dbServer.teams.update_one({"teamTag":self.teamTag},{'$pull': {'teamMembers':{"$in":[self.user.id]}}}, upsert = True)
        return f"{self.user.mention} tu as bien quitté la team {self.teamTag}"



    async def addTeamTagNickname(self):
        member  = self.server.get_member(self.user.id)
        oldNickName = member.name
        await member.edit(nick=f"[{self.teamTag}] {oldNickName}")

    async def removeTeamTagNickname(self):
        userNick = self.server.get_member(self.user.id)
        try:
            await userNick.edit(nick=None)
        except:
            pass
        
    async def removeTeamRole(self):
        roleId = self.getTeamRole()
        role = self.server.get_role(roleId)
        member = self.server.get_member(self.user.id)
    
        await member.remove_roles(role)
        return

    def isValidTeamTag(self):

        if dbServer.teams.find_one({"teamTag":self.teamTag}):
            return True
        
        return False

    async def getTeamOwner(self):
        result = self.db["teamOwner"]
        print(result)
        return result

    
    async def AcceptMemberTeam(self,  interaction: discord.Interaction, ownerChannel: discord.TextChannel):
        await interaction.response.send_message(f"Veux-tu accepter l'utilisateur {self.user} dans la team?", view=addMemberTeamPanel())
    



    async def invitationOwnerNewMember(self, guild:discord.Guild, teamOwner: discord.User, teamTag:str):

        serverInstance = ServerDBSetup(server=guild)

        try:
            await teamOwner.send(embed=buildEmbed(title="Demande d'intégration", content=f"{self.user.mention} veut rejoindre ta team. Quelle est ta décision?", guild = guild), 
                                 view=DecisionTeamOwner(teamTag=teamTag,ownerUser= teamOwner, memberUser=self.user, server=self.server, NotifChannel=await serverInstance.getNotifChannel()))

        except discord.Forbidden:
            teamOwnerChannel = guild.get_channel(serverInstance.getOwnerChannel())
            await teamOwnerChannel.send(content=teamOwner.mention,embed=buildEmbed(title="Demande d'intégration", content=f"{self.user.mention} veut rejoindre ta team. Quelle est ta décision?", guild = guild), 
                                        view=DecisionTeamOwner(memberUser=self.user,ownerUser= teamOwner, teamTag=self.teamTag, server=self.server, NotifChannel=serverInstance.getNotifChannel))


    def getTeamRole(self):
        return self.db["teamRole"]
    
    async def getTeamChannel(self):
        return self.db["teamChannel"]
    

    def checkIfMemberInVc(self, user: discord.Member, vc:discord.VoiceChannel):

        if user in vc.members:
            return True
        
        return False

    async def SendNotificationVoc(self):

        serverInstance = ServerDBSetup(server=self.server)
        categorieTeamVoc:discord.CategoryChannel = serverInstance.getTeamCategory()
        voice_channels = [channel for channel in categorieTeamVoc.channels if isinstance(channel, discord.VoiceChannel)]
        userAbsents = []
        usersPresents = []

        for channel in voice_channels:
            membreConnectesCount= len(channel.members)

            if membreConnectesCount >=2 and membreConnectesCount>6:

                db = dbServer.teams.find_one({"teamChannel":channel.id})
                listeTeamMembres = db["teamMembers"]
                teamTag = db["teamTag"]

                for elt in listeTeamMembres:

                    userID = elt[1]
                    user = self.server.get_member(userID)

                    if not userID in channel.members:

                        userAbsents.append(user)
                    
                    elif userID in channel.members:

                        usersPresents.append(user)

        return userAbsents, usersPresents


    async def sendNotifEmbedToTeam(self, content):
    
        serverInstance = ServerDBSetup(server=self.server)
        serverInstance.getNotifChannel()


        
                




