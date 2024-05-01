import asyncio
import json

import disnake
from disnake.ext import commands
from mysql.connector import (connection)
from datetime import datetime, timezone, timedelta
from core import cnx as db

from disnake.ui import Button

Channel_ID = []
Active_user = []
Role = []
Time_Violation = []

# Роли наказаний
Role_Global_Mute = 1192166110481621052
Role_Chat_Mute = 1028711769599909959
Role_Voice_Mute = 574291156431536132
Role_Ban = 1192166503563399320
Role_Warn = 1192166277280698529

ID_Channel_Logs = 1191740643463139419
ID_Thread_Logs = 1192191531084427326

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

# db = connection.MySQLConnection(user=utils["Database"]["User"],
#                                 password=utils["Database"]["Password"],
#                                 host=utils["Database"]["Host"],
#                                 database=utils["Database"]["Database_Name"])
cursor = db.cursor(buffered=True)


class Core(commands.Cog):
    def __init__(self, bot):
        self.user = None
        self.channel_id = None
        self.bot = bot
        self.buttons = Buttons(self, self.bot)
        self.not_access_roles = [1191473245560504390, 1191479088557346876]
        self.guild_id = 387409949442965506

    async def channel_log(self):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(self.guild_id)
        channel = guild.get_channel(1191740643463139419)
        thread = channel.get_thread(1192191531084427326)
        return thread

    @commands.Cog.listener()
    async def on_button_click(self, interaction):
        await self.buttons.handle_button_click(interaction, user=self.user)

    @commands.has_any_role(1191478744888651786, 1191478906662961313, 1191473245560504390, 1191479088557346876,
                           1191445517381681153, 1102900444986081310)
    @commands.slash_command(name="action",
                            description="Админ команда",
                            guild_ids=[847415392485376050, 387409949442965506])
    async def action(self, ctx,
                     пользователь: disnake.Member, ):
        await ctx.response.defer(ephemeral=True)
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(387409949442965506)
        if guild:
            self.user = пользователь

            if пользователь.bot:
                await ctx.send(content="Это же бездушная машина, зачем её наказывать?", ephemeral=True)
                return

            if пользователь == ctx.author:
                await ctx.send(content="Вы не можете наказать самого себя!", ephemeral=True)
                return

            # try:
            Active_user.clear()
            Active_user.append(пользователь)

            self.channel_id = ctx.channel.id
            user = await self.bot.fetch_user(пользователь.id)
            author_avatar_url = user.avatar.url if user else None

            action_embed = disnake.Embed(
                color=disnake.Color.blurple()
            )
            try:
                action_embed.set_author(name=f"Модерация - {пользователь}", icon_url=author_avatar_url)
            except BaseException as ev:
                action_embed.set_author(name=f"Модерация - {пользователь}")

            last_violation = cursor.execute(f"SELECT `reason` FROM `Violation` WHERE `id` = '{пользователь.id}'")
            result = cursor.fetchone()

            now_date_registration_user = пользователь.created_at
            now_date_joined_user = пользователь.joined_at
            date_registration_user = int(now_date_registration_user.timestamp())
            date_joined_user = int(now_date_joined_user.timestamp())
            action_embed.add_field(name=f"", value=f"**Присоединился**: \n<t:{date_joined_user}:R>")
            action_embed.add_field(name=f"", value=f"**Создан:**\n <t:{date_registration_user}:R>")
            action_embed.set_image(url="https://i.imgur.com/XunDsDM.png")
            if result is not None:
                action_embed.add_field(name="", value=f"**Последнее нарушение**:\n **{result[0]}**")
            else:
                action_embed.add_field(name="", value="**Последнее нарушение**:\n **Отсутствует**")

            user_roles_ids = [role.id for role in ctx.author.roles]
            not_access_roles = [1191473245560504390, 1191479088557346876]
            if any(role_id in user_roles_ids for role_id in not_access_roles):
                buttons = self.buttons.get_buttons_not_bans()
            else:
                buttons = self.buttons.get_buttons()

            await ctx.send(embed=action_embed, ephemeral=True, components=[buttons])
        else:
            print("Отказано в доступе")
            return


