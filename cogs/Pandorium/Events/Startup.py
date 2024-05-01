import asyncio
import json
import sqlite3

import disnake
from disnake.ext import commands
from datetime import datetime, timezone, timedelta


class startUp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.start_time = datetime.now()

    @commands.Cog.listener()
    async def on_ready(self):
        with open('./cogs/Pandorium/Utils.json', "r") as util:
            utils = json.load(util)

        now = datetime.now(timezone(timedelta(hours=+3)))
        d_time = now.strftime('%H:%M')
        channel = self.bot.get_channel(1142639804350201898)
        avatar_url = self.bot.user.avatar.url
        user_id = 589492162211610662
        user = await self.bot.fetch_user(user_id)
        author_avatar_url = user.avatar.url if user else None
        uptime = datetime.now() - self.start_time
        milliseconds = uptime.microseconds // 1000

        online_emoji = "<:online:892647180614123540>"
        time_startup = "<:stage_channel:906947237559537804>"

        embed = disnake.Embed(
            color=0x2f3136,
            title=f"{online_emoji} Бот {self.bot.user.name} был инициализирован",
            description=f"{time_startup} Время запуска: **{milliseconds} мс**"
        )
        embed.set_thumbnail(url=avatar_url)

        embed.set_footer(icon_url=author_avatar_url, text=f"Автор: {utils['Main']['Author']} • {d_time}")
        await channel.send(embed=embed)

        print(f"Бот {self.bot.user.name} запущен!")


def setup(bot):
    bot.add_cog(startUp(bot))
