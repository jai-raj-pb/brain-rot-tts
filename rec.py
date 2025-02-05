import os
import json
import requests
from openai import OpenAI
from typing import Generator, Optional
from dotenv import load_dotenv

load_dotenv()

class ChatGPTClient:
    def __init__(self):
        self.client = OpenAI(
            api_key=os.getenv('OPENAI_API_KEY')  # Use environment variables for API keys
        )
    
    def get_chat_response(
        self,
        messages: list[dict[str, str]],
        model: str = "gpt-4",
        temperature: float = 0.5,
        max_tokens: Optional[int] = None,
        stream: bool = False
    ) -> Generator[str, None, None] | str:
        """
        Get response from ChatGPT API
        """
        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=stream
            )
            
            if stream:
                return self._handle_stream_response(response)
            return self._handle_normal_response(response)
        
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def _handle_normal_response(self, response) -> str:
        return response.choices[0].message.content.strip()

    def _handle_stream_response(self, response) -> Generator[str, None, None]:
        for chunk in response:
            content = chunk.choices[0].delta.content
            if content is not None:
                yield content

if __name__ == "__main__":
    client = ChatGPTClient()
    
    results_dir = 'results'
    
    big_string = ""
    for filename in os.listdir(results_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(results_dir, filename)
            print(f"Opening {filepath}")
            with open(filepath, 'r') as file:
                data = json.load(file)
                objectId = data.get("objectId", "")
                script = data.get("response", "")
                big_string = big_string + "objectId: " + objectId + "\t<script-start>" + script + "<script-end>"
                
    # ask chatgpt to recommend 3 scripts for each script
    messages = [
        {"role": "system", "content": "You are a script recommendation expert given several scripts"},
        {"role": "user", "content": "<data-start> " + big_string + "<data-end> from the given data recommend 3 scripts for each script in following format: objectIdx: [recommendedObjectId1, recommendedObjectId2, recommendedObjectId3]"},
    ]
    
    response = client.get_chat_response(messages)
    print(response)
            
            