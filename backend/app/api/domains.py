from pydantic import BaseModel, Field

class SearchPromptsRequest(BaseModel):
    command: str
    template: str
    #parameters: dict[str, str]

class SearchPromptsResponse(BaseModel):
    system_prompt: str
    user_prompt: str
    #other_prompts: dict[str, str]

"""
{
  "command": "code_review",
  "systemPrompt": "You are an expert in {{ language }}",
  "userPrompt": "please review the following {{ language }} code for code smells and suggest improvements:\n",
  "computerLanguage": "Java",
  "outputLanauage": "Chinese",
  "input": "",
  "inputSource": "text"
}
"""


class CommandRequest(BaseModel):
    cmd: str
    seq: int
    time: int # Unix timestamp
    id: str
    from_: str = Field(..., alias="from")  # Handle Python keyword conflict
    to: str
    msg: str

class CommandResponse(CommandRequest):
    code: int
    desc: str

class PromptRequest(BaseModel):
    # Core OpenAI API fields
    model: str = "gpt-4"  # Default model
    messages: list['Message']  # Chat messages
    temperature: float = 0.7  # Default creativity level
    max_tokens: int = Field(4096, alias="maxTokens")
    # Your application-specific fields
    computer_language: str = Field("", alias="computerLanguage")
    output_language: str = Field("", alias="outputLanguage")
    input_source: str = Field("", alias="inputSource")
    input_content: str = Field("", alias="inputContent")
    track_id: str = Field("", alias="trackId")  # For request tracking
    session_id: str = Field("", alias="sessionId")  # For session tracking

    class Message(BaseModel):
        role: str  # "system", "user", or "assistant"
        content: str  # The message content
        name: str = ""  # Optional name for the message sender

    # Example usage:
    @classmethod
    def create(
        cls,
        system_prompt: str,
        user_prompt: str,
        computer_language: str,
        output_language: str,
        input_content: str = "",
        model: str = "gpt-4"
    ) -> 'PromptRequest':
        return cls(
            model=model,
            messages=[
                cls.Message(role="system", content=system_prompt),
                cls.Message(role="user", content=user_prompt),

            ],
            computer_language=computer_language,
            output_language=output_language,
            input_source="text" if not input_content else "input",
            input_content=input_content
        )

class PromptResponse(BaseModel):
    id: str  # OpenAI response ID
    object: str  # e.g., "chat.completion"
    created: int  # Unix timestamp
    model: str  # e.g., "gpt-4"
    choices: list['Choice']  # List of completion choices
    usage: 'Usage'  # Token usage information

    class Choice(BaseModel):
        index: int
        message: 'Message'
        finish_reason: str  # e.g., "stop", "length"

    class Message(BaseModel):
        role: str  # "assistant", "system", or "user"
        content: str  # The actual response content

    class Usage(BaseModel):
        prompt_tokens: int
        completion_tokens: int
        total_tokens: int