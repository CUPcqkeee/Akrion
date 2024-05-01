import json

import disnake
from mysql.connector import (connection)
from disnake import ButtonStyle
from disnake.ext import commands
from disnake.ui import View, Button
from core import cnx as db

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cursor = db.cursor(buffered=True)


class Verification(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="verify")
    async def verifyinformation(self, ctx):
        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{ctx.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()

        guild_kp = self.bot.get_guild(387409949442965506)

        if perms_owner is not None:
            if ctx.guild == guild_kp:
                channel_verify = self.bot.get_channel(1194668618441568386)

                # embed = disnake.Embed(
                #     color=0x2f3136,
                #     title="Верификация",
                #     description=f"Добро пожаловать на сервер **{ctx.guild}**"
                #                 f"\n\nПрежде чем начнём Ваше ознакомление с сервером, просьбапройти верификацию"
                #                 f"\nВам необходимо нажать на кнопку под этим сообщением"
                # )
                embed = disnake.Embed(colour=0x2f3136)
                embed.set_image(
                    url="https://i.imgur.com/IFStUSw.png")
                # embed.set_footer(
                #     text="После прохождения верификации вы свободно сможете общаться на этом сервере")

                verify_button = View()
                verify_button.add_item(
                    Button(
                        style=ButtonStyle.green,
                        label="Пройти верификацию",
                        custom_id="verify_button"))

                await channel_verify.purge()
                await channel_verify.send(embed=embed, view=verify_button)
                return

        await ctx.message.delete(delay=5)
        await ctx.reply(content="Права на использование есть только у разработчика бота", delete_after=5)

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        guild_kp = self.bot.get_guild(387409949442965506)

        if inter.guild == guild_kp:
            verify_role = disnake.utils.get(inter.guild.roles,
                                            id=1029037374434463815)  # 387409949442965506 - everyone ; 610184544418791426 - участник сервера ; 1029037374434463815 - verify ;
            user_role = disnake.utils.get(inter.guild.roles, id=610184544418791426)

            if inter.channel.id == 1194668618441568386:
                if inter.component.custom_id == "verify_button":
                    if verify_role in inter.author.roles:
                        if user_role in inter.author.roles:
                            embed = disnake.Embed(title=f"<:branding:1004492631117664287> Ура-ура!", colour=0x2f3136)
                            embed.add_field(name="", value=f"Вы успешно прошли верификацию на сервере **{guild_kp}**")
                            await inter.author.send(embed=embed)
                            await inter.send("Успех!", ephemeral=True)
                            await inter.author.remove_roles(verify_role, reason="Прохождение верификации")
                            return

                        embed = disnake.Embed(title=f"<:branding:1004492631117664287> Ура-ура!", colour=0x2f3136)
                        embed.add_field(name="", value=f"Вы успешно прошли верификацию на сервере **{guild_kp}**")
                        await inter.author.send(embed=embed)
                        await inter.send("Успех!", ephemeral=True)
                        await inter.author.add_roles(user_role, reason="Прохождение верификации")
                        await inter.author.remove_roles(verify_role, reason="Прохождение верификации")
                        return

                    await inter.send(content="Вы уже верифицированы", ephemeral=True)


def setup(bot):
    bot.add_cog(Verification(bot))
