import asyncio
import json

import disnake
from disnake import ModalInteraction
from disnake.ui import Button
from disnake.ext import commands
from mysql.connector import (connection)
from core import cnx as db

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cursor = db.cursor(buffered=True)


class TicketMessage(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.var = Variables(bot)
        self.embed = Embeds()
        self.data = Database()
        self.persistents_view = False

        self.button = Buttons()


    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if self.persistents_view:
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(ChooseTicketType(bot=self.bot))
        self.bot.add_view(view)

    @commands.slash_command(name="tickets",
                            description="Перегенерирование сообщение",
                            guild_ids=[847415392485376050, 387409949442965506],
                            default_member_permissions=1)
    async def ticket_message(self, ctx):
        await self.bot.wait_until_ready()
        #
        if self.data.perms_owner(user=ctx.author.id) is not None:
            if self.var.get_channel_ticket() is not None:
                await ctx.response.defer(ephemeral=True)
                #
                view = ChooseTicketTypeView(bot=self.bot)
                #
                await self.var.get_channel_ticket().purge(limit=None)
                embed = self.embed.ticket_message(bot=self.bot)
                await self.var.get_channel_ticket().send(embed=embed, view=view)
                await ctx.send(f"Успешно!", ephemeral=True)
            else:
                embed = self.embed.error(description="Канал для Тикетов не найден",
                                         member=ctx)
                await ctx.send(embed=embed, ephemeral=True)
        else:
            embed = self.embed.error(description="У вас недостаточно прав",
                                     member=ctx)
            await ctx.send(embed=embed, ephemeral=True)

    @commands.slash_command(name="ticket", guild_ids=[387409949442965506], default_member_permissions=1)
    async def ticket(self, interaction):
        pass

    @ticket.sub_command(name="clear", description="Удаление закрытых обращений")
    async def ticket_clear(self, interaction):
        await interaction.response.defer(ephemeral=True)
        await interaction.send(content="Процесс удаления запущен...", ephemeral=True)

        guild = self.bot.get_guild(387409949442965506)
        close_ticket_categoy = guild.get_channel(1017468432716931102)
        close_ticket_categoy1 = guild.get_channel(1017466513856397323)
        close_ticket_categoy2 = guild.get_channel(1029139609214529568)
        close_ticket_categoy3 = guild.get_channel(1029139889540833310)
        channel_delete = 0

        for channel in interaction.guild.text_channels:
            if channel.category == close_ticket_categoy or channel.category == close_ticket_categoy1 or channel.category == close_ticket_categoy2 or channel.category == close_ticket_categoy3:
                await channel.delete()
                channel_delete = channel_delete + 1

        embed = self.embed.success(description=f"Было удалено **{channel_delete}** закрытых обращений(-я)!",
                                   member=interaction)
        await interaction.send(embed=embed, ephemeral=True)

    @ticket_clear.error
    async def clear_errors(self, error, interaction):
        if isinstance(error, commands.MissingAnyRole):
            await interaction.send(f"У вас отсутствует нужная роль!")

    @commands.Cog.listener()
    async def on_button_click(self, inter):
        custom_id = inter.component.custom_id
        mention = inter.user
        if custom_id == "close_ticket":
            await inter.response.defer()
            await self.bot.wait_until_ready()
            cursor.execute(f"""SELECT * FROM `Tickets` WHERE
                              `status` = 'OPEN'
                              AND `channel_id` = '{inter.channel.id}'""")
            channel = cursor.fetchall()
            bot_guild = self.bot.get_guild(387409949442965506)
            ticket_channel = inter.channel
            ch_id = int(channel[0][2])
            ch = inter.guild.get_channel(ch_id)

            if channel:
                for row in channel:
                    status = row[3]
                if status == "OPEN":
                    if ticket_channel == ch:
                        category_closed_ticket = bot_guild.get_channel(1017468432716931102)
                        role_support = bot_guild.get_role(575666099408994316)
                        try:
                            await inter.send(f"Обращение успешно закрыто! — {mention.mention}")
                            await ticket_channel.edit(category=category_closed_ticket)
                            await ticket_channel.set_permissions(inter.author, read_messages=False,
                                                                 send_messages=False,
                                                                 view_channel=False)
                            await ticket_channel.set_permissions(role_support, read_messages=False,
                                                                 send_messages=False,
                                                                 view_channel=False)
                            cursor.execute(
                                f"""UPDATE `Tickets` SET `status` = 'CLOSED' WHERE `type` = '{channel[0][4]}'""")
                            db.commit()

                        except BaseException as ev:
                            await inter.send(ev, ephemeral=True)
                    else:
                        embed = self.embed.error(description="Вы не в канале обращения", member=inter)
                        await inter.send(embed=embed, ephemeral=True)
                else:
                    await inter.send(f"Как вы вообще сюда зашли?\nУ вас нет открытых обращений!", ephemeral=True)
            else:
                embed = self.embed.error(description="У вас нет открытых обращений",
                                         member=inter)
                await inter.send(embed=embed, ephemeral=True)

            await inter.edit_original_response()


class Buttons:
    def close_button(self):
        button = [
            Button(style=disnake.ButtonStyle.grey,
                   custom_id="close_ticket",
                   label="Закрыть обращение")
        ]
        return button


class ChooseTicketTypeView(disnake.ui.View):
    def __init__(self, bot):
        self.bot = bot
        super().__init__(timeout=None)
        self.add_item(ChooseTicketType(bot=self.bot))


class ChooseTicketType(disnake.ui.StringSelect):
    def __init__(self, bot):
        self.bot = bot

        options = [
            disnake.SelectOption(label='Ничего',
                                 value='nothing',
                                 emoji=f"{utils['Emojis']['dot']}",
                                 default=True),
            disnake.SelectOption(label='Задать вопрос персоналу',
                                 description="Задать вопрос касающийся серверных механик/сервера в целом",
                                 value='ask',
                                 emoji=f"{utils['Emojis']['dot']}"),
            disnake.SelectOption(label='Жалоба на персонал',
                                 description="Подать жалобу на участника персонала",
                                 value='complaint_staff',
                                 emoji=f"{utils['Emojis']['dot']}"),
            disnake.SelectOption(label='Жалоба на участника',
                                 description="Подать жалобу на участника сервера",
                                 value='complaint_member',
                                 emoji=f"{utils['Emojis']['dot']}")
        ]
        super().__init__(
            placeholder="Выберите интересующий вас вопрос",
            custom_id="choose_ticket_type",
            min_values=1,
            max_values=1,
            options=options
        )

    @disnake.ui.select(custom_id="choose_ticket_type", reconnect=True)
    async def callback(self, inter: disnake.MessageInteraction):
        selected_option = self.values[0]

        if selected_option == 'ask':
            await inter.response.send_modal(modal=Modal(selected_option, bot=self.bot))
            await inter.edit_original_response()
        if selected_option == 'complaint_staff':
            await inter.response.send_modal(modal=Modal(selected_option, bot=self.bot))
            await inter.edit_original_response()
        elif selected_option == "complaint_member":
            await inter.response.send_modal(modal=Modal(selected_option, bot=self.bot))
            await inter.edit_original_response()
        elif selected_option == "nothing":
            await inter.response.defer(ephemeral=True)
            await inter.edit_original_response()


class Modal(disnake.ui.Modal):
    def __init__(self, types, bot):
        self.type = types
        self.embed = Embeds()
        self.rep = Reply(bot=bot)
        self.bot = bot

        components = [
            disnake.ui.TextInput(label="Опишите вашу проблему",
                                 placeholder="Ваш рассказ",
                                 custom_id="ask_text",
                                 min_length=10,
                                 style=disnake.TextInputStyle.paragraph)
        ]
        # —
        if types == "ask":
            types = "Вопрос персоналу"
        elif types == "complaint_staff":
            types = "Жалоба на персонал"
        elif types == "complaint_member":
            types = "Жалоба на игрока"

        super().__init__(title=f"Тикет на тему — {types}", components=components, custom_id="ModalTicket")

    async def callback(self, interaction: ModalInteraction, /) -> None:

        guild = self.bot.get_guild(387409949442965506)

        text = interaction.text_values["ask_text"]
        if self.type == "ask":
            check1 = cursor.execute(
                f"""SELECT type, status FROM `Tickets` WHERE `user_id` = '{interaction.author.id}' AND `type` = 'ask'""")
            check1 = cursor.fetchone()
            if check1:
                types = check1[0]
                status = check1[1]
                if types == "ask" and status == 'OPEN':
                    await interaction.send(content=f"У вас уже создано обращение такого типа!", ephemeral=True)
                else:
                    await self.rep.ask(interaction=interaction, type_ticket=self.type, text=text)
            else:
                await self.rep.ask(interaction=interaction, type_ticket=self.type, text=text)

        if self.type == "complaint_staff":
            check2 = cursor.execute(
                f"""SELECT type, status FROM `Tickets` WHERE `user_id` = '{interaction.author.id}' AND `type` = 'complaint_staff'""")
            check2 = cursor.fetchone()
            if check2:
                types = check2[0]
                status = check2[1]
                if types == "complaint_staff" and status == 'OPEN':
                    await interaction.send(content=f"У вас уже создано обращение такого типа!", ephemeral=True)
                else:
                    await self.rep.complaint_staff(interaction=interaction, type_ticket=self.type, text=text)
            else:
                await self.rep.complaint_staff(interaction=interaction, type_ticket=self.type, text=text)
        if self.type == "complaint_member":
            check3 = cursor.execute(
                f"""SELECT type, status FROM `Tickets` WHERE `user_id` = '{interaction.author.id}' AND `type` = 'complaint_member'""")
            check3 = cursor.fetchone()
            if check3:
                types = check3[0]
                status = check3[1]
                if types == "complaint_member" and status == 'OPEN':
                    await interaction.send(content=f"У вас уже создано обращение такого типа!", ephemeral=True)
                else:
                    await self.rep.complaint_member(interaction=interaction, type_ticket=self.type, text=text)
            else:
                await self.rep.complaint_member(interaction=interaction, type_ticket=self.type, text=text)
        if self.type == "nothing":
            await interaction.send(content="Вы установили значение списка на **По умолчанию**", ephemeral=True)
            return
        #


class Reply:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 387409949442965506
        self.guild = self.bot.get_guild(self.guild_id)
        self.category_id = 1017466409439219732
        self.category = self.guild.get_channel(self.category_id)
        self.category_close_ticket_id = 1017468432716931102
        self.category_close_ticket = self.guild.get_channel(self.category_close_ticket_id)
        self.role_support_id = 575666099408994316
        self.role_support = self.guild.get_role(self.role_support_id)
        self.role_s_staff_id = 927329713431646228
        self.role_s_staff = self.guild.get_role(self.role_s_staff_id)
        self.role_s_admin_id = 600258400978468874
        self.role_s_admin = self.guild.get_role(self.role_s_admin_id)
        self.embed = Embeds()
        self.ru_type = ""
        self.data = Database()

        self.button = Buttons()

    async def ask(self, interaction, type_ticket, text):
        #
        self.ru_type = "Вопрос персоналу"
        embed = self.embed.ticket_message_create(user=interaction,
                                                 types=self.ru_type,
                                                 ask_text=text)
        #
        cursor.execute(f"""SELECT * FROM `Tickets_Count`""")
        count = cursor.fetchone()

        #
        if count is not None:
            await interaction.response.defer(ephemeral=True)

            perm = {
                self.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                # self.guild.me: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                interaction.author: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_support: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_s_admin: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_s_staff: disnake.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            await self.bot.wait_until_ready()

            category_open_ticket = self.guild.get_channel(self.category_id)
            open_ticket = await category_open_ticket.create_text_channel(
                name=f"🔹Вопрос персоналу—№{count[0]}—{interaction.author.display_name}",
                overwrites=perm
            )
            if open_ticket:
                try:
                    cursor.execute(f"""INSERT INTO `Tickets`(`user_id`, `guild_id`, `channel_id`, `status`, `type`)
                                         VALUES ('{interaction.author.id}','{self.guild_id}','{open_ticket.id}','OPEN','{type_ticket}')""")
                    cursor.execute(f"""UPDATE `Tickets_Count` SET `count` = `count` + 1""")
                    db.commit()
                    #
                    await asyncio.sleep(2)
                    await self.bot.wait_until_ready()
                    #
                    button = self.button.close_button()
                    await open_ticket.send(f"{self.role_support.mention}", embed=embed, components=[button])
                    #
                    await interaction.send(f"Ваш тикет успешно создан — {open_ticket.mention}", ephemeral=True)
                except BaseException as be:
                    await interaction.send(f"Произошла ошибка: ```{be}```\nСообщите администрации!")
                    return
            else:
                print("Ошибка при создании обращения")

        else:
            cursor.execute(f"""INSERT INTO `Tickets_Count`(`count`) VALUES ('1')""")
            db.commit()
            return

    async def complaint_staff(self, interaction, type_ticket, text):
        #
        self.ru_type = "Жалоба на персонал"
        embed = self.embed.ticket_message_create(user=interaction,
                                                 types=self.ru_type,
                                                 ask_text=text)
        #
        cursor.execute(f"""SELECT * FROM `Tickets_Count`""")
        count = cursor.fetchone()

        #
        if count is not None:
            await interaction.response.defer(ephemeral=True)

            perm = {
                self.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                # self.guild.me: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                interaction.author: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_support: disnake.PermissionOverwrite(view_channel=False, send_messages=False),
                self.role_s_admin: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_s_staff: disnake.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            open_ticket = await self.category.create_text_channel(
                name=f"🔹Жалоба на персонал—№{count[0]}—{interaction.author.display_name}",
                overwrites=perm
            )
            if open_ticket:
                try:
                    cursor.execute(f"""INSERT INTO `Tickets`(`user_id`, `guild_id`, `channel_id`, `status`, `type`)
                                         VALUES ('{interaction.author.id}','{self.guild_id}','{open_ticket.id}','OPEN','{type_ticket}')""")
                    cursor.execute(f"""UPDATE `Tickets_Count` SET `count` = `count` + 1""")
                    db.commit()
                    #
                    await asyncio.sleep(3)
                    await self.bot.wait_until_ready()
                    #
                    user = self.guild.get_member(interaction.author.id)
                    button = self.button.close_button()
                    await open_ticket.send(f"{self.role_s_admin.mention}, {self.role_s_staff.mention}", embed=embed,
                                           components=[button])
                    #
                    await interaction.send(f"Ваш тикет успешно создан — {open_ticket.mention}", ephemeral=True)
                except BaseException as be:
                    await interaction.send(f"Произошла ошибка: ```{be}```\nСообщите администрации!")
                    return
            else:
                print("Ошибка при создании обращения")

        else:
            cursor.execute(f"""INSERT INTO `Tickets_Count`(`count`) VALUES ('1')""")
            db.commit()
            return

    async def complaint_member(self, interaction, type_ticket, text):
        #
        self.ru_type = "Жалоба на игрока"
        embed = self.embed.ticket_message_create(user=interaction,
                                                 types=self.ru_type,
                                                 ask_text=text)
        #
        cursor.execute(f"""SELECT * FROM `Tickets_Count`""")
        count = cursor.fetchone()

        #
        if count is not None:
            await interaction.response.defer(ephemeral=True)

            perm = {
                self.guild.default_role: disnake.PermissionOverwrite(view_channel=False),
                # self.guild.me: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                interaction.author: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_support: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_s_admin: disnake.PermissionOverwrite(view_channel=True, send_messages=True),
                self.role_s_staff: disnake.PermissionOverwrite(view_channel=True, send_messages=True)
            }

            open_ticket = await self.category.create_text_channel(
                name=f"🔹Жалоба на игрока—№{count[0]}—{interaction.author.display_name}",
                overwrites=perm
            )
            if open_ticket:
                try:
                    cursor.execute(f"""INSERT INTO `Tickets`(`user_id`, `guild_id`, `channel_id`, `status`, `type`)
                                         VALUES ('{interaction.author.id}','{self.guild_id}','{open_ticket.id}','OPEN','{type_ticket}')""")
                    cursor.execute(f"""UPDATE `Tickets_Count` SET `count` = `count` + 1""")
                    db.commit()
                    #
                    await asyncio.sleep(3)
                    await self.bot.wait_until_ready()
                    #
                    user = self.guild.get_member(interaction.author.id)
                    button = self.button.close_button()
                    await open_ticket.send(f"{self.role_support.mention}", embed=embed, components=[button])
                    #
                    await interaction.send(f"Ваш тикет успешно создан — {open_ticket.mention}", ephemeral=True)
                except BaseException as be:
                    await interaction.send(f"Произошла ошибка: ```{be}```\nСообщите администрации!")
                    return
            else:
                print("Ошибка при создании обращения")

        else:
            cursor.execute(f"""INSERT INTO `Tickets_Count`(`count`) VALUES ('1')""")
            db.commit()
            return


class Database:

    def perms_owner(self, user):
        cursor.execute(f"""SELECT * FROM `Perms` WHERE `user_id` = '{user}' AND `lvlrights` = 'OWN'""")
        result = cursor.fetchone()
        return result

    def select(self, what, where, condition=None):
        if condition:
            cursor.execute(f"""SELECT {what} FROM `{where}` WHERE `{condition}`""")
            result = cursor.fetchone()
        else:
            cursor.execute(f"""SELECT `{what}` FROM `{where}`""")
            result = cursor.fetchone()
        return result


class Variables:
    def __init__(self, bot):
        self.bot = bot
        self.guild = 387409949442965506
        self.channel = 1194020792883744859
        self.open_thread = 1017466409439219732
        self.close_thread = 1017468432716931102
        self.cupcqkeee = 589492162211610662

    def get_guild(self):
        guild = self.bot.get_guild(self.guild)
        return guild

    def get_channel_ticket(self):
        channel = self.get_guild().get_channel(self.channel)
        return channel

    def get_open_thread_channel(self):
        thread = self.get_guild().get_channel(self.open_thread)
        return thread

    def get_close_thread_channel(self):
        thread = self.get_guild().get_channel(self.close_thread)
        return thread


class Embeds:

    def ticket_message_create(self, user, types, ask_text):
        embed = disnake.Embed(colour=0x36393F)
        embed.add_field(name="",
                        value=f"**Создал обращение** — {user.author.mention}",
                        inline=False)
        embed.add_field(name=f"Тикет на тему - {types}",
                        value=f"**Описание**:\n```{ask_text}```",
                        inline=False)
        embed.set_footer(text=f"Чтобы закрыть обращение — пропишите '/решено' в обращении")
        try:
            embed.set_thumbnail(url=user.author.avatar.url)
        except BaseException:
            pass
        return embed

    def ticket_message(self, bot):
        embed = disnake.Embed(colour=0x36393F)
        embed.set_image(url="https://i.imgur.com/Z2SDSo4.png")
        embed.set_footer(
            text=f"Убедительная просьба не создавать тикеты, которые \nне несут ценности/смысла. Уважайте наше и ваше время!",
            icon_url=bot.user.avatar.url)
        return embed

    def error(self, description, member):
        embed = disnake.Embed(colour=0x36393F, title=f"{utils['Emojis']['not_success']} Произошла ошибка",
                              description=description)
        try:
            embed.set_thumbnail(url=member.author.avatar.url)
        except BaseException:
            pass
        return embed

    def success(self, description, member):
        embed = disnake.Embed(colour=0x36393F, title=f"{utils['Emojis']['success']} Успех!",
                              description=description)
        try:
            embed.set_thumbnail(url=member.author.avatar.url)
        except BaseException:
            pass
        return embed


def setup(bot):
    bot.add_cog(TicketMessage(bot))