class Buttons:
    def __init__(self, bot, core):
        self.bot = bot
        self.core = core

    # КНОПКИ
    async def handle_button_click(self, interaction, user):
        custom_id = interaction.component.custom_id

        # Основные кнопки
        if custom_id == "mute":
            await self.handle_type_mute(interaction, user=user)
        elif custom_id == "warn":
            await self.handle_type_warn(interaction, user=user)
        elif custom_id == "ban":
            await self.handle_type_ban(interaction, user=user)

        # Реализация варна
        elif custom_id == "await_warn":
            await self.await_warn(interaction, user=user)

        # Реализация бана
        elif custom_id == "await_ban":
            await self.await_ban(interaction, user=user)

        # Вариации мута
        elif custom_id == "mute_global":
            await interaction.response.edit_message(components=self.get_global_mute_buttons())
        elif custom_id == "await_mute_global":
            await self.await_global_mute(interaction, user=user)

        # Кнопки вернуться назад
        elif custom_id == "return_one_phase":
            user_roles_ids = [role.id for role in user.roles]
            not_access_roles = [1191473245560504390, 1191479088557346876]
            if any(role_id in user_roles_ids for role_id in not_access_roles):
                await interaction.response.edit_message(components=self.get_buttons_not_bans())
            else:
                await interaction.response.edit_message(components=self.get_buttons())
        elif custom_id == "return_two_phase":
            await interaction.response.edit_message(components=self.get_mute_buttons())

        # Кнопки удаления наказаний
        elif custom_id == "remove_mute_global":
            now = datetime.now(timezone(timedelta(hours=+3)))
            d_time = now.strftime('%H:%M')
            check = cursor.execute(f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
            result = cursor.fetchone()
            if result[0][0]:
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:warnings:877264842854113322> У пользователя отсутствует мут данного типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                global_role = disnake.utils.get(user.guild.roles, id=Role_Global_Mute)
                await user.remove_roles(global_role,
                                        reason=f"Решение администрации")
                await interaction.response.edit_message(components=self.successfully_removed_violation())
                cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = f'{user.id}' AND `type` = '1'""")
                db.commit()
                embed = disnake.Embed(colour=disnake.Color.green(),
                                      title="<:online:892647180614123540> С вас был снят общий мут")
                embed.add_field(name=f"Администратор: {interaction.author}",
                                value=f"")
                embed.set_footer(text=f"Пандориум • {d_time} ")
                await user.send(embed=embed)
        elif custom_id == "remove_mute_text":
            now = datetime.now(timezone(timedelta(hours=+3)))
            d_time = now.strftime('%H:%M')
            check = cursor.execute(f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
            result = cursor.fetchone()
            if result[0][0]:
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:warnings:877264842854113322> У пользователя отсутствует мут данного типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                global_role = disnake.utils.get(user.guild.roles, id=Role_Global_Mute)
                await user.remove_roles(global_role,
                                        reason=f"Решение администрации")
                await interaction.response.edit_message(components=self.successfully_removed_violation())
                cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = f'{user.id}' AND `type` = '2'""")
                db.commit()
                embed = disnake.Embed(colour=disnake.Color.green(),
                                      title="<:online:892647180614123540> С вас был снят текстовой мут")
                embed.add_field(name=f"Администратор: {interaction.author}",
                                value=f"")
                embed.set_footer(text=f"Пандориум • {d_time} ")
                await user.send(embed=embed)
        elif custom_id == "remove_mute_voice":
            now = datetime.now(timezone(timedelta(hours=+3)))
            d_time = now.strftime('%H:%M')
            check = cursor.execute(f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
            check = cursor.fetchone()
            if check[0][0]:
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:warnings:877264842854113322> У пользователя отсутствует мут данного типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                global_role = disnake.utils.get(user.guild.roles, id=Role_Voice_Mute)
                await user.remove_roles(global_role,
                                        reason=f"Решение администрации")
                await interaction.response.edit_message(components=self.successfully_removed_violation())
                cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{user.id}' AND `type` = '3'""")
                db.commit()
                embed = disnake.Embed(colour=disnake.Color.green(),
                                      title="<:online:892647180614123540> С вас был снят голосовой мут")
                embed.add_field(name=f"Администратор: {interaction.author}",
                                value=f"")
                embed.set_footer(text=f"Пандориум • {d_time} ")
                await user.send(embed=embed)
        elif custom_id == "remove_warn":
            # global_role = disnake.utils.get(user.guild.roles, id=Role_Voice_Mute)
            # await user.remove_roles(global_role,
            #                         reason=f"Решение администрации")
            now = datetime.now(timezone(timedelta(hours=+3)))
            d_time = now.strftime('%H:%M')
            check = cursor.execute(f"""SELECT `amount` FROM `Violation` WHERE `id` = '{user.id}'""")
            check = cursor.fetchone()
            if check[0][0]:
                cursor.execute(f"""UPDATE `Violation` SET `amount` = `amount` - '1' WHERE `id` = '{user.id}'""")
                db.commit()
                await interaction.response.edit_message(components=self.successfully_removed_violation())
                embed = disnake.Embed(colour=disnake.Color.green(),
                                      title="<:online:892647180614123540> С вас был снят 1 варн")
                embed.add_field(name=f"Администратор: {interaction.author}",
                                value=f"У вас осталось {check[0]} варн(-ов)")
                embed.set_footer(text=f"Пандориум • {d_time} ")
                await user.send(embed=embed)
            else:
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:warnings:877264842854113322> У пользователя отсутствуют варны")
                await interaction.send(embed=embed, ephemeral=True)
        elif custom_id == "remove_ban":
            now = datetime.now(timezone(timedelta(hours=+3)))
            d_time = now.strftime('%H:%M')
            ban_role = disnake.utils.get(user.guild.roles, id=Role_Ban)
            check = cursor.execute(f"""SELECT * FROM `Violation` WHERE `id` = '{user.id}' AND `type` = '5'""")
            check = cursor.fetchone()
            if check[0][0]:
                await user.remove_roles(ban_role,
                                        reason=f"Решение администрации")
                await interaction.response.edit_message(components=self.successfully_removed_violation())
                cursor.execute(f"""DELETE FROM `Violation` WHERE `id` = '{user.id}' AND `type` = '5'""")
                db.commit()
                embed = disnake.Embed(colour=disnake.Color.green(),
                                      title="<:online:892647180614123540> С вас был снят бан")
                embed.add_field(name=f"Администратор: {interaction.author}",
                                value=f"")
                embed.set_footer(text=f"Пандориум • {d_time} ")
                await user.send(embed=embed)
            else:
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:warnings:877264842854113322> У пользователя отсутствует бан")
                await interaction.send(embed=embed, ephemeral=True)


        elif custom_id == "mute_chat":
            await interaction.response.edit_message(components=self.get_chat_mute_buttons())
        elif custom_id == "await_mute_text":
            await self.await_text_mute(interaction, user=user)

        elif custom_id == "mute_voice":
            await interaction.response.edit_message(components=self.get_voice_mute_buttons())
        elif custom_id == "await_mute_voice":
            await self.await_voice_mute(interaction, user=user)

    # РЕАЛИЗАЦИЯ НАКАЗАНИЙ
    async def await_global_mute(self, interaction, user):
        check_global_mute = cursor.execute(
            f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
        check_global_mute = cursor.fetchall()

        if check_global_mute:
            print(check_global_mute)
            if any('1' in row for row in check_global_mute):
                print("222")
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:No_Check:877264845366517770> У пользователя уже имеется мут такого типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                view = disnake.ui.View(timeout=None)
                view.add_item(ChooseTimeGlobalMute(bot=self.bot))

                await interaction.response.edit_message(view=view)
        else:
            view = disnake.ui.View(timeout=None)
            view.add_item(ChooseTimeGlobalMute(bot=self.bot))

            await interaction.response.edit_message(view=view)

    async def await_text_mute(self, interaction, user):
        check_chat_mute = cursor.execute(
            f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
        check_chat_mute = cursor.fetchall()
        if check_chat_mute:
            if any('2' in row for row in check_chat_mute):
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:No_Check:877264845366517770> У пользователя уже имеется мут такого типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                view = disnake.ui.View(timeout=None)
                view.add_item(ChooseTimeTextMute(bot=self.bot))

                await interaction.response.edit_message(view=view)
        else:
            view = disnake.ui.View(timeout=None)
            view.add_item(ChooseTimeTextMute(bot=self.bot))

            await interaction.response.edit_message(view=view)

    async def await_voice_mute(self, interaction, user):
        check_voice_mute = cursor.execute(
            f"""SELECT `type` FROM `Violation` WHERE `id` = '{user.id}'""")
        check_voice_mute = cursor.fetchall()
        if check_voice_mute:
            if any('3' in row for row in check_voice_mute):
                embed = disnake.Embed(colour=disnake.Color.red(),
                                      title="<a:No_Check:877264845366517770> У пользователя уже имеется мут такого типа")
                await interaction.send(embed=embed, ephemeral=True)
            else:
                view = disnake.ui.View(timeout=None)
                view.add_item(ChooseTimeVoiceMute(bot=self.bot))

                await interaction.response.edit_message(view=view)
        else:
            view = disnake.ui.View(timeout=None)
            view.add_item(ChooseTimeVoiceMute(bot=self.bot))

            await interaction.response.edit_message(view=view)

    async def await_warn(self, interaction, user):
        await interaction.response.send_modal(modal=ReasonWarn(bot=self.bot))
        await interaction.edit_original_response(components=Buttons.last_buttons(self))

    async def await_ban(self, interaction, user):
        cursor.execute(
            f"""SELECT * FROM `Violation` WHERE `id` = '{user.id}' AND `type` = '5'""")
        result = cursor.fetchall()
        if result:
            embed = disnake.Embed(colour=disnake.Color.red(),
                                  title="<a:No_Check:877264845366517770> У пользователя уже имеется бан")
            await interaction.send(embed=embed, ephemeral=True)
        else:
            view = disnake.ui.View(timeout=None)
            view.add_item(ChooseTimeBan(bot=self.bot))

            await interaction.response.edit_message(view=view)

    # Хэндлы
    async def handle_type_mute(self, interaction, user):
        action_embed = disnake.Embed(
            color=disnake.Color.blurple()
        )
        author_avatar_url = user.avatar.url if user else None
        try:
            action_embed.set_author(name=f"Выбор типа мута - {user}", icon_url=author_avatar_url)
        except BaseException:
            action_embed.set_author(name=f"Модерация - {пользователь}")

        cursor.execute(f"""SELECT reason FROM `Violation` WHERE id = '{user.id}' ORDER BY `reason` DESC LIMIT 1;""")
        result = cursor.fetchone()

        now_date_registration_user = user.created_at
        now_date_joined_user = user.joined_at
        date_registration_user = int(now_date_registration_user.timestamp())
        date_joined_user = int(now_date_joined_user.timestamp())
        action_embed.add_field(name=f"", value=f"**Присоединился**: \n<t:{date_joined_user}:R>")
        action_embed.add_field(name=f"", value=f"**Создан:**\n <t:{date_registration_user}:R>")
        action_embed.set_image(url="https://i.imgur.com/XunDsDM.png")
        if result is not None:
            last_violation = result[0]
            action_embed.add_field(name="", value=f"**Последнее нарушение**:\n **{last_violation}**")
        else:
            action_embed.add_field(name="", value="**Последнее нарушение**:\n **Отсутствует**")

        buttons = self.get_mute_buttons()

        await interaction.response.edit_message(embed=action_embed, components=[buttons])

    async def handle_type_warn(self, interaction, user):
        action_embed = disnake.Embed(
            color=disnake.Color.blurple()
        )
        author_avatar_url = user.avatar.url if user else None
        try:
            action_embed.set_author(name=f"Выбор действия варна - {user}", icon_url=author_avatar_url)
        except BaseException:
            action_embed.set_author(name=f"Модерация - {пользователь}")

        cursor.execute(f"""SELECT reason FROM `Violation` WHERE id = '{user.id}' ORDER BY `reason` DESC LIMIT 1;""")
        result = cursor.fetchone()

        now_date_registration_user = user.created_at
        now_date_joined_user = user.joined_at
        date_registration_user = int(now_date_registration_user.timestamp())
        date_joined_user = int(now_date_joined_user.timestamp())
        action_embed.add_field(name=f"", value=f"**Присоединился**: \n<t:{date_joined_user}:R>")
        action_embed.add_field(name=f"", value=f"**Создан:**\n <t:{date_registration_user}:R>")
        action_embed.set_image(url="https://i.imgur.com/XunDsDM.png")
        if result is not None:
            last_violation = result[0]
            action_embed.add_field(name="", value=f"**Последнее нарушение**:\n **{last_violation}**")
        else:
            action_embed.add_field(name="", value="**Последнее нарушение**:\n **Отсутствует**")

        buttons = self.get_warn_buttons()

        await interaction.response.edit_message(embed=action_embed, components=[buttons])

    async def handle_type_ban(self, interaction, user):
        action_embed = disnake.Embed(
            color=disnake.Color.blurple()
        )
        author_avatar_url = user.avatar.url if user else None
        try:
            action_embed.set_author(name=f"Выбор действия бана - {user}", icon_url=author_avatar_url)
        except BaseException:
            action_embed.set_author(name=f"Модерация - {пользователь}")

        cursor.execute(f"""SELECT reason FROM `Violation` WHERE id = '{user.id}' ORDER BY `reason` DESC LIMIT 1;""")
        result = cursor.fetchone()

        now_date_registration_user = user.created_at
        now_date_joined_user = user.joined_at
        date_registration_user = int(now_date_registration_user.timestamp())
        date_joined_user = int(now_date_joined_user.timestamp())
        action_embed.add_field(name=f"", value=f"**Присоединился**: \n<t:{date_joined_user}:R>")
        action_embed.add_field(name=f"", value=f"**Создан:**\n <t:{date_registration_user}:R>")
        action_embed.set_image(url="https://i.imgur.com/XunDsDM.png")
        if result is not None:
            last_violation = result[0]
            action_embed.add_field(name="", value=f"**Последнее нарушение**:\n **{last_violation}**")
        else:
            action_embed.add_field(name="", value="**Последнее нарушение**:\n **Отсутствует**")

        buttons = self.get_ban_buttons()

        await interaction.response.edit_message(embed=action_embed, components=[buttons])

    # КНОПКИ
    def get_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Мут", custom_id="mute"),
            Button(style=disnake.ButtonStyle.gray, label="Варн", custom_id="warn"),
            Button(style=disnake.ButtonStyle.gray, label="Бан", custom_id="ban")
        ]
        return buttons

    def get_buttons_not_bans(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Мут", custom_id="mute"),
            Button(style=disnake.ButtonStyle.gray, label="Варн", custom_id="warn"),
        ]
        return buttons

    def get_mute_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_one_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Общий", custom_id="mute_global"),
            Button(style=disnake.ButtonStyle.gray, label="Текстовой", custom_id="mute_chat"),
            Button(style=disnake.ButtonStyle.gray, label="Голосовой", custom_id="mute_voice")
        ]
        return buttons

    def get_ban_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_one_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Выдать бан", custom_id="await_ban"),
            Button(style=disnake.ButtonStyle.gray, label="Снять бан", custom_id="remove_ban")
        ]
        return buttons

    def get_warn_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_one_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Выдать варн", custom_id="await_warn"),
            Button(style=disnake.ButtonStyle.gray, label="Снять варн", custom_id="remove_warn")
        ]
        return buttons

    def get_global_mute_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_two_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Выдать общий мут", custom_id="await_mute_global"),
            Button(style=disnake.ButtonStyle.gray, label="Снять общий мут", custom_id="remove_mute_global")
        ]
        return buttons

    def get_chat_mute_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_two_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Выдать текстовой мут", custom_id="await_mute_text"),
            Button(style=disnake.ButtonStyle.gray, label="Снять текстовой мут", custom_id="remove_mute_text")
        ]
        return buttons

    def get_voice_mute_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray, label="Вернуться", custom_id="return_two_phase"),
            Button(style=disnake.ButtonStyle.gray, label="Выдать голосовой мут", custom_id="await_mute_voice"),
            Button(style=disnake.ButtonStyle.gray, label="Снять голосовой мут", custom_id="remove_mute_voice")
        ]
        return buttons

    def last_buttons(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray,
                   label="Author: CUPcqkeee | Нажмите ниже, чтобы убрать это сообщение",
                   custom_id="last_buttons")
        ]
        return buttons

    def successfully_removed_violation(self):
        buttons = [
            Button(style=disnake.ButtonStyle.gray,
                   label="Author: CUPcqkeee | Успешное снятие наказания",
                   custom_id="last_buttons")
        ]
        return buttons


