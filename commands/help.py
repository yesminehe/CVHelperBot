from discord.ext import commands

def setup(bot: commands.Bot) -> None:
    @bot.command(name="cvhelp")
    async def custom_help(ctx: commands.Context) -> None:
        """
        List all available commands and what they do.
        """
        help_text = (
            "**CV Helper Bot Commands:**\n\n"
            "`!reviewcv` — Analyze and summarize a CV, provide feedback, and score it.\n"
            "`!extractinfo` — Extract contact information (email, phone, LinkedIn) from a CV.\n"
            "`!cvcompare` — Compare two CVs (PDFs) and highlight differences or strengths.\n"
            "`!cvgrammar` — Check grammar and spelling in the uploaded CV and report the number of issues found.\n"
            "`!cvhelp` — List all available commands and what they do.\n"
        )
        await ctx.send(help_text)
