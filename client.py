from ollama import Client
import time
import ollama
import httpx

SERVER_URL = 'http://127.0.0.1:11434'
client = Client(host=SERVER_URL, timeout = 10.0)

questions = [
  "What's today's date?",
  "Tell me a joke.",
  "Can you tell me the weather today?",
  "Can you remind me to take my medicine at 11:00 AM?"
]

# CHUNK MANAGEMENT
MAX_QUESTION_LENGTH = 20

# BARGE-IN
BARGE_IN = False
INTERRUPTION_SECONDS = 0.5

# LATENCY DATA STORED IN TUPLE
latency = []

# ERROR MANAGMENT
ENABLE_SERVER_ERROR = False

def reply(response):
    # To simplify things, treat print as a TTS reply
    print(response.strip())

# Added func here, a callback function so we can easily change what we want Alva
# to do with the response like speak it or print it
# Added cancel callback to give ROS 2 an option to interrupt LLM gen
def ask(question, func=reply, cancel=lambda: False):
    stream = None
    try:
        if ENABLE_SERVER_ERROR:
            # SERVER ERROR SIMULATION
            raise ollama.ResponseError("Server Error", status_code=500)

        # LATENCY CHECKS
        start = time.perf_counter()
        time_to_first_token = None
        time_to_first_speakable_chunk = None
        stream = client.chat(
            model='qwen2.5:1.5b',
            messages=[{'role': 'user', 'content': question}],
            stream=True,
        )

        print("question: " + question)

        response = ''

        # combine the chunks of messages from the stream
        print("response: ")
        for chunk in stream:
            # Token time
            if time_to_first_token is None:
                time_to_first_token = time.perf_counter() - start

            # Apply barge in    
            if cancel() or (BARGE_IN and barge_in(start)):
                stream.close()
                return

            response += chunk.message.content

            # If it ends with '.', '?', or '!', we reply (TTS)
            if response.endswith(('.', '?', '!')):
                if time_to_first_speakable_chunk is None:
                    time_to_first_speakable_chunk = time.perf_counter() - start
                func(response)
                # reset result
                response = ''
            # If we exceed MAX_QUESTION_LENGTH, we need to split the sentence into multiple pieces
            elif len(response.split()) > MAX_QUESTION_LENGTH:
                words = response.split()
                if time_to_first_speakable_chunk is None:
                    time_to_first_speakable_chunk = time.perf_counter() - start
                # Reply for first half
                func(' '.join(words[:MAX_QUESTION_LENGTH]))
                # Store the second half for future chunks
                response = ' '.join(words[MAX_QUESTION_LENGTH:])

        # If we still have stuff need to be said
        if response.strip():
            if time_to_first_speakable_chunk is None:
                time_to_first_speakable_chunk = time.perf_counter() - start
            func(response)

        print(f"TIME TO FIRST TOKEN: {time_to_first_token}")
        print(f"TIME TO FIRST SPEAKABLE CHUNK: {time_to_first_speakable_chunk}")
        latency.append((time_to_first_token, time_to_first_speakable_chunk))
    except ollama.ResponseError as e:
        # reply is for Alva to speak about the error
        # print is for developers to see error code
        func("ERROR: PLEASE CONTACT SUPPORT, SERVERS ARE DOWN!")
        print('Server Error:', e.status_code)
    except httpx.TimeoutException as e:
        func("ERROR: PLEASE CONTACT SUPPORT, SERVER TIMEOUT!")
        print('Timeout:', e)
    except httpx.ConnectError as e:
        func("ERROR: PLEASE CONTACT SUPPORT, CONNECTION ERROR!")
        print('Connection Error:', e)
    finally:
        # make sure the stream closes at the end
        if stream is not None:
            stream.close()

def barge_in(start):
    # Interruption Simulation
    # barge in after INTERRUPTION_SECONDS delay
    if (time.perf_counter() - start) > INTERRUPTION_SECONDS:
        print("BARGE-IN ENABLED! USER HAS INTERRUPTED!")
        return True
    else:
        return False

for question in questions:
    ask(question)

print("LATENCY REPORT: (time_to_first_token, time_to_first_speakable_chunk)")
print(latency)