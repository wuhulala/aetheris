from abc import abstractmethod
from typing import List


class AworldBaseAgent:


    @abstractmethod
    def agent_name(self) -> str:
        pass


    async def run(
            self,
            user_message: str,
            model_id: str,
            messages: List[dict],
            body: dict
    ):
        pass