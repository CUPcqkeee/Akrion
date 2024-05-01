import json

import disnake
from disnake import ButtonStyle
from disnake.ui import Button
from disnake.ext import commands
from mysql.connector import (connection)
from core import bot as bt
from core import cnx as db

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cursor = db.cursor(buffered=True)


class RCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.embed = Embed()
        self.persistents_view = False

    @commands.Cog.listener()
    async def on_ready(self):
        await self.bot.wait_until_ready()
        if self.persistents_view:
            return

        view = disnake.ui.View(timeout=None)
        view.add_item(DropdownMenu())
        view.add_item(DropdownMenu_Result())
        self.bot.add_view(view)
        #self.bot.add_view(view, message_id=1191768122735218688)

    @commands.is_owner()
    @commands.command(name='rc')
    async def recruitment(self, interaction):
        await self.bot.wait_until_ready()
        guild = self.bot.get_guild(387409949442965506)
        channel = guild.get_channel(1191737785565053028)

        perms_owner = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{interaction.author.id}' AND `lvlrights` = 'OWN'""")
        perms_owner = cursor.fetchone()
        perms_dev = cursor.execute(
            f"""SELECT * FROM `Perms` WHERE `user_id` = '{interaction.author.id}' AND `lvlrights` = 'DEV'""")
        perms_dev = cursor.fetchone()

        view = DropdownView()

        if perms_owner or perms_dev:
            if guild:
                if channel:
                    await channel.send(embeds=[self.embed.main_image(), self.embed.main()], view=view)
                else:
                    embed = self.embed.error(decription="Канал не найден")
                    await interaction.response.send(embed=embed, ephemeral=True)
            else:
                embed = self.embed.error(decription="Я не работаю на этом сервере")
                await interaction.response.send(embed=embed, ephemeral=True)
        else:
            embed = self.embed.error(decription="У вас недостаточно прав")
            await interaction.response.send(embed=embed, ephemeral=True)


class RecruitementModal(disnake.ui.Modal):
    def __init__(self, arg):
        self.arg = arg
        self.embed = Embed()
        self.log_channel = 1191740643463139419

        components = [
            disnake.ui.TextInput(label="Ваше имя",
                                 placeholder="Максим",
                                 custom_id="name",
                                 max_length=50,
                                 min_length=2),
            disnake.ui.TextInput(label="Ваш возраст",
                                 placeholder="18",
                                 custom_id="age",
                                 max_length=2,
                                 min_length=1),
            disnake.ui.TextInput(label="Ваш часовой пояс и прайм-тайм",
                                 placeholder="+0 МСК, 8:00 - 20:00",
                                 custom_id="time",
                                 max_length=50),
            disnake.ui.TextInput(label="Имеется ли у вас опыт на данной должности",
                                 placeholder="Если да, то на каких серверах",
                                 custom_id="expirience",
                                 max_length=999,
                                 min_length=5),
            disnake.ui.TextInput(label="Расскажите о себе",
                                 placeholder="Ваш рассказ",
                                 custom_id="about",
                                 style=disnake.TextInputStyle.paragraph,
                                 min_length=10,
                                 max_length=500,
                                 )
        ]
        if arg == "538725888276168735":
            arg = "Moderator"
        elif arg == "1191472711512367174":
            arg = "Control"
        elif arg == "575666099408994316":
            arg = "Support"
        elif arg == "1003322021654040706":
            arg = "Eventer"
        elif arg == "1191767519510401164":
            arg = "TribuneMod"
        super().__init__(title=f"Заявка на {arg}", components=components, custom_id="recruitementModal")

    async def callback(self, interaction: disnake.ModalInteraction) -> None:
        name = interaction.text_values["name"]
        age = interaction.text_values["age"]
        time = interaction.text_values["time"]
        exp = interaction.text_values["expirience"]
        about = interaction.text_values["about"]

        embed = self.embed.sended(arg=self.arg, interaction=interaction)
        await interaction.response.send_message(embed=embed, ephemeral=True)

        channel = interaction.guild.get_channel(self.log_channel)
        embed = self.embed.sended_log(arg=self.arg,
                                      name=name,
                                      age=age,
                                      time=time,
                                      exp=exp,
                                      about=about,
                                      interaction=interaction)

        view = DropdownView_Result()
        thread = channel.get_thread(1191763388771090453)
        message = await thread.send(embed=embed, view=view)

        cursor.execute(f"""INSERT INTO `Staff_Set`(`user_id`, `result`, `type`, `message_id`)
         VALUES ('{interaction.author.id}','NULL','{self.arg}','{message.id}')""")
        db.commit()


