from openai import OpenAI

from app.gpt.base import GPT
from app.gpt.provider.OpenAI_compatible_provider import OpenAICompatibleProvider
from app.gpt.universal_gpt import UniversalGPT
from app.models.model_config import ModelConfig


class GPTFactory:
    """LLM 实例工厂。

    项目内的供应商都尽量收敛到 OpenAI-compatible 协议，因此业务层只需要传入
    ModelConfig，就能获得统一的 GPT 抽象实现。
    """

    @staticmethod
    def from_config(config: ModelConfig) -> GPT:
        """根据数据库中的模型配置创建 GPT 客户端。"""
        client = OpenAICompatibleProvider(api_key=config.api_key, base_url=config.base_url).get_client
        return UniversalGPT(client=client, model=config.model_name)
