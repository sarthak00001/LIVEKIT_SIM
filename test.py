from litellm import completion

response = completion(
    model="anthropic/claude-3-sonnet-20240229",
    messages=[{"role": "user", "content": "hello"}],
)

print(response)