class DropdownView(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DropdownMenu())


class DropdownView_Result(disnake.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(DropdownMenu_Result())


class DropdownMenu(disnake.ui.StringSelect):
    def __init__(self):
        dot = "<:ddddd:1191556735433977976>"
        options = [
            disnake.SelectOption(label='Moderator', description="Ответственные за модерацию в войсе", value='mod',
                                 emoji=f"{dot}"),
            disnake.SelectOption(label='Control', description="Ответственные за модерацию в чате", value='ctrl',
                                 emoji=f"{dot}"),
            disnake.SelectOption(label='TribuneMod', description="Ответственные за проведение трибуны", value='tbm',
                                 emoji=f"{dot}"),
            disnake.SelectOption(label='EventMod', description="Ответственные за проведение мероприятий", value='evm',
                                 emoji=f"{dot}"),
            disnake.SelectOption(label='Support', description="Ответственный за помощь по вопросам сервера",
                                 value='sup',
                                 emoji=f"{dot}")
        ]
        super().__init__(
            placeholder="Выберите интересующую вас должность",
            custom_id="choose_role",
            min_values=1,
            max_values=1,
            options=options
        )

    @disnake.ui.select(custom_id="choose_role", reconnect=True)
    async def callback(self, inter: disnake.MessageInteraction):
        selected_option = self.values[0]

        if selected_option == 'mod':
            await inter.response.send_modal(modal=RecruitementModal(arg="538725888276168735"))
        if selected_option == 'ctrl':
            await inter.response.send_modal(modal=RecruitementModal(arg="1191472711512367174"))
        if selected_option == 'tbm':
            await inter.response.send_modal(modal=RecruitementModal(arg="1191767519510401164"))
        elif selected_option == "evm":
            await inter.response.send_modal(modal=RecruitementModal(arg="1003322021654040706"))
        elif selected_option == "sup":
            await inter.response.send_modal(modal=RecruitementModal(arg="575666099408994316"))


class DropdownMenu_Result(disnake.ui.StringSelect):
    def __init__(self):
        self.embed = Embed()
        self.res = Result(bot=bt)

        dot = "<:ddddd:1191556735433977976>"
        options = [
            disnake.SelectOption(label='Принять', description="Принять заяву", value='access',
                                 emoji=f"{dot}"),
            disnake.SelectOption(label='Отклонить', description="Отклонить заявку", value='not_access',
                                 emoji=f"{dot}"),
        ]
        super().__init__(
            placeholder="Решите судьбу игрока",
            custom_id="result_askd",
            min_values=1,
            max_values=1,
            options=options
        )

    @disnake.ui.select(custom_id="result_askd", reconnect=True)
    async def callback(self, inter: disnake.MessageInteraction):
        selected_option = self.values[0]

        if selected_option == 'access':
            await self.res.res_access(message=inter.message.id, admin=inter.author)
        if selected_option == 'not_access':
            await self.res.res_not_access(message=inter.message.id, admin=inter.author)


class Result:
    def __init__(self, bot):
        self.bot = bot
        self.embed = Embed()

    async def res_access(self, message, admin):
        await self.bot.wait_until_ready()
        cursor.execute(f"""SELECT * FROM `Staff_Set` WHERE `message_id` = '{message}'""")
        result = cursor.fetchone()
        guild = self.bot.get_guild(387409949442965506)
        user = await guild.fetch_member(result[0])
        if result:
            for row in result:
                user_id = row[0]
                result = row[1]
                types = row[2]

            requiered_role_id = 1102900444986081310
            requiered_role = guild.get_role(requiered_role_id)
            trainee_role_id = 1191453550694387873
            trainee_role = guild.get_role(trainee_role_id)

            button_access = Button(style=ButtonStyle.green, label=f"Принят на должность Стажёра | {admin.display_name}")
            if requiered_role in user.roles:
                await user.add_roles(trainee_role, reason=f"Принят - {admin.display_name}")

                embed = self.embed.success(description="Вы были приняты на должность **Стажёра**")
                await user.send(embed=embed)

                channel = guild.get_channel(1191740643463139419)
                thread = channel.get_thread(1191763388771090453)
                message = await thread.fetch_message(message)
                await message.edit(components=[button_access])
                return
            else:
                embed = self.embed.error(decription="У вас недостаточно прав")
                await user.send(embed=embed)
        else:
            embed = self.embed.error(decription="Ошибка в запросе к Базе")
            await user.send(embed=embed)

    async def res_not_access(self, message, admin):
        await self.bot.wait_until_ready()
        cursor.execute(f"""SELECT * FROM `Staff_Set` WHERE `message_id` = '{message}'""")
        result = cursor.fetchone()
        guild = self.bot.get_guild(387409949442965506)
        user = await guild.fetch_member(result[0])
        if result:
            for row in result:
                user_id = row[0]
                result = row[1]
                types = row[2]

            requiered_role_id = 1102900444986081310
            requiered_role = guild.get_role(requiered_role_id)

            button_not_access = Button(style=ButtonStyle.gray, label=f"Не принят на должность Стажёра | {admin.display_name}")
            if requiered_role in user.roles:
                embed = self.embed.success(description="Заявка на должность **Стажёра** была отклонена!\nПопробуйте подать ещё раз через некоторое время!")
                await user.send(embed=embed)

                channel = guild.get_channel(1191740643463139419)
                thread = channel.get_thread(1191763388771090453)
                message = await thread.fetch_message(message)
                await message.edit(components=[button_not_access])
                return
            else:
                embed = self.embed.error(decription="У вас недостаточно прав")
                await user.send(embed=embed)
        else:
            embed = self.embed.error(decription="Ошибка в запросе к Базе")
            await user.send(embed=embed)


class Embed:
    def main(self):
        dot = "<:ddddd:1191556735433977976>"
        embed = disnake.Embed(colour=0x2f3136, title="Набор в Staff")
        embed.add_field(name="**Требования от вас:**",
                        value=f"{dot} Уделять серверу не менее 3-х часов в день\n"
                              f"{dot} Быть не младше 16 лет\n"
                              f"{dot} Адекватность и стрессоустойчивость\n"
                              f"{dot} Знать правила сервера\n",
                        inline=False)
        embed.add_field(name="",
                        value=f"**Что вы получите:**\n"
                              f"{dot} Зарплату в виду серверной валюты\n"
                              f"{dot} Интересное времяпровождение\n"
                              f"{dot} Отзывчивую администрацию и дружелюбный коллектив\n"
                              f"\nТеперь наберитесь терпения, я отправлю вам уведомление, если \n вы будете приняты на эту должность!",
                        inline=False)
        return embed

    def main_image(self):
        embed = disnake.Embed(colour=0x2f3136)
        embed.set_image(url="https://i.imgur.com/5VluqZj.png")
        return embed

    def sended(self, arg, interaction):
        embed = disnake.Embed(colour=0x2f3136)
        embed.add_field(name="", value=f"Заявка на должность <@&{arg}> отправлена!")
        embed.set_footer(text=f"Спасибо за заявку. Её рассмотрят в ближайшее время",
                         icon_url=interaction.author.avatar.url)
        return embed

    def sended_log(self, arg, interaction, name, age, time, exp, about):
        embed = disnake.Embed(colour=0x2F3136)
        embed.set_author(name=interaction.author.display_name, icon_url=interaction.author.avatar.url)
        embed.add_field(name=f"", value=f"**Оставил(-а) заявку на должность** <@&{arg}>", inline=False)
        embed.add_field(name=f"", value=f"**Линк** {interaction.author.mention}", inline=False)
        embed.add_field(name=f"Ваше имя", value=f"```{name}```", inline=False)
        embed.add_field(name=f"Ваш возраст", value=f"```{age}```", inline=False)
        embed.add_field(name=f"Ваш часовой пояс", value=f"```{time}```", inline=False)
        embed.add_field(name=f"Опыт работы", value=f"```{exp}```", inline=False)
        embed.add_field(name=f"Рассказ о себе", value=f"```{about}```", inline=False)
        return embed

    def error(self, decription):
        embed = disnake.Embed(colour=0x2F3136)
        embed.add_field(name=f"<a:No_Check:877264845366517770> Произошла ошибка",
                        value=decription)
        return embed

    def success(self, description):
        embed = disnake.Embed(colour=0x2F3136)
        embed.add_field(name=f"<a:Yes_Check:877264845504917565> Поздравляю!",
                        value=description)
        return embed


def setup(bot):
    bot.add_cog(RCommand(bot))
