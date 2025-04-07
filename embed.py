import openai

client = openai.OpenAI(
    base_url="https://api.sambanova.ai/v1/",
    api_key="2e1477b9-1043-4aa7-9726-47f6f62e0d7d",
)

response = client.embeddings.create(
    model="E5-Mistral-7B-Instruct",
    input="The quick brown fox jumps over the lazy dog"
)

print(response)