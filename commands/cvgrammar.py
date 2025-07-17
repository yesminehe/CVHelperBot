import discord
from discord.ext import commands
import tempfile
import os
from utils.cv_processor import extract_text_from_pdf
import language_tool_python
import logging

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)

def setup(bot: commands.Bot) -> None:
    @bot.command()
    async def cvgrammar(ctx: commands.Context) -> None:
        """
        Check grammar and spelling in the uploaded CV PDF and report the number of issues found.
        """
        await ctx.send("Please upload your CV PDF file to check grammar and spelling.")

        def check(m: discord.Message) -> bool:
            return (
                m.author == ctx.author and
                m.attachments and
                m.attachments[0].filename.lower().endswith(".pdf")
            )

        try:
            msg = await bot.wait_for('message', check=check, timeout=120)
            attachment = msg.attachments[0]
        except Exception:
            logging.exception("An error occurred while waiting for the CV upload in cvgrammar.")
            await ctx.send("An unexpected error occurred. Please try again later.")
            return

        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            temp_path = tmp.name

        try:
            await attachment.save(temp_path)
            cv_text = extract_text_from_pdf(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        tool = language_tool_python.LanguageTool('en-US')
        matches = tool.check(cv_text)
        num_errors = len(matches)

        if num_errors == 0:
            await ctx.send("No grammar or spelling issues found in the CV! 🎉")
        else:
            await ctx.send(f"Found {num_errors} grammar/spelling issues in the CV.")
