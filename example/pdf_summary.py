from pypdf import PdfReader
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from loguru import logger
from dotenv import load_dotenv
import os
import sys
import httpx
load_dotenv()

class PdfSummarizer:
    def __init__(self, model_name: str = None, api_key: str = None, base_url: str = None):
        """
        Initialize the PDF summarizer with LLM configuration

        Args:
            model_name: OpenAI model name (e.g., "gpt-4")
            api_key: OpenAI API key
            base_url: OpenAI API base URL
        """
        self.model_name = model_name or os.getenv("LLM_MODEL")
        self.api_key = api_key or os.getenv("LLM_API_KEY")
        self.base_url = base_url or os.getenv("LLM_BASE_URL")

        # Configure logger
        logger.add(sys.stdout,
                  format="{time} {message}",
                  filter="client",
                  level="DEBUG")
        self._patch_httpx()
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=self.model_name,
            openai_api_key=self.api_key,
            openai_api_base=self.base_url,
            max_tokens=1024
        )

        # Define prompt template
        self.prompt_template = """
        Please summarize the following content:
        {pdf_text}
        Summary:
        """
        
        self.prompt = PromptTemplate(
            input_variables=["pdf_text"],
            template=self.prompt_template,
        )

        # Create chain
        self.chain = self.prompt | self.llm

    def _patch_httpx(self):
        """Patch httpx to disable SSL verification"""
        original_init = httpx.Client.__init__
        def patched_init(self, *args, **kwargs):
            kwargs['verify'] = False
            original_init(self, *args, **kwargs)
        httpx.Client.__init__ = patched_init
    def extract_text(self, file_path: str) -> str:
        """
        Extract text from PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Extracted text as string
        """
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text

    def summarize(self, file_path: str) -> str:
        """
        Summarize the content of a PDF file
        
        Args:
            file_path: Path to PDF file
            
        Returns:
            Generated summary as string
        """
        pdf_text = self.extract_text(file_path)
        logger.debug(f"PDF content length: {len(pdf_text)} characters")
        
        result = self.chain.invoke({"pdf_text": pdf_text})
        return result.content

    @staticmethod
    def print_summary(summary: str):
        """Helper method to print summary with separator"""
        print("-" * 80)
        print("PDF summary:\n", summary)
        print("-" * 80)


# Usage example
if __name__ == "__main__":
    summarizer = PdfSummarizer()
    summary = summarizer.summarize("gst-dynamic-pipeline.pdf")
    summarizer.print_summary(summary)