import os
from pathlib import Path

import disnake
import pandas as pd
from disnake.ext import commands

from bot.client.base_cog import BaseCog
from config import GUILD_ID
from utils.logger import logger


def calculate_packing_type_and_quantity(total: int) -> tuple[str, float]:
    """
    Calculate the packing type and quantity of shulker boxes needed.
    Args:
        total: Total number of items

    Returns:
        tuple: Packing type and quantity
    """
    if total >= 9 * 64:
        return "盒裝", total / (27.0 * 64.0)  # Full box
    elif 3 * 64 <= total < 9 * 64:
        return "1/3箱", total / (3 * 64)  # 1/3 box, packed in multiples of 9 stacks
    elif 1 * 64 <= total < 3 * 64:
        return "1/9箱", total / 64  # 1/9 box, packed in multiples of 3 stacks
    else:
        return "散裝", total / 64  # Less than a stack


class AnalyzeMaterial(BaseCog):
    def __init__(self, bot: commands.Bot):
        super().__init__(bot)

    @commands.message_command(
        name="分析藍圖材料表",
        description="分析材料列表並提供準備建議，請附加一個 CSV 文件。",
        guild_ids=[GUILD_ID],
    )
    async def analyze_material(self, inter: disnake.ApplicationCommandInteraction):
        """
        分析材料列表並提供準備建議。
        """
        await inter.response.defer(ephemeral=True)

        logger.info(f"分析材料表：{inter.target.id}")

        # 檢查消息是否包含附件
        if not inter.target.attachments:
            await inter.edit_original_response("未找到附件，請附加一個 CSV 文件。")
            return

        # 獲取附件
        attachment = inter.target.attachments[0]
        if not attachment.filename.endswith('.csv'):
            await inter.edit_original_response("附件不是 CSV 文件，請上傳一個 CSV 文件。")
            return

        # 保存附件
        file_path = Path(f'data/material/{attachment.filename}')
        await attachment.save(file_path)

        try:
            await inter.edit_original_response("正在分析材料表，請稍候...")

            # 讀取CSV文件
            df = pd.read_csv(file_path)

            # Apply the calculation to the dataframe
            df['PackingType'], df['ShulkerBox'] = zip(*df['Total'].apply(calculate_packing_type_and_quantity))

            # Generate the preparation steps Markdown
            preparation_steps = ""

            # Full Box (盒裝)
            df_boxed = df[df['PackingType'] == '盒裝']
            if not df_boxed.empty:
                preparation_steps += "## 盒裝物品\n" + "\n".join(
                    [f"- 項目: {row['Item']}, 需要 {row['ShulkerBox']:.2f} 盒 (準備 {int(row['ShulkerBox']) + 1} 盒)"
                     for _, row in df_boxed.iterrows()]
                )

            # 1/3 Box
            df_one_third_box = df[df['PackingType'] == '1/3箱']
            if not df_one_third_box.empty:
                preparation_steps += "\n\n## 1/3盒物品\n" + "\n".join(
                    [
                        f"- 項目: {row['Item']}, 需要 {row['ShulkerBox'] * 3:.2f} 組 (準備 {((int(row['ShulkerBox']) // 9) + 1) * 9} 組)"
                        for _, row in df_one_third_box.iterrows()]
                )

            # 1/9 Box
            df_one_ninth_box = df[df['PackingType'] == '1/9箱']
            if not df_one_ninth_box.empty:
                preparation_steps += "\n\n## 1/9盒物品\n" + "\n".join(
                    [
                        f"- 項目: {row['Item']}, 需要 {row['ShulkerBox']:.2f} 組 (準備 {((int(row['ShulkerBox']) // 3) + 1) * 3} 組)"
                        for _, row in df_one_ninth_box.iterrows()]
                )

            # 散裝
            df_not_boxed = df[df['PackingType'] == '散裝']
            if not df_not_boxed.empty:
                preparation_steps += "\n\n## 散裝物品\n" + "\n".join(
                    [f"- 項目: {row['Item']}, 需要 {int(row['Total'])} 個 (準備 {int(row['ShulkerBox']) + 1} 組)"
                     for _, row in df_not_boxed.iterrows()]
                )

            # 附上表格計算結果
            embed = disnake.Embed(
                title="材料分析表",
                description=preparation_steps,
                color=disnake.Color.blurple()
            )

            await inter.edit_original_response("分析完成！")

            # 返回分析結果給用戶
            await inter.send(embed=embed)

            # 刪除文件
            os.remove(file_path)

        except Exception as e:
            logger.error(f"分析文件時出現錯誤: {e}")
            await inter.edit_original_response("分析文件時出現錯誤，請稍後重試。")


def setup(bot: commands.Bot):
    bot.add_cog(AnalyzeMaterial(bot))