# ВРЕМЯ И ПРИЧИНА
class ChooseTimeGlobalMute(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(label="30 Минут", value="30"),
            disnake.SelectOption(label="45 Минут", value="45"),
            disnake.SelectOption(label="60 Минут", value="60"),
            disnake.SelectOption(label="75 Минут", value="75"),
            disnake.SelectOption(label="90 Минут", value="90")
        ]
        super().__init__(placeholder="Выберите время наказания", options=options,
                         custom_id="choose_time_global_mute_menu")

    async def callback(self, interaction: disnake.MessageInteraction):
        Time_Violation.clear()
        Time_Violation.append(self.values[0])

        user = Active_user[0]
        global_role = disnake.utils.get(user.guild.roles, id=Role_Global_Mute)
        # Очистка списка
        Role.clear()
        try:
            if global_role in [role.id for role in user.roles]:
                embed = disnake.Embed(
                    colour=disnake.Color.red(),
                    title="<a:warnings:877264842854113322> У пользователя уже имеется мут"
                )
                await interaction.send(embed=embed, ephemeral=True)
            else:
                Role.append(global_role)
                await interaction.response.send_modal(modal=ReasonGlobalMute(bot=self.bot))
                await interaction.edit_original_response(components=Buttons.last_buttons(self))
        except BaseException as e:
            print(e)
            embeds = disnake.Embed(
                colour=disnake.Color.red(),
                title=f"<:online:892647180614123540> Ошибка использования {e}"
            )
            await interaction.send(embed=embeds, ephemeral=True)


