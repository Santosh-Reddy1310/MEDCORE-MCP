from dotenv import load_dotenv
load_dotenv('.env.local')
import os
from groq import Groq

key = os.getenv('GROQ_API_KEY')
key2 = os.getenv('GROQ_API_KEY_2')
print('Key 1:', key[:20] + '...' if key else 'NOT FOUND')
print('Key 2:', key2[:20] + '...' if key2 else 'NOT FOUND')

for label, k in [('GROQ_API_KEY', key), ('GROQ_API_KEY_2', key2)]:
    if not k:
        continue
    try:
        client = Groq(api_key=k)
        resp = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': 'say hello'}],
            max_tokens=10
        )
        print(f'{label}: OK - {resp.choices[0].message.content}')
    except Exception as e:
        print(f'{label}: FAILED - {e}')
