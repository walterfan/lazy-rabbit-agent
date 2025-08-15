class BaseTaskHandler:
    async def run(self, params: dict) -> dict:
        raise NotImplementedError

