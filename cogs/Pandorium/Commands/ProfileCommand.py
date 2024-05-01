import io
import sqlite3
from io import BytesIO

import disnake
from disnake.ext import commands
from PIL import Image, ImageDraw, ImageFont

with sqlite3.connect("DBAkrion.db") as db:
    cursor = db.cursor()


    class Command(commands.Cog):
        def __init__(self, bot):
            self.bot = bot

        @commands.slash_command(name="profile", description="Просмотреть профиль пользователя", guild_ids=[847415392485376050])
        async def main_command(self, interaction, пользователь: disnake.User = None):
            if пользователь is None:
                try:
                    await interaction.response.defer()
                    # Создание нового белого изображения
                    image = Image.new('RGB', (1920, 1080), color=(255, 255, 255))
                    draw = ImageDraw.Draw(image)

                    # Загрузка аватарки пользователя
                    avatar_asset = interaction.author.avatar.with_size(64)
                    avatar_data = io.BytesIO(await avatar_asset.read())
                    avatar_image = Image.open(avatar_data).convert("RGBA")

                    # Размещение аватарки, ника и текста "право"
                    image.paste(avatar_image, (150, 150), avatar_image)
                    draw.text((40, 150), interaction.author.name, font=ImageFont.truetype("arial.ttf", 24), fill=(0, 0, 0))
                    draw.text((250, 150), "право", font=ImageFont.truetype("arial.ttf", 24), fill=(0, 0, 0))

                    # Написание текста "5" под аватаркой
                    draw.text((170, 200), "5", font=ImageFont.truetype("arial.ttf", 32), fill=(0, 0, 0))

                    # Преобразование изображения в файл
                    output_buffer = io.BytesIO()
                    image.save(output_buffer, format='PNG')
                    output_buffer.seek(0)

                    # Отправка изображения пользователю
                    await interaction.edit_original_response(file=disnake.File(output_buffer, 'avatar.png'))
                except BaseException as error:
                    print("Ошибка:", error)
            else:
                try:
                    await interaction.response.defer()
                    # Создание нового белого изображения
                    image = Image.new('RGB', (1920, 1080), color=(255, 255, 255))
                    draw = ImageDraw.Draw(image)

                    # Загрузка аватарки пользователя
                    avatar_asset = пользователь.avatar.with_size(64)
                    avatar_data = io.BytesIO(await avatar_asset.read())
                    avatar_image = Image.open(avatar_data).convert("RGBA")

                    # Размещение аватарки, ника и текста "право"
                    image.paste(avatar_image, (150, 150), avatar_image)
                    draw.text((40, 150), пользователь.name, font=ImageFont.truetype("arial.ttf", 24),
                              fill=(0, 0, 0))
                    draw.text((250, 150), "право", font=ImageFont.truetype("arial.ttf", 24), fill=(0, 0, 0))

                    # Написание текста "5" под аватаркой
                    draw.text((170, 200), "5", font=ImageFont.truetype("arial.ttf", 32), fill=(0, 0, 0))

                    # Преобразование изображения в файл
                    output_buffer = io.BytesIO()
                    image.save(output_buffer, format='PNG')
                    output_buffer.seek(0)

                    # Отправка изображения пользователю
                    await interaction.edit_original_response(file=disnake.File(output_buffer, 'avatar.png'))
                except BaseException as error:
                    print("Ошибка:", error)


def setup(bot):
    bot.add_cog(Command(bot))
