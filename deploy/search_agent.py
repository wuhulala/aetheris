# pip install -qU "langchain[anthropic]" to call the model
from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from pydantic import SecretStr


def get_weather(city: str) -> str:
    """Get weather for a given city."""
    return f"It's always sunny in {city}!"


def get_local_time(city: str) -> str:
    """Get the local time."""
    return datetime.now().strftime(f"{city} time now is {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


llm_mode = ChatOpenAI(
    base_url="http://chat.agihome.com/api/",
    api_key=SecretStr("sk-f67756b5674f46da94a80e79b7bc3cf1"),
    model="qwen3:8b"
    # model="function-calls-qwen3"
)
agent = create_react_agent(
    model=llm_mode,
    tools=[get_weather, get_local_time],
    prompt="You are a helpful assistant"
)

max_iterations = 3
recursion_limit = 2 * max_iterations + 1
agent_with_recursion_limit = agent.with_config(recursion_limit=recursion_limit)

for chunk in agent.stream(
        input={"messages": [{
            "role": "user",
            "content": "what is the weather in sf"
        }]},
        stream_mode="updates"):
    print(chunk)

# print(result)
