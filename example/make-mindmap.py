#!/usr/bin/env python3
import os
import argparse
import requests
import zlib
import base64
from typing import Optional, Literal, Union
from pathlib import Path
import subprocess
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser

def encode(plantuml_text):
    zlibbed_str = zlib.compress(plantuml_text.encode('utf-8'))
    compressed_string = zlibbed_str[2:-4]  # strip zlib headers
    return encode64(compressed_string)

def encode64(data):
    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    res = ''
    data = bytearray(data)
    i = 0
    while i < len(data):
        b1 = data[i]
        b2 = data[i+1] if i+1 < len(data) else 0
        b3 = data[i+2] if i+2 < len(data) else 0
        res += alphabet[(b1 >> 2) & 0x3F]
        res += alphabet[((b1 & 0x3) << 4 | (b2 >> 4) & 0xF) & 0x3F]
        res += alphabet[((b2 & 0xF) << 2 | (b3 >> 6) & 0x3) & 0x3F]
        res += alphabet[b3 & 0x3F]
        i += 3
    return res

class MindmapGenerator:
    """A class to generate PlantUML mindmaps from web content.
    
    This class fetches content from a URL, summarizes it using an LLM,
    and then converts the summary into a PlantUML mindmap diagram.
    It can also generate PNG images from the PlantUML diagrams using the PlantUML server API.
    """

    def __init__(self, output_file: str = "mindmap.puml", plantuml_server: str = "https://www.plantuml.com/plantuml"):
        """Initialize the MindmapGenerator.
        
        Args:
            output_file: Path to save the generated mindmap PlantUML file.
            plantuml_server: URL of the PlantUML server to use for image generation.
        """
        load_dotenv()

        # Initialize configuration
        self.output_file = output_file
        self.plantuml_server = plantuml_server.rstrip('/')
        
        # Get API configuration from environment variables
        api_key = os.getenv("LLM_API_KEY")
        base_url = os.getenv("LLM_BASE_URL")
        model_name = os.getenv("LLM_MODEL")
        
        if not api_key or not base_url or not model_name:
            raise ValueError("LLM_API_KEY or LLM_BASE_URL or LLM_MODEL environment variable is not set")
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            temperature=0,
            openai_api_key=api_key,
            openai_api_base=base_url,
            model=model_name
        )
        
        # Initialize the parser
        self.parser = StrOutputParser()
        
        # Create the summary chain
        summary_prompt = PromptTemplate(
            input_variables=["text"],
            template="Summarize this page content in key bullet points:\n\n{text}\n\nSummary:"
        )
        self.summary_chain = summary_prompt | self.llm | self.parser
        
        # Create the mindmap chain
        mindmap_prompt = PromptTemplate(
            input_variables=["summary"],
            template="""
            Generate a PlantUML mindmap diagram based on the following summary:
            {summary}

            Use this format:
            @startmindmap
            * Main Topic
            ** ...
            @endmindmap
            """
        )
        self.mindmap_chain = mindmap_prompt | self.llm | self.parser
    
    def fetch_content(self, url: str) -> str:
        """Fetch content from a URL.
        
        Args:
            url: The URL to fetch content from.
            
        Returns:
            The content of the URL as a string.
            
        Raises:
            Exception: If there's an error fetching the content.
        """
        try:
            print(f"Fetching {url}")
            response = requests.get(url, verify=False)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except Exception as e:
            print(f"Error fetching content: {e}")
            raise
    
    def generate_summary(self, content: str) -> str:
        """Generate a summary of the content.
        
        Args:
            content: The content to summarize.
            
        Returns:
            A summary of the content.
        """
        try:
            print("\n--- Summarizing ---")
            summary = self.summary_chain.invoke({"text": content})
            print(summary)
            return summary
        except Exception as e:
            print(f"Error generating summary: {e}")
            raise
    
    def generate_mindmap(self, summary: str) -> str:
        """Generate a PlantUML mindmap from a summary.
        
        Args:
            summary: The summary to convert to a mindmap.
            
        Returns:
            A PlantUML mindmap diagram as a string.
        """
        try:
            print(f"\n--- Generating Mindmap: {str}")
            mindmap = self.mindmap_chain.invoke({"summary": summary})
            print(mindmap)
            return mindmap
        except Exception as e:
            print(f"Error generating mindmap: {e}")
            raise
    
    def save_mindmap(self, mindmap: str) -> None:
        """Save the mindmap to a file.
        
        Args:
            mindmap: The PlantUML mindmap to save.
        """
        try:
            with open(self.output_file, "w") as f:
                f.write(mindmap)
            print(f"\nMindmap saved to {self.output_file}")
        except Exception as e:
            print(f"Error saving mindmap: {e}")
            raise


    def render_plantuml_image(self, puml_file: str):
        # download plantuml.jar：https://plantuml.com/download
        cmd = ["java", "-jar", "plantuml.jar", puml_file]
        #cmd = ["plantuml", puml_file]
        subprocess.run(cmd, check=True)

    def generate_image(self, plantuml_text: str, output_file: Optional[str] = None,
                      format: Literal["png", "svg", "pdf"] = "png") -> str:
        """Generate an image from PlantUML text using the PlantUML server API.
        
        Args:
            plantuml_text: The PlantUML diagram text.
            output_file: Path to save the generated image. If None, uses the base name of
                         self.output_file with the appropriate extension.
            format: The image format to generate (png, svg, or pdf).

        Returns:
            The path to the generated image file.
        """
        try:
            print(f"\n--- Generating {format.upper()} Image ---{plantuml_text}")

            
            # Encode the PlantUML text
            encoded = encode(plantuml_text)
            
            # Determine the output file path
            if output_file is None:
                # Use the base name of self.output_file with the appropriate extension
                base_path = Path(self.output_file).with_suffix(f'.{format}')
                output_file = str(base_path)
            
            # Construct the URL for the PlantUML server
            url = f"{self.plantuml_server}/{format}/{encoded}"
            
            # Fetch the image from the PlantUML server
            print(f"Fetching image from {url}")
            response = requests.get(url)
            response.raise_for_status()
            
            # Save the image to a file
            with open(output_file, "wb") as f:
                f.write(response.content)
                
            print(f"Image saved to {output_file}")
            return output_file
        except Exception as e:
            print(f"Error generating image: {e}")
            raise
    
    def generate_from_url(self, url: str, generate_image: bool = False,
                          image_format: Literal["png", "svg", "pdf"] = "png", 
                          image_output: Optional[str] = None) -> Union[str, tuple[str, str]]:
        """Generate a mindmap from a URL.
        
        This method combines all the steps: fetching content,
        generating a summary, creating a mindmap, and saving it.
        Optionally, it can also generate an image from the PlantUML diagram.
        
        Args:
            url: The URL to generate a mindmap from.
            generate_image: Whether to generate an image from the PlantUML diagram.
            image_format: The format of the image to generate (png, svg, or pdf).
            image_output: Path to save the generated image. If None, uses the base name of
                         self.output_file with the appropriate extension.
            
        Returns:
            If generate_image is False, returns the generated PlantUML mindmap as a string.
            If generate_image is True, returns a tuple of (mindmap, image_path).
        """

        if not os.path.exists(self.output_file):
            content = self.fetch_content(url)
            summary = self.generate_summary(content)
            mindmap = self.generate_mindmap(summary)
            self.save_mindmap(mindmap)
        else:
            with open(self.output_file, "r") as f:
                mindmap = f.read()

        if generate_image:
            #image_path = self.generate_image(mindmap, image_output, image_format)
            #return mindmap, image_path
            self.render_plantuml_image(self.output_file)

        return mindmap, self.output_file[:-5] + ".png"


