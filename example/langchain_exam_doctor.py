#!/usr/bin/env python3
import os
import re
#from langchain.chat_models import ChatOpenAI
from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain


from langchain.prompts import PromptTemplate
from loguru import logger
from dotenv import load_dotenv

load_dotenv()


class DiagnosisChain:
    def __init__(self):
        # Define the OpenAI LLM with the provided API key
        self.llm = ChatOpenAI(
            model='deepseek-chat',
            openai_api_key=os.getenv("LLM_API_KEY"),
            openai_api_base=os.getenv("LLM_BASE_URL"),
            max_tokens=1024
        )

        # Define the prompt template to get structured JSON output
        self.prompt_template = PromptTemplate(
            input_variables=["doctor_input"],
            template="""
            You are a medical assistant. Based on the input from the doctor, provide a diagnosis in a JSON format.

            Doctor's input: "{doctor_input}"

            Please structure the output like this:
            {
                "symptoms": [...],
                "diagnosis": "...",
                "recommendation": "..."
            }
            """
        )

        # Combine the LLM and prompt into a chain
        self.chain = LLMChain(
            llm=self.llm,
            prompt=self.prompt_template
        )

    def extract_symptoms(self, doctor_input):
        """
        Extract symptoms from the doctor's input using regex or keyword matching.
        """
        symptoms_keywords = ['pain', 'fever', 'cough', 'shortness of breath', 'dizziness']
        symptoms = [word for word in symptoms_keywords if word in doctor_input.lower()]
        if not symptoms:
            symptoms = ["unspecified symptom"]
        return symptoms

    def extract_diagnosis(self, doctor_input):
        """
        Provide a mock diagnosis based on input. In a real-world case, this could be more complex,
        potentially involving medical knowledge bases.
        """
        if 'chest pain' in doctor_input.lower() or 'shortness of breath' in doctor_input.lower():
            return "possible cardiac issue"
        elif 'fever' in doctor_input.lower():
            return "viral infection"
        else:
            return "unspecified diagnosis"

    def extract_recommendation(self, doctor_input):
        """
        Provide a mock recommendation based on the symptoms/diagnosis.
        """
        if 'chest pain' in doctor_input.lower() or 'shortness of breath' in doctor_input.lower():
            return "immediate ECG and consult a cardiologist"
        elif 'fever' in doctor_input.lower():
            return "rest, hydration, and over-the-counter fever reducer"
        else:
            return "further investigation needed"

    def run(self, doctor_input):
        """
        This method runs the chain and applies custom functions for symptoms, diagnosis, and recommendations.
        """
        # Run the chain to get the LLM's raw output (if you'd like to use it)
        raw_output = self.chain.run(doctor_input=doctor_input)

        # Post-process the output manually by calling the helper functions
        structured_output = {
            "symptoms": self.extract_symptoms(doctor_input),
            "diagnosis": self.extract_diagnosis(doctor_input),
            "recommendation": self.extract_recommendation(doctor_input)
        }
        return structured_output


# Example usage
if __name__ == "__main__":
    # Initialize the DiagnosisChain class with your OpenAI API key

    diagnosis_chain = DiagnosisChain()

    # Example doctor's input
    doctor_input = "The patient is experiencing chest pain, shortness of breath, and dizziness."

    # Run the chain
    result = diagnosis_chain.run(doctor_input)

    # Print the structured JSON output
    print("Generated JSON response:")
    print(result)