"""
a worker is Runnable object that for each task, it will create a new thread to run the task.
"""
import asyncio
import threading
from service.llm_service import get_llm_service_instance
from util.agent_logger import logger

class Task:
    def __init__(self, system_prompt=None, user_prompt=None):
        self.system_prompt = system_prompt
        self.user_prompt = user_prompt
        self.result = None


class Worker:
    def __init__(self, prefix):
        self._prefix = prefix
        self._llm_service = get_llm_service_instance()
        self._task = Task()

    async def execute(self, prompt_dict: dict):
        self._task.system_prompt = self._llm_service.get_prompt(f"{self._prefix}_system_prompt")
        self._task.user_prompt = self._llm_service.build_user_prompt(prompt_dict, f"{self._prefix}_user_prompt")
        self._task.result = None
        self._thread = threading.Thread(target=self.run)
        self._thread.start()
        while not self._task.result:
            await asyncio.sleep(0.1)
        self._thread.join()
        return self._task.result

    def run(self):
        self._task.result = self._llm_service.ask_as_str(self._task.system_prompt, self._task.user_prompt)
        logger.info(self._task.result)

    def get_result(self):
        return self._task.result
class Composer(Worker):

    def __init__(self, prefix="compose"):
        super().__init__(prefix)



class Translator(Worker):

    def __init__(self, prefix="translate"):
        super().__init__(prefix)

