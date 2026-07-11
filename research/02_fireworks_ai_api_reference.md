# Fireworks AI API - Complete Reference for AMD Hackathon

## Base Configuration
```
Base URL:  https://api.fireworks.ai/inference/v1
Auth:      Bearer token via FIREWORKS_API_KEY
```

Fireworks AI provides 1:1 OpenAI-compatible API. Use the standard OpenAI Python SDK.

## Basic Python Setup
```python
from openai import OpenAI
import os

client = OpenAI(
    base_url=os.environ.get("FIREWORKS_BASE_URL", "https://api.fireworks.ai/inference/v1"),
    api_key=os.environ.get("FIREWORKS_API_KEY"),
)

response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[{"role": "user", "content": "Hello!"}],
)
print(response.choices[0].message.content)
```

## Available Models on AMD Hardware

### Small/Fast Models (for routing, classification, cheap inference)
| Model | Model ID | Size |
|-------|----------|------|
| Llama 3 8B Instruct | accounts/fireworks/models/llama-v3-8b-instruct | 8B |
| Llama 3.1 8B Instruct | accounts/fireworks/models/llama-v3p1-8b-instruct | 8B |
| Llama 3.2 3B Instruct | accounts/fireworks/models/llama-v3p2-3b-instruct | 3B |
| Mistral 7B Instruct v0.3 | accounts/fireworks/models/mistral-7b-instruct-v0-3 | 7B |
| DeepSeek V4 Flash | accounts/fireworks/models/deepseek-v4-flash | ~20B |

### Large Reasoning Models
| Model | Model ID | Size |
|-------|----------|------|
| DeepSeek V4 Pro | accounts/fireworks/models/deepseek-v4-pro | Large |
| DeepSeek V3 | accounts/fireworks/models/deepseek-v3 | 671B MoE |
| DeepSeek R1 | accounts/fireworks/models/deepseek-r1 | 671B MoE |
| Llama 3.1 70B Instruct | accounts/fireworks/models/llama-v3p1-70b-instruct | 70B |
| Llama 3.3 70B Instruct | accounts/fireworks/models/llama-v3p3-70b-instruct | 70B |
| Qwen 2.5 72B Instruct | accounts/fireworks/models/qwen2p5-72b-instruct | 72B |
| Qwen 3 235B A22B | accounts/fireworks/models/qwen3-235b-a22b | 235B MoE |

## Pricing (per 1M tokens)
| Model | Input $/1M | Output $/1M |
|-------|-----------|------------|
| GPT-OSS-20B | $0.070 | $0.300 |
| DeepSeek V4 Flash | $0.140 | $0.280 |
| Small models (8B) | ~$0.20 | ~$0.20 |
| DeepSeek V4 Pro | $1.740 | $3.480 |

## Structured Outputs (JSON)
```python
response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-70b-instruct",
    messages=[{"role": "user", "content": "Generate data"}],
    response_format={"type": "json_object"}
)
```

## Token Usage Tracking
```python
response = client.chat.completions.create(
    model="accounts/fireworks/models/llama-v3p1-8b-instruct",
    messages=[{"role": "user", "content": "Hello"}],
)
print(response.usage.prompt_tokens)
print(response.usage.completion_tokens)
print(response.usage.total_tokens)
```

## Key Parameters
- context_length_exceeded_behavior: "truncate" or "error"
- perf_metrics_in_response: true for performance metrics
- temperature: 0.0-0.3 recommended for structured outputs
- max_tokens: control output length
