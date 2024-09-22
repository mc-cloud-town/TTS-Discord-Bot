import os
from pathlib import Path

import disnake
import numpy as np
import pandas as pd
from disnake.ext import commands

from bot.api.gemini_api import GeminiAPIClient
from config import ModelConfig, GUILD_ID, ANALYSIS_MATERIAL_PROMPT
from utils.logger import logger


class AnalyzeMaterial(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.llm_client = GeminiAPIClient(model_config=ModelConfig())

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

            # 選擇需要的欄位並計算 ShulkerBox 數量
            df['ShulkerBox'] = df['Total'] / (27.0 * 64.0)
            df_prepare = df[df['ShulkerBox'] > 1][['Item', 'ShulkerBox']]

            preparation_steps = ""

            if not df_prepare.empty:
                # 如果有材料需要多於一個 Shulker Box
                preparation_steps = "## 盒裝物品" + "\n".join(
                    [f"- 項目: {row['Item']}, 需要 {row['ShulkerBox']:.2} 個 Shulker Box" for _, row in
                     df_prepare.iterrows()]
                )

            # 移除已經用盒子表示的材料
            df_not_box= df[~df['Item'].isin(df_prepare['Item'])]

            preparation_steps = preparation_steps + "\n\n## 散裝物品" + "\n".join(
                [f"- 項目: {row['Item']}, 需要 {int(row['Total'])} 個材料" for _, row in df_not_box.iterrows()]
            )

            # 發送資料到 LLM 模型進行分析
            response_text, feedback = self.llm_client.get_response_from_text(
                prompt=ANALYSIS_MATERIAL_PROMPT,
                text=preparation_steps
            )

            # 建構 Embed
            embed = disnake.Embed(
                title="材料分析結果",
                description=response_text,
                color=disnake.Color.blurple()
            )

            await inter.edit_original_response("分析完成！")

            # 返回分析結果給用戶
            await inter.send(embed=embed)

            # 附上表格計算結果
            embed = disnake.Embed(
                title="材料分析表",
                description=preparation_steps,
                color=disnake.Color.blurple()
            )

            await inter.send(embed=embed)

            # 刪除文件
            os.remove(file_path)

        except Exception as e:
            logger.error(f"分析文件時出現錯誤: {e}")
            await inter.edit_original_response("分析文件時出現錯誤，請稍後重試。")

def setup(bot: commands.Bot):
    bot.add_cog(AnalyzeMaterial(bot))
