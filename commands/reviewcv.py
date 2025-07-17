import discord
from discord.ext import commands
import tempfile
from utils.cv_processor import extract_text_from_pdf
from ai.ai_feedback import get_cv_feedback
import logging
import os
from utils.scoring import score_cv

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)

def setup(bot: commands.Bot) -> None:
    """
    Registers the reviewcv command with the provided bot instance.
    """
    @bot.command()
    @commands.cooldown(1, 120, commands.BucketType.user)
    async def reviewcv(ctx: commands.Context) -> None:
        """
        Discord command to review a user's CV.
        Prompts the user to upload a PDF, extracts text, and provides AI feedback.
        """
        await ctx.send("Please upload your CV PDF file.")

        def check(m: discord.Message) -> bool:
            return (
                m.author == ctx.author and
                m.attachments and
                m.attachments[0].filename.lower().endswith(".pdf")
            )

        try:
            # Wait for the user to upload a PDF file
            msg = await bot.wait_for('message', check=check, timeout=120)
            attachment = msg.attachments[0]
        except Exception:
            logging.exception("An error occurred while processing the CV upload.")
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

        if not cv_text.strip():
            await ctx.send(
                "Sorry, I couldn't extract any text from your PDF. "
                "This may happen if your CV is scanned or contains only images. "
                "Please try uploading a text-based PDF."
            )
            return

        await ctx.send("Analyzing your CV... Please wait.")
        feedback = get_cv_feedback(cv_text)
        if not feedback.strip():
            await ctx.send(
                "Sorry, I couldn't generate feedback for your CV. "
                "Please try again later or check your file."
            )
            return
        score = score_cv(cv_text)
        await ctx.send(f"Your CV Score: {score}/100\n\nHere is your CV feedback:\n{feedback}")

    @reviewcv.error
    async def reviewcv_error(ctx: commands.Context, error: Exception) -> None:
        if isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f"This command is on cooldown. Please wait {int(error.retry_after)} seconds before using it again."
            )
        else:
            logging.exception("An error occurred in reviewcv_error.")
            await ctx.send("An unexpected error occurred. Please try again later.")
