import json

import disnake
from mysql.connector import (connection)
from disnake.ext import commands
from core import cnx as db

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cursor = db.cursor(buffered=True)


class InteractionDatabase(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: disnake.Message):
        if message.guild:
            aboutme_entry = cursor.execute(
                f"""SELECT user_id FROM `Aboutme` WHERE `user_id` = '{message.author.id}' AND `guild_id` = '{message.guild.id}'""")
            aboutme_entry = cursor.fetchone()
            perms_entry = cursor.execute(
                f"""SELECT user_id FROM `Perms` WHERE `user_id` = '{message.author.id}'""")
            perms_entry = cursor.fetchone()

            if aboutme_entry is None:
                cursor.execute(
                    f"""INSERT INTO `Aboutme` 
                    VALUES ('{message.guild.id}', '{message.author.id}', 'Пользователь ничего о себе не рассказал.')""")
                db.commit()

            if perms_entry is None:
                cursor.execute(f"""INSERT INTO `Perms` VALUES ('{message.author.id}', 'USER')""")
                db.commit()
        else:
            print("3")

    @commands.Cog.listener()
    async def on_member_join(self, member: disnake.Member):
        aboutme_entry = cursor.execute(
            f"""SELECT user_id FROM `Aboutme` WHERE `user_id` = '{member.id}' AND `guild_id` = '{member.guild.id}'""")
        aboutme_entry = cursor.fetchone()
        perms_entry = cursor.execute(f"""SELECT user_id FROM `Perms` WHERE `user_id` = '{member.id}'""")
        perms_entry = cursor.fetchone()

        if aboutme_entry is None:
            cursor.execute(
                f"""INSERT INTO `Aboutme` VALUES ('{member.guild.id}', '{member.id}', 'Пользователь ничего о себе не рассказал.')""")
            db.commit()

        if perms_entry is None:
            cursor.execute(f"""INSERT INTO `Perms` VALUES ('{member.id}', 'USER')""")
            db.commit()

    @commands.slash_command(guild_ids=[387409949442965506])
    async def database(self, inter):
        pass

    @database.sub_command(name="add",
                          description="Добавить пользователя в БД",
                          options=[disnake.Option(name="user",
                                                  description="Укажите пользователя",
                                                  type=disnake.OptionType.user,
                                                  required=True)],
                          guild_ids=[387409949442965506])
    async def adddatabase(self, inter, user: disnake.User):
        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{inter.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()

        aboutme_entry = cursor.execute(
            f"""SELECT user_id FROM `Aboutme` WHERE `user_id` = '{user.id}' AND `guild_id` = '{inter.guild.id}'""")
        aboutme_entry = cursor.fetchone()
        badges_entry = cursor.execute(f"""SELECT `user_id` FROM `Badges` WHERE `user_id` = '{user.id}'""")
        badges_entry = cursor.fetchone()
        perms_entry = cursor.execute(f"""SELECT `user_id` FROM `Perms` WHERE `user_id` = '{user.id}'""")
        perms_entry = cursor.fetchone()

        if perms_owner is not None:
            if aboutme_entry is None:
                cursor.execute(
                    f"""INSERT INTO `Aboutme` VALUES ('{inter.guild.id}', '{user.id}', 'Пользователь ничего о себе не рассказал.')""")
                db.commit()

                await inter.send(content=f"Пользователь {user.mention} добавлен в таблицу **aboutme**.", ephemeral=True)
            else:
                await inter.send(content=f"Пользователь {user.mention} был зарегистрирован в таблице **aboutme**.",
                                 ephemeral=True)

            if badges_entry is None:
                cursor.execute(f"""INSERT INTO `Badges` VALUES ('{user.id}', 'None')""")
                db.commit()

                await inter.send(content=f"Пользователь {user.mention} добавлен в таблицу **badges**.", ephemeral=True)
            else:
                await inter.send(content=f"Пользователь {user.mention} был зарегистрирован в таблице **badges**.",
                                 ephemeral=True)

            if perms_entry is None:
                cursor.execute(f"""INSERT INTO `Perms` VALUES ('{user.id}', 'USER')""")
                db.commit()

                await inter.send(content=f"Пользователь {user.mention} добавлен в таблицу **perms**.", ephemeral=True)
            else:
                await inter.send(content=f"Пользователь {user.mention} был зарегистрирован в таблице **perms**.",
                                 ephemeral=True)
        else:
            await inter.send(content="Права на использование есть только у разработчика бота.", ephemeral=True)

    @database.sub_command(name="remove",
                          description="Удалить пользователя из БД",
                          options=[disnake.Option(name="user",
                                                  description="Укажите пользователя",
                                                  type=disnake.OptionType.user,
                                                  required=True)],
                          guild_ids=[387409949442965506])
    async def removedatabase(self, inter, user: disnake.User):
        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{inter.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()

        owner_entry = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = {user.id} AND `lvlrights` = 'OWN'""")
        owner_entry = cursor.fetchone()
        aboutme_entry = cursor.execute(
            f"""SELECT user_id FROM `Aboutme` WHERE `user_id` = '{user.id}' AND `guild_id` = '{inter.guild.id}'""")
        aboutme_entry = cursor.fetchone()
        perms_entry = cursor.execute(f"""SELECT user_id FROM `Perms` WHERE `user_id` = '{user.id}'""")
        perms_entry = cursor.fetchone()

        if perms_owner is not None:
            if owner_entry is not None:
                await inter.send(
                    content="Нельзя взаимодействовать с пользователями, уровень прав которых равен **OWN**.",
                    ephemeral=True)
                return

            if aboutme_entry is not None:
                cursor.execute(f"""DELETE FROM `Aboutme` WHERE `user_id` = '{user.id}'""")
                db.commit()

                await inter.send(content=f"Пользователь {user.mention} удалён из таблицы **Aboutme**.", ephemeral=True)
            else:
                await inter.send(content=f"Пользователь {user.mention} уже был удалён в таблице **Aboutme**.",
                                 ephemeral=True)

            if perms_entry is not None:
                cursor.execute(f"""DELETE FROM `Perms` WHERE `user_id` = '{user.id}'""")
                db.commit()

                await inter.send(content=f"Пользователь {user.mention} удалён из таблицы **perms**.", ephemeral=True)
            else:
                await inter.send(content=f"Пользователь {user.mention} уже был удалён в таблице **perms**.",
                                 ephemeral=True)
        else:
            await inter.send(
                content="Права на использование есть только у разработчика бота, уровень прав которого равен **OWN**.",
                ephemeral=True)

    @database.sub_command(name="perms",
                          description="Изменить права пользователя",
                          options=[disnake.Option(name="user",
                                                  description="Укажите пользователя",
                                                  type=disnake.OptionType.user,
                                                  required=True),
                                   disnake.Option(name="perms",
                                                  description="Установите права пользователя",
                                                  type=disnake.OptionType.string,
                                                  required=True)],
                          guild_ids=[387409949442965506])
    async def permsdatabase(self, inter, user: disnake.User, perms: str):
        perms_owner = cursor.execute(
            f"""SELECT * FROM perms WHERE user_id = {inter.author.id} AND lvl_rights = 'OWN'""")
        perms_owner = cursor.fetchone()
        perms_entry = cursor.execute(f"""SELECT user_id FROM perms WHERE user_id = {user.id}""")
        perms_entry = cursor.fetchone()

        if perms_owner is not None:

            if perms_entry is None:
                cursor.execute(f"""INSERT INTO `Perms` VALUES ('{user.id}', 'USER')""")
                db.commit()

            try:
                cursor.execute(
                    f"""UPDATE `Perms` SET `lvlrights` = '{perms}' WHERE `user_id` = '{user.id}' AND `lvlrights` != 'OWN'""")
                db.commit()
            except BaseException:
                await inter.send(
                    content="Нельзя взаимодействовать с пользователями, уровень прав которых равен **OWN**.",
                    ephemeral=True)
                return

            await inter.send(
                content=f"Изменено значение **lvlrights** на {perms} у пользователя {user.mention} в базе данных.",
                ephemeral=True)
            return

        await inter.send(content="Права на использование есть только у разработчика бота.", ephemeral=True)

    @database.sub_command(name="verify-add",
                          description="Верификацировать пользователя",
                          options=[disnake.Option(name="user",
                                                  description="Укажите пользователя",
                                                  type=disnake.OptionType.user,
                                                  required=True)],
                          guild_ids=[387409949442965506])
    async def addverifydatabase(self, inter, user: disnake.User):
        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{inter.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()
        badges_entry = cursor.execute(f"""SELECT `user_id` FROM `Badges` WHERE `user_id` = '{user.id}'""")
        badges_entry = cursor.fetchone()

        if perms_owner is not None:
            if badges_entry is None:
                cursor.execute(f"""INSERT INTO `Badges` VALUES ('{user.id}', 'None')""")
                db.commit()

            cursor.execute(f"""UPDATE `Badges` SET `verify_status` = 'VERIFY' WHERE `user_id` = '{user.id}'""")
            db.commit()

            await inter.send(
                content=f"Изменено значение **verify_status** на **VERIFY** у пользователя {user.mention} в базе данных.",
                ephemeral=True)
            return

        await inter.send(content="Права на использование есть только у разработчика бота.", ephemeral=True)

    @database.sub_command(name="verify-remove",
                          description="Убрать верификацию у пользователя",
                          options=[disnake.Option(name="user",
                                                  description="Укажите пользователя",
                                                  type=disnake.OptionType.user,
                                                  required=True)],
                          guild_ids=[387409949442965506])
    async def removeverifydatabase(self, inter, user: disnake.User):
        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{inter.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()

        badges_entry = cursor.execute(f"""SELECT `user_id` FROM `Badges` WHERE `user_id` = '{user.id}'""")
        badges_entry = cursor.fetchone()

        if perms_owner is not None:
            if badges_entry is None:
                cursor.execute(f"""INSERT INTO `Badges` VALUES ('{user.id}', 'None', 'Нет значков.')""")
                db.commit()

            cursor.execute(f"""UPDATE `Badges` SET `verify_status` = 'None' WHERE `user_id` = '{user.id}'""")
            db.commit()

            await inter.send(
                content=f"Изменено значение **verify_status** на **None** у пользователя {user.mention} в базе данных.",
                ephemeral=True)
            return

        await inter.send(content="Права на использование есть только у разработчика бота.", ephemeral=True)


def setup(bot):
    bot.add_cog(InteractionDatabase(bot))
