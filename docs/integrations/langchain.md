# LangChain Integration

## Overview

The `LangChainCallback` tracks costs across all LLM calls in a LangChain chain or agent. Budget is checked *before* each LLM call and usage is logged *after*.

## Setup

```python
from langchain_openai import ChatOpenAI
from llm_toll import LangChainCallback

handler = LangChainCallback(project="my-chain", max_budget=10.0)
llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])

# All calls through this LLM instance are tracked
result = llm.invoke("Hello")
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `project` | `str` | `"default"` | Project name for grouping usage |
| `max_budget` | `float \| None` | `None` | Hard budget cap in USD |
| `store` | `BaseStore \| None` | `None` | Custom store instance (defaults to shared store) |
| `reporter` | `CostReporter \| None` | `None` | Custom reporter instance |

## Callback Methods

### `on_llm_start(serialized, prompts, **kwargs)`

Called before the LLM executes. If `max_budget` is set, checks the accumulated cost for the project and raises `BudgetExceededError` if the budget is exceeded.

### `on_llm_end(response, **kwargs)`

Called after a successful LLM completion. Extracts token usage from LangChain's `LLMResult.llm_output`:

- Model name from `llm_output["model_name"]`
- Input tokens from `llm_output["token_usage"]["prompt_tokens"]`
- Output tokens from `llm_output["token_usage"]["completion_tokens"]`

Calculates cost and logs usage to the store.

### `on_llm_error(error, **kwargs)`

Called after a failed LLM call. No-op -- failed calls are not tracked.

## Budget Enforcement

Unlike the LiteLLM callback, the LangChain callback checks budget **before** each LLM call:

```python
handler = LangChainCallback(project="my-chain", max_budget=5.0)
llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])

try:
    result = llm.invoke("Hello")
except BudgetExceededError as e:
    print(f"Budget exceeded: ${e.current_cost:.4f} >= ${e.max_budget:.4f}")
```

## With LangChain Chains

```python
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from llm_toll import LangChainCallback

handler = LangChainCallback(project="summarizer", max_budget=10.0)
llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])

prompt = ChatPromptTemplate.from_template("Summarize: {text}")
chain = prompt | llm

result = chain.invoke({"text": "Long document here..."})
```

## With LangChain Agents

```python
from langchain_openai import ChatOpenAI
from langchain.agents import create_react_agent
from llm_toll import LangChainCallback

handler = LangChainCallback(project="agent", max_budget=20.0)
llm = ChatOpenAI(model="gpt-4o", callbacks=[handler])

# All LLM calls made by the agent are tracked
agent = create_react_agent(llm, tools, prompt)
```

Every LLM invocation within the agent's reasoning loop is tracked and counts toward the budget.
