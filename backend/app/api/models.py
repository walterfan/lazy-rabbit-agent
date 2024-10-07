from pydantic import BaseModel


class SearchPromptsRequest(BaseModel):
    command: str
    template: str
    #parameters: dict[str, str]

class SearchPromptsResponse(BaseModel):
    system_prompt: str
    user_prompt: str
    #other_prompts: dict[str, str]