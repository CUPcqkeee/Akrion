import disnake
from disnake.ext import commands
import sqlite3


class MessageTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.author_deleted_message = None
        self.admin_deleted_message = None
        self.reason_deleted_message = None
        self.channel_deleted_message = None
        self.content = None
        self.guild = 387409949442965506

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):

        if before.guild.id == self.guild:

            if before.author.bot:
                return
            await self.bot.wait_until_ready()

            channel_id = 1191740643463139419
            channel = self.bot.get_channel(channel_id)
            thread = channel.get_thread(1191886943190012075)

            if thread:
                try:
                    embed = disnake.Embed(title="Логи - Изменение сообщения",
                                          color=0x303136)
                    embed.add_field(name="",
                                    value=f">>> **Изменил:** {before.author.mention}\n"
                                          f"**Канал:** {before.channel.mention}\n\n", inline=False)
                    embed.add_field(name="",
                                    value=f"> **До изменения**: \n> ```{before.content}```\n> "
                                          f"**После изменения**: \n> ```{after.content}```", inline=False)

                    await thread.send(embed=embed)
                except BaseException as be:
                    print(be)
            else:
                return

    @commands.Cog.listener()
    async def on_message_delete(self, message):

        if message.guild.id == self.guild:

            if message.author.bot:
                return

            await self.bot.wait_until_ready()

            guild = self.bot.get_guild(self.guild)
            channel_id = 1191740643463139419
            channel = self.bot.get_channel(channel_id)
            thread = channel.get_thread(1191886943190012075)
            messages = await guild.audit_logs(action=disnake.AuditLogAction.message_delete,
                                              limit=None).flatten()
            message_deleted = messages[0].user
            if thread:
                try:
                    embed = disnake.Embed(title="Логи - Удаление сообщения",
                                          color=0x303136)
                    embed.add_field(name=f"",
                                    value=f"> **Удалил**: {message_deleted.mention}\n> "
                                          f"**Кому удалил**: {message.author.mention}\n> "
                                          f"**Канал**: {message.channel.mention}\n\n"
                                          f"> **Содержимое**:\n> ```{message.content}```")
                    await thread.send(embed=embed)
                except BaseException as es:
                    print(es)

    @commands.Cog.listener()
    async def on_member_join(self, member):

        await self.bot.wait_until_ready()

        if member.guild.id == self.guild:
            embed = disnake.Embed(title="Логи - Вход на сервер", color=0x303136)
            embed.add_field(name="", value=f"> **Игрок:** {member.mention}\n> "
                                           f"**ID Игрока:** {member.id}", inline=False)  # Айди - member.discriminator
            channel = self.bot.get_channel(1191740643463139419)
            thread = channel.get_thread(1191887184026935306)
            await thread.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):

        await self.bot.wait_until_ready()

        if member.guild.id == self.guild:
            embed = disnake.Embed(title="Логи - Выход из сервер", color=0x303136)
            embed.add_field(name="", value=f"> **Игрок:** {member.mention}\n> "
                                           f"**ID Игрока:** {member.id}", inline=False)  # Айди - member.discriminator
            channel = self.bot.get_channel(1191740643463139419)
            thread = channel.get_thread(1191887251920126093)
            await thread.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_update(self, before, after):

        await self.bot.wait_until_ready()
        if before.guild.id == self.guild:
            guild = self.bot.get_guild(self.guild)
            nick = await guild.audit_logs(action=disnake.AuditLogAction.member_update,
                                          limit=None).flatten()
            author_update_nick = nick[0].user
            if author_update_nick != after:
                author_change_name = author_update_nick
                if before.nick != after.nick:
                    channel = self.bot.get_channel(1191740643463139419)
                    thread = channel.get_thread(1191887110085541938)
                    embed = disnake.Embed(title="Логи - Изменение ника",
                                          colour=0x303136)
                    embed.add_field(name="", value=f"> **Кто изменил**: {author_change_name.mention}\n> "
                                                   f"**Кому изменил**: {before.mention}\n\n"
                                                   f"> **До изменения**: \n> ```{before.nick}```\n> "
                                                   f"**После изменения**: \n> ```{after.nick}```")
                    await thread.send(embed=embed)
            else:
                return


def setup(bot):
    bot.add_cog(MessageTracker(bot))
