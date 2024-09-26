#!/usr/bin/env python3
import simple_llm_agent
from typing import Type, List, Optional
from enum import Enum
from pydantic import Field, BaseModel, model_validator, ValidationInfo
import re

class Fact(BaseModel):
    fact: str = Field(...)
    substring_quote: List[str] = Field(...)

    @model_validator(mode="after")
    def validate_sources(self, info: ValidationInfo) -> "Fact":
        text_chunks = info.context.get("text_chunk", None)
        spans = list(self.get_spans(text_chunks))
        self.substring_quote = [text_chunks[span[0] : span[1]] for span in spans]
        return self

    def get_spans(self, context):
        for quote in self.substring_quote:
            yield from self._get_span(quote, context)

    def _get_span(self, quote, context):
        for match in re.finditer(re.escape(quote), context):
            yield match.span()

class Analyst:
    def __init__(self):
        self._llm_agent = simple_llm_agent.LlmAgent()
        self._system_prompt = "You are a secure AI assistant trained to handle confidential document queries."



def demo():
    analyst = Analyst()


if __name__ == "__main__":
    demo()