class ChooseTimeTextMute(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(label="30 Минут", value="30"),
            disnake.SelectOption(label="45 Минут", value="45"),
            disnake.SelectOption(label="60 Минут", value="60"),
            disnake.SelectOption(label="75 Минут", value="75"),
            disnake.SelectOption(label="90 Минут", value="90")
        ]
        super().__init__(placeholder="Выберите время наказания", options=options,
                         custom_id="choose_time_global_mute_menu")

    async def callback(self, interaction: disnake.MessageInteraction):
        Time_Violation.clear()
        Time_Violation.append(self.values[0])

        user = Active_user[0]
        text_role = disnake.utils.get(user.guild.roles, id=Role_Chat_Mute)
        # Очистка списка
        Role.clear()
        try:
            if text_role in [role.id for role in user.roles]:
                embed = disnake.Embed(
                    colour=disnake.Color.red(),
                    title="<a:warnings:877264842854113322> У пользователя уже имеется мут"
                )
                await interaction.send(embed=embed, ephemeral=True)
            else:
                Role.append(text_role)
                await interaction.response.send_modal(modal=ReasonTextMute(bot=self.bot))
                await interaction.edit_original_response(components=Buttons.last_buttons(self))
        except BaseException as e:
            embeds = disnake.Embed(
                colour=disnake.Color.red(),
                title=f"<:online:892647180614123540> Ошибка использования {e}"
            )
            await interaction.send(embed=embeds, ephemeral=True)


