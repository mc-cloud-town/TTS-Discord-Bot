import os
from pathlib import Path

import disnake
from disnake.ext import commands

from config import GUILD_ID, DOWNLOAD_DIR, VOICE_MANAGER_ROLE_ID
from utils.logger import logger
from utils.file_utils import (
    load_sample_data,
    list_characters,
    add_character,
    remove_character,
    edit_character,
)


class VoiceManager(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.allowed_role = VOICE_MANAGER_ROLE_ID

    def _has_permission(self, member: disnake.Member) -> bool:
        return any(role.id == self.allowed_role for role in member.roles)

    @commands.slash_command(
        name="voice_add",
        guild_ids=[GUILD_ID],
        description="新增語音角色",
    )
    async def voice_add(
        self,
        inter: disnake.ApplicationCommandInteraction,
        character_name: str = commands.Param(name="角色名稱", desc="請輸入角色名稱"),
        reference_text: str = commands.Param(name="參考文本", desc="TTS 參考文本"),
        audio: disnake.Attachment = commands.Param(name="語音檔案", desc="上傳語音檔案"),
    ):
        if not self._has_permission(inter.author):
            await inter.response.send_message("你沒有權限使用此命令。", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)

        if not audio.filename.lower().endswith((".wav", ".ogg", ".mp3", ".m4a")):
            embed = disnake.Embed(
                title="錯誤",
                description="請上傳有效的音頻檔案。",
                color=disnake.Color.red(),
            )
            await inter.edit_original_response(embed=embed)
            return

        dest_path = Path(DOWNLOAD_DIR).joinpath(audio.filename)
        await audio.save(dest_path)
        try:
            add_character(character_name, audio.filename, reference_text)
        except ValueError:
            dest_path.unlink(missing_ok=True)
            embed = disnake.Embed(
                title="錯誤",
                description="角色已存在。",
                color=disnake.Color.red(),
            )
            await inter.edit_original_response(embed=embed)
            return

        embed = disnake.Embed(
            title="成功",
            description=f"已新增角色 {character_name}",
            color=disnake.Color.green(),
        )
        await inter.edit_original_response(embed=embed)
        logger.info(f"Added voice character {character_name}")

    @commands.slash_command(
        name="voice_remove",
        guild_ids=[GUILD_ID],
        description="刪除語音角色",
    )
    async def voice_remove(
        self,
        inter: disnake.ApplicationCommandInteraction,
        character_name: str = commands.Param(
            name="角色名稱",
            desc="選擇要刪除的角色",
            choices=[disnake.OptionChoice(name=c, value=c) for c in list_characters(load_sample_data())],
        ),
    ):
        if not self._has_permission(inter.author):
            await inter.response.send_message("你沒有權限使用此命令。", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)
        try:
            entry = remove_character(character_name)
            file_path = Path(DOWNLOAD_DIR).joinpath(entry["file"])
            if file_path.exists():
                file_path.unlink()
            embed = disnake.Embed(
                title="成功",
                description=f"已刪除角色 {character_name}",
                color=disnake.Color.green(),
            )
            logger.info(f"Removed voice character {character_name}")
        except ValueError:
            embed = disnake.Embed(
                title="錯誤",
                description="角色不存在。",
                color=disnake.Color.red(),
            )
        await inter.edit_original_response(embed=embed)

    @commands.slash_command(
        name="voice_edit",
        guild_ids=[GUILD_ID],
        description="編輯語音角色",
    )
    async def voice_edit(
        self,
        inter: disnake.ApplicationCommandInteraction,
        character_name: str = commands.Param(
            name="角色名稱",
            desc="選擇要編輯的角色",
            choices=[disnake.OptionChoice(name=c, value=c) for c in list_characters(load_sample_data())],
        ),
        reference_text: str = commands.Param(
            name="參考文本", desc="新的參考文本（留空則不修改）", default=None
        ),
        audio: disnake.Attachment = commands.Param(
            name="語音檔案", desc="新的語音檔案（可選）", default=None
        ),
    ):
        if not self._has_permission(inter.author):
            await inter.response.send_message("你沒有權限使用此命令。", ephemeral=True)
            return
        await inter.response.defer(ephemeral=True)

        filename = None
        if audio:
            if not audio.filename.lower().endswith((".wav", ".ogg", ".mp3", ".m4a")):
                embed = disnake.Embed(
                    title="錯誤",
                    description="請上傳有效的音頻檔案。",
                    color=disnake.Color.red(),
                )
                await inter.edit_original_response(embed=embed)
                return
            dest_path = Path(DOWNLOAD_DIR).joinpath(audio.filename)
            await audio.save(dest_path)
            filename = audio.filename

        try:
            edit_character(character_name, filename=filename, text=reference_text)
            embed = disnake.Embed(
                title="成功",
                description=f"已更新角色 {character_name}",
                color=disnake.Color.green(),
            )
            logger.info(f"Edited voice character {character_name}")
        except ValueError:
            if filename:
                Path(DOWNLOAD_DIR).joinpath(filename).unlink(missing_ok=True)
            embed = disnake.Embed(
                title="錯誤",
                description="角色不存在。",
                color=disnake.Color.red(),
            )

        await inter.edit_original_response(embed=embed)


def setup(bot: commands.Bot):
    bot.add_cog(VoiceManager(bot))
