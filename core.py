import json
import os
from mysql.connector import (connection)
import disnake
from disnake.ext import commands

bot = commands.Bot(
    command_prefix="a.",
    intents=disnake.Intents.all(),
    case_insensitive=True,
    help_command=None,
    allowed_mentions=disnake.AllowedMentions.all())

with open('./cogs/Pandorium/Utils.json', "r") as util:
    utils = json.load(util)

cnx = connection.MySQLConnection(user=utils["Database"]["User"],
                                 password=utils["Database"]["Password"],
                                 host=utils["Database"]["Host"],
                                 database=utils["Database"]["Database_Name"])
cursor = cnx.cursor()


def error_embed(description):
    embed = disnake.Embed(description=f"{description}", colour=disnake.Colour.red())
    embed.set_author(name=f"Ошибка использования!")
    return embed


def success_embed(description):
    embed = disnake.Embed(description=f"{description}", colour=disnake.Colour.green())
    embed.set_author(name=f"Успешное использование")
    return embed


@bot.command(name="load")
async def load(ctx, extension=None):
    perms_owner = cursor.execute(
        f"""SELECT lvlrights FROM `Perms` WHERE `user_id` = '{ctx.author.id}' AND `lvlrights` = 'OWN'""")
    result = cursor.fetchall()

    if result[0][0] is not None:
        if extension is None:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы не указали название модуля")
            await ctx.author.send(embed=embed)
            return
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.message.delete(delay=10)
            embed = success_embed(description=f"Модуль **{extension}** был загружен")
            await ctx.author.send(embed=embed)
            return
        except BaseException:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы указали неверное название модуля")
            await ctx.author.send(embed=embed)
            return

    await ctx.message.delete(delay=5)
    embed = error_embed(description=f"У вас недостаточно прав")
    await ctx.author.send(embed=embed)


@bot.command(name="unload")
async def unload(ctx, extension=None):
    perms_owner = cursor.execute(
        f"""SELECT lvlrights FROM `Perms` WHERE `user_id` = '{ctx.author.id}' AND `lvlrights` = 'OWN'""")
    result = cursor.fetchall()

    if result[0][0] is not None:
        if extension is None:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы не указали название модуля")
            await ctx.author.send(embed=embed)
            return
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.message.delete(delay=10)
            embed = success_embed(description=f"Модуль **{extension}** был отгружен")
            await ctx.author.send(embed=embed)
            return
        except BaseException:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы указали неверное название модуля")
            await ctx.author.send(embed=embed)
            return

    await ctx.message.delete(delay=5)
    embed = error_embed(description=f"У вас недостаточно прав")
    await ctx.author.send(embed=embed)


@bot.command(name="reload")
async def reload(ctx, extension=None):
    perms_owner = cursor.execute(
        f"""SELECT lvlrights FROM `Perms` WHERE `user_id` = '{ctx.author.id}' AND `lvlrights` = 'OWN'""")
    result = cursor.fetchall()

    if result[0][0] is not None:
        if extension is None:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы не указали название модуля")
            await ctx.author.send(embed=embed)
            return
        try:
            bot.load_extension(f"cogs.{extension}")
            await ctx.message.delete(delay=10)
            embed = success_embed(description=f"Модуль **{extension}** был перезагружен")
            await ctx.author.send(embed=embed)
            return
        except BaseException:
            await ctx.message.delete(delay=5)
            embed = error_embed(description=f"Вы указали неверное название модуля")
            await ctx.author.send(embed=embed)
            return

    await ctx.message.delete(delay=5)
    embed = error_embed(description=f"У вас недостаточно прав")
    await ctx.author.send(embed=embed)


path = "./cogs"
for root, dirs, files in os.walk(path):
    for filename in files:
        if filename.endswith(".py"):
            cog_path = os.path.relpath(os.path.join(root, filename), path)
            module = os.path.splitext(cog_path)[0].replace(os.sep, '.')
            bot.load_extension(f"cogs.{module}")

# token = open("token.txt", "r").readline()

bot.run(utils["Main"]["Token"])
