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
        temperature: float = 0.2,
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
    
    media_dir = 'medias'
    results_dir = 'results'
    for filename in os.listdir(media_dir):
        if filename.endswith('.json'):
            filepath = os.path.join(media_dir, filename)
            print(f"Opening {filepath}")
            with open(filepath, 'r') as file:
                data = json.load(file)
                # print(f"Loaded data: {data}")
                obj = data.get("obj", {})
                objectId = obj.get("id", "")
                tUrl = obj.get("transcriptPath", "")
                print(f"Extracted objectId: {objectId}, transcriptPath: {tUrl}")
            
            if not tUrl:
                print("Transcript URL not found in response.json")
                continue
            
            # Fetch the transcript from the URL
            print(f"Fetching transcript from URL: {tUrl}")
            response = requests.get(tUrl)
            if response.status_code == 200:
                transcript_data = response.json()
                results = transcript_data.get("results", [])
                # print(f"Fetched transcript data: {transcript_data}")
                text = results.get("transcript", "")
            else:
                print(f"Failed to fetch transcript from {tUrl}, status code: {response.status_code}")
                text = ""

            if not text:
                print("Transcript not found in the fetched data")
                continue
            
            
            messages = [
                {
                    "role": "system",
                    "content": "You excel at generating a summarized script for a short video generation service."
                },
                {
                    "role": "user",
                    "content": (
                        f"Generate a 50-second video script using only the relevant content from the following "
                        f"transcript (which is from a very lengthy video): {text} "
                        "The generated script must be deterministic, well-directed, and illustrative, covering all key points. "
                        "Make sure the final script is between 15 and 50 seconds. "
                        "The script should consist of speech only—exclude anything that's not spoken dialogue."
                    )
                }
            ]

            # Non-streaming response
            print("Generating response from ChatGPT")
            response = client.get_chat_response(messages)
            # print(f"Generated response: {response}")

            # Save response and objectId in result.json
            result = {
                "objectId": objectId,
                "response": response
            }
            result_filepath = os.path.join(results_dir, f'result_{filename}')
            with open(result_filepath, 'w') as result_file:
                json.dump(result, result_file, indent=4)
            print(f"Saved response and objectId in {result_filepath}")
            
            