class ChooseTimeVoiceMute(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(label="30 Минут", value="30"),
            disnake.SelectOption(label="45 Минут", value="45"),
            disnake.SelectOption(label="60 Минут", value="60"),
            disnake.SelectOption(label="75 Минут", value="75"),
            disnake.SelectOption(label="90 Минут", value="90"),
            disnake.SelectOption(label="1 Минута", value="1")
        ]
        super().__init__(placeholder="Выберите время наказания", options=options,
                         custom_id="choose_time_global_mute_menu")

    async def callback(self, interaction: disnake.MessageInteraction):
        Time_Violation.clear()
        Time_Violation.append(self.values[0])

        user = Active_user[0]
        voice_role = disnake.utils.get(user.guild.roles, id=Role_Voice_Mute)
        # Очистка списка
        Role.clear()
        try:
            if voice_role in [role.id for role in user.roles]:
                embed = disnake.Embed(
                    colour=disnake.Color.red(),
                    title="<a:warnings:877264842854113322> У пользователя уже имеется мут"
                )
                await interaction.send(embed=embed, ephemeral=True)
            else:
                Role.append(voice_role)
                await interaction.response.send_modal(modal=ReasonVoiceMute(bot=self.bot))
                await interaction.edit_original_response(components=Buttons.last_buttons(self))
        except BaseException as e:
            embeds = disnake.Embed(
                colour=disnake.Color.red(),
                title=f"<:online:892647180614123540> Ошибка использования {e}"
            )
            await interaction.send(embed=embeds, ephemeral=True)


