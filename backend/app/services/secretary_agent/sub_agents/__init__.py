"""
Sub-agents for the Personal Secretary system.

Each sub-agent follows SRP (Single Responsibility Principle):
- LearningAgent: English, tech topics, articles, Q&A
- ProductivityAgent: notes, tasks, reminders
- UtilityAgent: weather, calculator, datetime

ISP (Interface Segregation): each agent only gets tools it needs.
OCP (Open-Closed): add a new agent = add a new module + graph node.
"""

from app.services.secretary_agent.sub_agents.learning import (
    create_learning_agent,
    create_learning_tools,
)
from app.services.secretary_agent.sub_agents.productivity import (
    create_productivity_agent,
    create_productivity_tools,
)
from app.services.secretary_agent.sub_agents.utility import (
    create_utility_agent,
    create_utility_tools,
)

__all__ = [
    "create_learning_agent",
    "create_learning_tools",
    "create_productivity_agent",
    "create_productivity_tools",
    "create_utility_agent",
    "create_utility_tools",
]
