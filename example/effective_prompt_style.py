#!/usr/bin/env python3
from pydantic import BaseModel
import simple_llm_agent

class Email(BaseModel):
    subject: str
    message: str

client = simple_llm_agent.LlmAgent()

def generate_email(subject, to, sender, tone):
    system_prompt = "You are a smart sesecretary"
    user_prompt = f"""
        Write an email about {subject} to {to} from {sender}.
        The email should be {tone}.
    """
    return client.get_object_response(system_prompt, user_prompt, Email )


if __name__ == "__main__":
    email = generate_email(
        subject="invitation to all-hands on Monday at 6pm",
        to="All",
        sender="Walter Fan",
        tone="formal",
    )

    print(email.subject)
    #> Invitation to All-Hands Meeting
    print(email.message)