class ChooseTimeBan(disnake.ui.Select):
    def __init__(self, bot):
        self.bot = bot
        options = [
            disnake.SelectOption(label="6 Часов", value="360"),
            disnake.SelectOption(label="12 Часов", value="720"),
            disnake.SelectOption(label="1 День", value="1440"),
            disnake.SelectOption(label="2 Дня", value="2880"),
            disnake.SelectOption(label="3 Дня", value="4320")
        ]
        super().__init__(placeholder="Выберите время наказания", options=options,
                         custom_id="choose_time_ban_menu")

    async def callback(self, interaction: disnake.MessageInteraction):
        Time_Violation.clear()
        Time_Violation.append(self.values[0])

        user = Active_user[0]
        ban_role = disnake.utils.get(user.guild.roles, id=Role_Ban)
        # Очистка списка
        Role.clear()
        try:
            if ban_role in [role.id for role in user.roles]:
                embed = disnake.Embed(
                    colour=disnake.Color.red(),
                    title="<a:warnings:877264842854113322> У пользователя уже имеется бан"
                )
                await interaction.send(embed=embed, ephemeral=True)
            else:
                Role.append(ban_role)
                await interaction.response.send_modal(modal=ReasonBan(bot=self.bot))
                await interaction.edit_original_response(components=Buttons.last_buttons(self))
        except BaseException as e:
            embeds = disnake.Embed(
                colour=disnake.Color.red(),
                title=f"<:online:892647180614123540> Ошибка использования {e}"
            )
            await interaction.send(embed=embeds, ephemeral=True)


