# admin_commands.py
import discord
from discord.ext import commands
from bot_setup import create_bot
from config import OWNER, LOG_FILE
from password_manager import get_password, write_password
from utils.logging_utils import append_to_log
import os
import sys


class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.is_owner()
    async def 명령어동기화(self, ctx):
        try:
            synced = await self.bot.tree.sync()
            synced_ids = str(synced)
            synced_ids = synced_ids.replace('>, <','>\n<')
            await ctx.send(f"동기화된 명령어: {len(synced)}개")
            printf=f"({ctx.author}님의 입력)_동기화된 명령어: \n{synced_ids}"
            print(printf)
            append_to_log(printf, LOG_FILE)
        except Exception as e:
            await ctx.send(f"동기화 중 오류 발생: {e}")
            printf=f"({ctx.author}님의 입력)_동기화 오류: {e}"
            print(printf)
            append_to_log(printf, LOG_FILE)

    @commands.command()
    @commands.is_owner()
    async def 명령어리스트(self, ctx):
        commands_list = [command.name for command in self.bot.tree.get_commands()]
        await ctx.send(f"등록된 명령어: /{', /'.join(commands_list)}")
        printf=f"({ctx.author}님의 입력)_명령어리스트 정상 출력됨\n등록된 명령어: {commands_list}"
        print(printf)
        append_to_log(printf, LOG_FILE)

    @commands.command()
    @commands.is_owner()
    async def 명령어리로드(self, ctx, cogname: str):
        try:
            await self.bot.reload_extension(f"cogs.{cogname}")
            await ctx.send(f"{cogname} Cog가 리로드되었습니다.")
            synced = await self.bot.tree.sync()
            await ctx.send(f"명령어 동기화 완료: {len(synced)}개")
            printf=f"({ctx.author}님의 입력)_명령어리로드 정상 출력됨\n{cogname} Cog가 리로드되었습니다.\n명령어 동기화 완료: {len(synced)}개"
            print(printf)
            append_to_log(printf, LOG_FILE)
        except Exception as e:
            await ctx.send(f"리로드 중 오류 발생: {e}")
            printf=f"({ctx.author}님의 입력)_명령어리로드 오류 출력\n리로드 중 오류 발생: {e}"
            print(printf)
            append_to_log(printf, LOG_FILE)

    @commands.command()
    @commands.check(OWNER)
    async def 재시작(self, ctx, given_password: str):
        password = get_password()
        if given_password == password:
            await ctx.send("비밀번호 인증 완료. 봇을 재시작합니다.")
            printf = f"({ctx.author}님의 입력)_재시작 비밀번호 입력!"
            print(printf)
            python = sys.executable
            append_to_log(printf, LOG_FILE)
            os.execl(python, python, *sys.argv)
        else:
            await ctx.send("비밀번호가 일치하지 않습니다.")
            printf = f"({ctx.author}님의 입력)_재시작 '{given_password}'올바르지 않은 비밀번호 입력!"
            print(printf)

    @commands.command()
    @commands.check(OWNER)
    async def 비밀번호변경(self, ctx, current_password: str, new_password: str):
        password = get_password()
        if current_password == password:
            write_password(new_password)
            await ctx.send("비밀번호가 성공적으로 변경되었습니다.")
            printf = f"({ctx.author}님의 입력)_비밀번호 변경 완료: 새 비밀번호 '{new_password}'"
            print(printf)
            append_to_log(printf, LOG_FILE)
        else:
            await ctx.send("현재 비밀번호가 일치하지 않습니다.")
            printf = f"({ctx.author}님의 입력)_비밀번호 변경 실패: 현재 비밀번호가 일치하지 않음"
            print(printf)
            append_to_log(printf, LOG_FILE)

async def setup(bot):
    await bot.add_cog(AdminCommands(bot))