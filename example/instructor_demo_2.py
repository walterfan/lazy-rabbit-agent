#!/usr/bin/env python3
import simple_llm_agent
from pydantic import BaseModel
from typing import Type, List
import enum

class Labels(str, enum.Enum):
    """Enumeration for single-label text classification."""

    SPAM = "spam"
    NOT_SPAM = "not_spam"


class SinglePrediction(BaseModel):
    """
    Class for a single class label prediction.
    """

    class_label: Labels


# Define Enum class for multiple labels
class MultiLabels(str, enum.Enum):
    TECH_ISSUE = "tech_issue"
    BILLING = "billing"
    GENERAL_QUERY = "general_query"


# Define the multi-class prediction model
class MultiClassPrediction(BaseModel):
    """
    Class for a multi-class label prediction.
    """

    class_labels: List[MultiLabels]


class Classifier:
    def __init__(self, prompt="You are a smart analyst"):
        self._llm_agent = simple_llm_agent.LlmAgent()
        self._system_prompt = prompt

    def classify(self, data: str) -> SinglePrediction:
        return self._llm_agent.get_object_response(self._system_prompt,
            f"Classify the following text: {data}", SinglePrediction)

    def multi_classify(self, data: str) -> MultiClassPrediction:
        """Perform multi-label classification on the input text."""
        return self._llm_agent.get_object_response(self._system_prompt,
            f"Classify the following support ticket: {data}", MultiClassPrediction)


def demo():
    classifier = Classifier()
    # Test single-label classification
    message = "Hello there I'm a Nigerian prince and I want to give you money"
    prediction = classifier.classify(message)
    print(prediction)
    assert prediction.class_label == Labels.SPAM

    ticket = "My account is locked and I can't access my billing info."
    prediction = classifier.multi_classify(ticket)
    print(prediction)
    assert MultiLabels.TECH_ISSUE in prediction.class_labels
    assert MultiLabels.BILLING in prediction.class_labels

if __name__ == "__main__":
    demo()