def main():
    """Main function to run the mindmap generator from command line."""
    parser = argparse.ArgumentParser(description="Generate a PlantUML mindmap from a URL")
    parser.add_argument("url", help="URL to generate mindmap from")
    parser.add_argument(
        "-o", "--output", 
        default="mindmap.puml",
        help="Output file path (default: mindmap.puml)"
    )
    parser.add_argument(
        "-i", "--image",
        action="store_true",
        help="Generate an image from the PlantUML diagram"
    )
    parser.add_argument(
        "-f", "--format",
        choices=["png", "svg", "pdf"],
        default="png",
        help="Image format to generate (default: png)"
    )
    parser.add_argument(
        "-io", "--image-output",
        help="Output file path for the generated image (default: same as output with appropriate extension)"
    )
    parser.add_argument(
        "-s", "--server",
        default="https://www.plantuml.com/plantuml",
        help="PlantUML server URL (default: https://www.plantuml.com/plantuml)"
    )
    args = parser.parse_args()
    
    try:
        generator = MindmapGenerator(output_file=args.output, plantuml_server=args.server)
        result = generator.generate_from_url(
            args.url, 
            generate_image=args.image,
            image_format=args.format,
            image_output=args.image_output
        )
        
        print("\nMindmap generation completed successfully!")
        if args.image:
            _, image_path = result
            print(f"Image generated at: {image_path}")
    except Exception as e:
        print(f"\nError: {e}")
        return 1
    return 0


if __name__ == "__main__":
    # Example usage when run directly
    if len(os.sys.argv) == 1:  # No arguments provided, use example
        generator = MindmapGenerator()
        mindmap, image_path = generator.generate_from_url(
            "https://en.wikipedia.org/wiki/LangChain",
            generate_image=True,
            image_format="png"
        )
        print(f"Example image generated at: {image_path}")
    else:  # Arguments provided, use argparse
        exit(main())
