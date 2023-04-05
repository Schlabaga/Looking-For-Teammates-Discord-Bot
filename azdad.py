class DecisionTeamOwner(discord.ui.View):

    def __init__(self, teamTag, memberUser: discord.Member, ownerUser: discord.User, server: discord.Guild, NotifChannel):
        super().__init__(timeout=3600)
        self.teamTag = teamTag
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
