

from openai import OpenAI
 
# pip install openai 
# if you saved the key under a different environment variable name, you can do something like:
client = OpenAI(
  api_key="Your_API_KEY", 

)

command = '''
[5:44 pm, 08/10/2025] Zoya: Haa
[5:59 pm, 08/10/2025] Zoya: Hh
[5:59 pm, 08/10/2025] Zoya: Bolo
[6:04 pm, 08/10/2025] Safdar Ansari: hh
[6:04 pm, 08/10/2025] Safdar Ansari: kha ho
[6:04 pm, 08/10/2025] Zoya: Library
[6:14 pm, 08/10/2025] Zoya: H
[6:14 pm, 08/10/2025] Zoya: Where you
[6:18 pm, 08/10/2025] Safdar Ansari: hh
[6:22 pm, 08/10/2025] Zoya: Jii
[6:17 pm, 14/10/2025] Safdar Ansari: Hii
[6:17 pm, 14/10/2025] Zoya: Yes
'''
completion = client.chat.completions.create(
  model="gpt-3.5-turbo",
  messages=[
    {"role": "system", "content": "You are a person named safdar ansari who speaks hindi as well as english. He is from India and is a coder. You analyze chat history and respond like safdar ansari"},
    {"role": "user", "content": command}
  ]
)

print(completion.choices[0].message.content)


