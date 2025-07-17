import discord
from discord.ext import commands
from config import DISCORD_TOKEN

from commands.reviewcv import setup as setup_reviewcv
from utils.scoring import score_cv
from commands.extractinfo import setup as setup_extractinfo
from commands.cvcompare import setup as setup_cvcompare
from commands.help import setup as setup_help
from commands.cvgrammar import setup as setup_cvgrammar

import logging

logging.basicConfig(
    filename='logs/bot.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s:%(name)s: %(message)s'
)

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

setup_reviewcv(bot)
setup_extractinfo(bot)
setup_cvcompare(bot)
setup_help(bot)
setup_cvgrammar(bot)

bot.run(DISCORD_TOKEN)
