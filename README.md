Streaming Layer Setup:
- Install Python 3.10+
- Install Ollama
pip install ollama
- Download OLLAMA MODEL: qwen2.5:1.5b
ollama pull qwen2.5:1.5b
- Run ollama in background
Local servers on http://127.0.0.1:11434
- Can change this address if running on diff device
- Run client
python client.py

General Notes:
https://github.com/ollama/ollama-python
- Will being using the Custom Client
- Design as if seperate since I'm using one machine
- Change the SERVER_URL if on another device
- OLLAMA MODEL: qwen2.5:1.5b

Transport Layer:
I will be using HTTP Streaming. Ollama's REST API supports this:
https://docs.ollama.com/capabilities/streaming
- Seems like the easiest way to support streaming

Speakable Chunk Issue:
- I'm going to start off with the assumption that the average sentence spoken
or question asked is 15-20 words long to keep things simple.
- Chunk is ready if we hit a '.', '?', '!'
- If it goes beyond 20 words, we split it into 2

Barge-In Support:
- HOW TO ENABLE:
BARGE_IN = True
INTERRUPTION_SECONDS = 0.5
- I've implemented a very basic barge in feature
- I used INTERRUPTION_SECONDS as a way to simulate a user interrupting the AI after a certain
amount of seconds
- After this is triggered, the Stream closes, the response stops generating, and the
server stops generation

Latency Measurement:
- HOW TO ENABLE:
ENABLE_SERVER_ERROR = False
BARGE_IN = False

- I implemented a timer to keep track of how long it takes for the time_to_first_token
and time_to_first_speakable_chunk each at different times of streaming
- time_to_first_token: time between model token request and first streamed event
- time_to_first_speakable_chunk: time between first model token request and first chunk ready to be spoken by TTS
- At the end, a list is generated with tuples (time_to_first_token, time_to_first_speakable_chunk) from each question

Handle Failure:
- HOW TO ENABLE:
ENABLE_SERVER_ERROR = True
- Failure: Slower/unreachable server
- Return a message for the user when this occurs.
- 3 types of failures accounted for:
1. Server Response Error:
- Ollama servers cannot be reached
2. Timeout Error
- Time exceeded 10s, timeout
3. Connection Error
- Cannot establish connection