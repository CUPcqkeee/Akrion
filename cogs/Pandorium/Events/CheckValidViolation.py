import json
from datetime import datetime, timezone, timedelta

import disnake
from disnake.ext import commands, tasks
from mysql.connector import (connection)
from core import cnx as db

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cursor = db.cursor(buffered=True)


class CheckValid(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_violation_task.start()
        self.guild_id = 847415392485376050
        self.global_role = 1148680568729505842
        self.chat_role = 1142926635532820674
        self.voice_role = 1142926657578086451

    @tasks.loop(minutes=1, reconnect=True)
    async def check_violation_task(self):
        now = datetime.now(timezone(timedelta(hours=+4)))
        thirty_minutes_ago = now - timedelta(minutes=1)

        cursor.execute(f'SELECT id, type FROM `Violation` WHERE `time` <= "{thirty_minutes_ago}"')
        violations = cursor.fetchall()

        if violations:
            for violation in violations:
                id, type = violation
                try:
                    await self.process_violation(id, type)
                except BaseException:
                    await self.process_violation(id, type)

    async def process_violation(self, id, type):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.guild_id)
        now = datetime.now(timezone(timedelta(hours=+4)))
        d_time = now.strftime('%H:%M')
        get_type = cursor.execute(f'SELECT type FROM `Violation` WHERE `id` = "{id}"')
        get_type = cursor.fetchone()

        # try:
        if get_type[0] == '1':
            member = await guild.fetch_member(id)
            if guild:
                global_role = guild.get_role(self.global_role)
                if global_role:
                    try:
                        if global_role in member.roles:
                            await member.remove_roles(global_role)
                            cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{id}' AND `type` = '1'""")
                            db.commit()

                            embed = disnake.Embed(colour=disnake.Color.green(),
                                                  title=f"<:online:892647180614123540> С вас был снят Общий мут!")
                            embed.add_field(
                                name=f"Пожалуйста, не нарушайте больше правил <:like:877264843156123731>",
                                value="")
                            embed.set_footer(text=f"Пандориум • {d_time} ")
                            await member.send(embed=embed)
                        else:
                            pass
                    except BaseException as e:
                        print(e, "global")

        elif get_type[0] == '2':
            member = await guild.fetch_member(id)
            if guild:
                chat_role = guild.get_role(self.chat_role)
                if chat_role:
                    try:
                        if chat_role in member.roles:
                            await member.remove_roles(chat_role)
                            cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{id}' AND `type` = '2'""")
                            db.commit()

                            embed = disnake.Embed(colour=disnake.Color.green(),
                                                  title=f"<:online:892647180614123540> С вас был снят Текстовой мут!")
                            embed.add_field(
                                name=f"Пожалуйста, не нарушайте больше правил <:like:877264843156123731>",
                                value="")
                            embed.set_footer(text=f"Пандориум • {d_time} ")
                            await member.send(embed=embed)
                        else:
                            pass
                    except BaseException as e:
                        print(e, "text")

        elif get_type[0] == 3:
            member = await guild.fetch_member(id)
            if guild:
                voice_role = guild.get_role(self.chat_role)
                if voice_role:
                    try:
                        if voice_role in member.roles:
                            await member.remove_roles(voice_role)
                            cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{id}' AND `type` = '3'""")
                            print("УСПЕШНО УДАЛЕНО")
                            db.commit()

                            embed = disnake.Embed(colour=disnake.Color.green(),
                                                  title=f"<:online:892647180614123540> С вас был снят Голосовой мут!")
                            embed.add_field(
                                name=f"Пожалуйста, не нарушайте больше правил <:like:877264843156123731>",
                                value="")
                            embed.set_footer(text=f"Пандориум • {d_time} ")
                            await member.send(embed=embed)
                        else:
                            pass
                    except BaseException as e:
                        print(e, "voice")

        if get_type[0] == "5":
            guild = self.bot.get_guild(847415392485376050)
            member = guild.get_member(id)
            if guild:
                global_role = disnake.utils.get(guild.roles, id=1162839753461334137)
                if global_role:
                    try:
                        if global_role in member.roles:
                            await member.remove_roles(global_role)
                            cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{id}' AND `type` = '5'""")
                            db.commit()

                            embed = disnake.Embed(colour=disnake.Color.green(),
                                                  title=f"<:online:892647180614123540> С вас был снят Бан!")
                            embed.add_field(
                                name=f"Пожалуйста, не нарушайте больше правил <:like:877264843156123731>",
                                value="")
                            embed.set_footer(text=f"Пандориум • {d_time} ")
                            await member.send(embed=embed)
                        else:
                            pass
                    except BaseException as e:
                        print(e)
    # except BaseException as ev:
    #     try:
    #         guildA = self.bot.get_guild(847415392485376050)
    #         memberA = guildA.get_member(589492162211610662)
    #         embedE = disnake.Embed(colour=disnake.Color.red(),
    #                                title=f"<a:warnings:877264842854113322> ВОЗНИКЛА ПРОБЛЕМА")
    #         embedE.add_field(name=f"Тип ошибки: {ev}", value=f"Сервер: {guildA}")
    #         await memberA.send(embed=embedE)
    #     except BaseException as e:
    #         print(e)


def setup(bot):
    bot.add_cog(CheckValid(bot))
