import disnake
from disnake.ext import commands
from disnake.ext.commands import errors
from disnake import errors as dpy_errors


class BotErrors(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, err):
        if isinstance(err, errors.CommandNotFound):
            pass
            return

        if isinstance(err, errors.MemberNotFound):
            await ctx.message.delete(delay=5)
            await ctx.reply(content="Пользователь не найден.", delete_after=5)
            return

        if isinstance(err, errors.BotMissingPermissions):
            await ctx.message.delete(delay=5)
            await ctx.reply(content=f"У бота отсутствуют права: {' '.join(err.missing_perms)}.", delete_after=5)
            return

        if isinstance(err, errors.MissingPermissions):
            await ctx.message.delete(delay=5)
            await ctx.reply(content="У вас недостаточно прав.", delete_after=5)
            return

        if isinstance(err, errors.UserInputError):
            await ctx.message.delete(delay=5)
            await ctx.reply(content="Не правильное использование команды.", delete_after=5)
            return

        if isinstance(err, commands.CommandOnCooldown):
            await ctx.message.delete(delay=5)
            await ctx.reply(content=f"У вас еще не прошла задержка на команду.\n**Подождите еще {err.retry_after:.2f} секунд.**", delete_after=5)
            return

        if isinstance(err, dpy_errors.Forbidden):
            await ctx.message.delete(delay=5)
            await ctx.reply(content="У бота нет прав на запуск этой команды.", delete_after=5)
            return

        channel = self.bot.get_channel(1191740643463139419)
        thread = channel.get_thread(1191887427019739166)

        embed = disnake.Embed(
            title="<a:warnings:877264842854113322> Неизвестная ошибка!",
            description="**Произошла неизвестная ошибка!**",
            color=0xff0000)
        embed.add_field(
            name="Ошибка",
            value=f"**```yaml\n{err}\n```**",
            inline=False)
        embed.add_field(
            name="Разработчик бота",
            value="<@589492162211610662>",
            inline=False)
        embed.set_footer(
            text="Пожалуйста, свяжитесь с разработчиком для исправления этой ошибки.")

        embed1 = disnake.Embed(
            title="<a:warnings:877264842854113322> Произошла неизвестная ошибка!",
            color=0x2f3136)
        embed1.add_field(
            name="Участник, создавший ошибку:",
            value=ctx.author.mention,
            inline=False)
        embed1.add_field(
            name="Ошибка была выведена при взаимодействии с командой:",
            value=f"**```yaml\n{ctx.command}\n```**",
            inline=False)
        embed1.add_field(
            name="Ошибка",
            value=f"**```yaml\n{err}\n```**",
            inline=False)
        embed1.set_footer(
            text=f"{ctx.guild} (ID: {ctx.guild.id})",
            icon_url=ctx.guild.icon)

        await ctx.message.delete(delay=25)
        await ctx.reply(embed=embed, delete_after=25)
        await thread.send("<@589492162211610662>", embed=embed1)

    @commands.Cog.listener()
    async def on_slash_command_error(self, ctx, err):
        if isinstance(err, errors.CommandNotFound):
            pass
            return

        if isinstance(err, errors.MemberNotFound):
            await ctx.send(content="Пользователь не найден.", ephemeral=True)
            return

        if isinstance(err, errors.BotMissingPermissions):
            await ctx.send(content=f"У бота отсутствуют права: {' '.join(err.missing_perms)}.", ephemeral=True)
            return

        if isinstance(err, errors.MissingPermissions):
            await ctx.send(content="У вас недостаточно прав.", ephemeral=True)
            return

        if isinstance(err, commands.CommandOnCooldown):
            await ctx.send(content=f"У вас еще не прошла задержка на команду.\n**Подождите еще {err.retry_after:.2f} секунд.**", ephemeral=True)
            return

        if isinstance(err, dpy_errors.Forbidden):
            await ctx.send(content="У бота нет прав на запуск этой команды.", ephemeral=True)
            return

        channel = self.bot.get_channel(1191740643463139419)
        thread = channel.get_thread(1191887427019739166)

        embed = disnake.Embed(
            title="<a:warnings:877264842854113322> Неизвестная ошибка!",
            description="**Произошла неизвестная ошибка!**",
            color=0xff0000)
        embed.add_field(
            name="Ошибка",
            value=f"**```yaml\n{err}\n```**",
            inline=False)
        embed.add_field(
            name="Разработчик бота",
            value="<@589492162211610662>",
            inline=False)
        embed.set_footer(
            text="Пожалуйста, свяжитесь с разработчиком для исправления этой ошибки.")

        embed1 = disnake.Embed(
            title="<a:warnings:877264842854113322> Произошла неизвестная ошибка!",
            color=0x2f3136)
        embed1.add_field(
            name="Участник, создавший ошибку:",
            value=ctx.author.mention,
            inline=False)
        embed1.add_field(
            name="Ошибка была выведена при взаимодействии с командой:",
            value=f"**```yaml\n{ctx.application_command.body.name}\n```**",
            inline=False)
        embed1.add_field(
            name="Ошибка",
            value=f"**```yaml\n{err}\n```**",
            inline=False)
        embed1.set_footer(
            text=f"{ctx.guild} (ID: {ctx.guild.id})",
            icon_url=ctx.guild.icon)

        await ctx.send(embed=embed, ephemeral=True)
        await thread.send("<@589492162211610662>", embed=embed1)


def setup(bot):
    bot.add_cog(BotErrors(bot))
