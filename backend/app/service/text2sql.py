from service.task_handler import BaseTaskHandler

class Text2SQLHandler(BaseTaskHandler):
    async def run(self, params: dict) -> dict:
        question = params.get("question", "")
        db_schema = params.get("db_schema", "")
        dialect = params.get("dialect", "mysql")
        # 这里你可以调用实际的 langchain 逻辑
        sql = f"SELECT * FROM sales WHERE date >= NOW() - INTERVAL 7 DAY;"
        return {"sql": sql}