class ReasonGlobalMute(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Укажите причину наказания",
                placeholder="2.1",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                max_length=10,
            )
        ]
        super().__init__(
            title="Причина наказания",
            custom_id="reason_violation_mute",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(colour=disnake.Color.blurple(),
                              title=f"<:yes_minecraft:958081418641149954> Успешная выдача наказания")
        for key, value in inter.text_values.items():
            pass
        await inter.send(embed=embed, ephemeral=True)
        embed_sender = SendLog(self.bot)
        await embed_sender.send_log_embed(type_violation="Общий мут",
                                          admin=inter.author,
                                          user=Active_user[0],
                                          reason=value[:1024],
                                          time=Time_Violation[0],
                                          types=1)


class ReasonTextMute(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Укажите причину наказания",
                placeholder="2.1",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                max_length=10,
            )
        ]
        super().__init__(
            title="Причина наказания",
            custom_id="reason_violation_mute",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(colour=disnake.Color.blurple(),
                              title=f"<:yes_minecraft:958081418641149954> Успешная выдача наказания")
        for key, value in inter.text_values.items():
            pass
        await inter.send(embed=embed, ephemeral=True)
        embed_sender = SendLog(self.bot)
        await embed_sender.send_log_embed(type_violation="Текстовой мут",
                                          admin=inter.author,
                                          user=Active_user[0],
                                          reason=value[:1024],
                                          time=Time_Violation[0],
                                          types=2)


class ReasonVoiceMute(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Укажите причину наказания",
                placeholder="2.1",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                max_length=10,
            )
        ]
        super().__init__(
            title="Причина наказания",
            custom_id="reason_violation_mute",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(colour=disnake.Color.blurple(),
                              title=f"<:yes_minecraft:958081418641149954> Успешная выдача наказания")
        for key, value in inter.text_values.items():
            pass
        await inter.send(embed=embed, ephemeral=True)
        embed_sender = SendLog(self.bot)
        await embed_sender.send_log_embed(type_violation="Голосовой мут",
                                          admin=inter.author,
                                          user=Active_user[0],
                                          reason=value[:1024],
                                          time=Time_Violation[0],
                                          types=3)


class ReasonWarn(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Укажите причину наказания",
                placeholder="2.1",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                max_length=10,
            )
        ]
        super().__init__(
            title="Причина наказания",
            custom_id="reason_violation_mute",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(colour=disnake.Color.blurple(),
                              title=f"<:yes_minecraft:958081418641149954> Успешная выдача наказания")
        for key, value in inter.text_values.items():
            pass
        await inter.send(embed=embed, ephemeral=True)
        guild = inter.guild
        role = guild.get_role(Role_Warn)
        await Active_user[0].add_roles(role, reason="Варн")

        embed_sender = SendLogWarn(self.bot)
        await embed_sender.send_log_embed(type_violation="Варн",
                                          admin=inter.author,
                                          user=Active_user[0],
                                          reason=value[:1024],
                                          types=4)


class ReasonBan(disnake.ui.Modal):
    def __init__(self, bot):
        self.bot = bot
        components = [
            disnake.ui.TextInput(
                label="Укажите причину наказания",
                placeholder="2.1",
                custom_id="reason",
                style=disnake.TextInputStyle.short,
                max_length=10,
            )
        ]
        super().__init__(
            title="Причина наказания",
            custom_id="reason_violation_mute",
            components=components,
        )

    async def callback(self, inter: disnake.ModalInteraction):
        embed = disnake.Embed(colour=disnake.Color.blurple(),
                              title=f"<:yes_minecraft:958081418641149954> Успешная выдача наказания")
        for key, value in inter.text_values.items():
            pass
        await inter.send(embed=embed, ephemeral=True)
        embed_sender = SendLogBan(self.bot)
        await embed_sender.send_log_embed(type_violation="Бан",
                                          admin=inter.author,
                                          user=Active_user[0],
                                          reason=value[:1024],
                                          time=Time_Violation[0],
                                          types=5)


# ЛОГИРОВАНИЕ
class SendLog:
    def __init__(self, bot):
        self.bot = bot

    async def send_log_embed(self, type_violation, types, admin, user, reason, time):
        channel = await self.bot.channel_log()
        now = datetime.now(timezone(timedelta(hours=+3)))
        data_remove_violation = now + timedelta(minutes=int(time))
        d_time = now.strftime('%H:%M')
        text_role = disnake.utils.get(user.guild.roles, id=Role_Chat_Mute)
        cursor.execute(f"""INSERT INTO `Violation` (`id`, `type`, `reason`, `time`, `admin`, `amount`) 
                                      VALUES ('{user.id}',
                                       '{types}',
                                        '{reason}',
                                         '{data_remove_violation}',
                                          '{admin.id}', '1')""")

        db.commit()
        await user.add_roles(text_role,
                             reason=f"{reason} • Администратор: {admin}")
        if channel:
            embed = disnake.Embed(title=f"Логи - {type_violation}",
                                  color=disnake.Color.dark_gray())
            embed.add_field(name="", value=f"Выдал: **{admin}**\n"
                                           f"Нарушитель: **{user}**\n"
                                           f"Причина: **{reason}**\n"
                                           f"Время: **{time} минут**")
            embed.set_footer(text=f"Author - CUPcqkeee • {d_time}")
            await channel.send(embed=embed)
        else:
            print(f"Канал с ID {ID_Channel_Logs} не найден.")


class SendLogWarn:
    def __init__(self, bot):
        self.bot = bot

    async def send_log_embed(self, type_violation, types, admin, user, reason):
        channel = await self.bot.channel_log()
        print("channel: ", channel)
        now = datetime.now(timezone(timedelta(hours=+3)))
        d_time = now.strftime('%H:%M')
        text_role = disnake.utils.get(user.guild.roles, id=Role_Chat_Mute)
        cursor.execute(
            f"""SELECT `amount` FROM `Violation` WHERE `id` = '{user.id}'""")
        result = cursor.fetchone()
        if result:
            cursor.execute(
                f"""UPDATE `Violation` SET `amount` = `amount` + '1', `reason` = CONCAT(`reason`, ' + ', '{reason}') WHERE `id` = '{user.id}'""")
            db.commit()
        else:
            cursor.execute(f"""INSERT INTO `Violation` (`id`, `type`, `reason`, `time`, `admin`, `amount`) 
                                        VALUES ('{user.id}', '{types}', '{reason}', 'NULL', '{admin.id}', '0')""")
            cursor.execute(f"""UPDATE `Violation` SET `amount` = `amount` + '1' WHERE `id` = '{user.id}'""")
            db.commit()
        await user.add_roles(text_role,
                             reason=f"{reason} • Администратор: {admin}")
        if channel:
            check_amounts = cursor.execute(
                f"""SELECT `amount` FROM `Violation` WHERE `id` = '{user.id}'""")
            check_amounts = cursor.fetchone()
            embed = disnake.Embed(title=f"Логи - {type_violation}",
                                  color=disnake.Color.dark_gray())
            embed.add_field(name="", value=f"Выдал: **{admin}**\n"
                                           f"Нарушитель: **{user}**\n"
                                           f"Причина: **{reason}**\n"
                                           f"Варнов: **{check_amounts[0][0]}**")
            embed.set_footer(text=f"Author - CUPcqkeee • {d_time}")
            await channel.send(embed=embed)
        else:
            print(f"Канал с ID {ID_Channel_Logs} не найден.")


class SendLogBan:
    def __init__(self, bot):
        self.bot = bot

    async def send_log_embed(self, type_violation, types, admin, user, reason, time):
        channel = await self.bot.channel_log()
        now = datetime.now(timezone(timedelta(hours=+3)))
        data_remove_violation = now + timedelta(minutes=int(time))
        d_time = now.strftime('%H:%M')
        ban_role = disnake.utils.get(user.guild.roles, id=Role_Ban)
        cursor.execute(f"""INSERT INTO `Violation` (id, type, reason, amount,  time, admin) 
                                      VALUES ('{user.id}', '{types}', '{reason}', 'NULL', '{data_remove_violation}', '{admin.id}')""")

        db.commit()
        await user.add_roles(ban_role,
                             reason=f"{reason} • Администратор: {admin}")
        if int(time) <= int(1000):
            new_time_hourse = (int(time) % (60 * 24)) // 60
            if channel:
                embed = disnake.Embed(title=f"Логи - {type_violation}",
                                      color=disnake.Color.dark_gray())
                embed.add_field(name="", value=f"Выдал: **{admin}**\n"
                                               f"Нарушитель: **{user}**\n"
                                               f"Причина: **{reason}**\n"
                                               f"Время: **{new_time_hourse} час(-ов/-а)**")
                embed.set_footer(text=f"Author - CUPcqkeee • {d_time}")
                await channel.send(embed=embed)
            else:
                print(f"Канал с ID {ID_Channel_Logs} не найден.")
        else:
            if channel:
                new_time_day = int(time) // (60 * 24)
                embed = disnake.Embed(title=f"Логи - {type_violation}",
                                      color=disnake.Color.dark_gray())
                embed.add_field(name="", value=f"Выдал: **{admin}**\n"
                                               f"Нарушитель: **{user}**\n"
                                               f"Причина: **{reason}**\n"
                                               f"Время: **{new_time_day} день(-я)**")
                embed.set_footer(text=f"Author - CUPcqkeee • {d_time}")
                await channel.send(embed=embed)
            else:
                print(f"Канал с ID {ID_Channel_Logs} не найден.")


def setup(bot):
    bot.add_cog(Core(bot))
