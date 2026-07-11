# AMD Developer Hackathon: ACT II - Complete Rules & Track Specifications

## Event Overview
- **Platform**: lablab.ai
- **Dates**: July 6-12, 2026
- **Focus**: AI Agents + High-Performance AI using AMD GPUs in the cloud
- **Tech Stack**: AMD Developer Cloud, ROCm open-source software stack, Fireworks AI API
- **Hardware**: AMD Instinct MI300X GPUs (192GB VRAM)
- **Prize Pool**: $10,000+ total ($5,000 first, $3,000 second, $2,000 third)

## Track 1: Hybrid Token-Efficient Routing Agent

### What the Submission Must Do
- Read a batch of tasks from `/input/tasks.json`
- Write structured responses to `/output/results.json`
- Build an intelligent routing agent that minimizes token usage and inference costs WITHOUT compromising answer quality

### tasks.json Input Schema
```json
[
  {
    "task_id": "unique_identifier_001",
    "category": "factual_knowledge",
    "instruction": "What is the primary architecture used by AMD Instinct GPUs?"
  },
  {
    "task_id": "unique_identifier_002",
    "category": "math",
    "instruction": "Solve for x: 2x + 10 = 30."
  },
  {
    "task_id": "unique_identifier_003",
    "category": "code_generation",
    "instruction": "Write a Python function to calculate the Fibonacci sequence."
  }
]
```

### 8 Task Categories
1. Factual knowledge
2. Mathematical reasoning
3. Sentiment classification
4. Text summarization
5. Named Entity Recognition (NER)
6. Code debugging
7. Logical/deductive reasoning
8. Code generation

### results.json Output Schema
```json
[
  {
    "task_id": "unique_identifier_from_input",
    "answer": "The generated response or solution for the task"
  }
]
```

### ALLOWED_MODELS Environment Variable
- Contains a comma-separated list of Fireworks AI model IDs injected at runtime
- Common models available:
  - accounts/fireworks/models/llama-v3p3-70b-instruct
  - accounts/fireworks/models/llama-v3p2-3b-instruct
  - accounts/fireworks/models/llama-v3p1-70b-instruct
  - accounts/fireworks/models/qwen2p5-72b-instruct
  - accounts/fireworks/models/qwen3-235b-a22b
- MUST be read dynamically at runtime, never hardcoded

### Token Efficiency Measurement
- Two-phase evaluation:
  1. Accuracy Gate: An LLM-judge evaluates each answer for correctness. Only submissions that PASS the accuracy gate proceed.
  2. Token Ranking: Passing submissions are then ranked by total token consumption (lower is better)
- Time constraints: ~30 seconds per task, ~10 minutes total runtime budget

### Evaluation Rubric
1. Accuracy (pass/fail gate via LLM judge)
2. Token Efficiency (primary ranking metric after accuracy gate)
3. Problem Understanding & Approach (how the routing strategy works)
4. Novelty & Impact (innovation of the routing approach)
5. Technical Feasibility (robustness, error handling)
6. Documentation (clear README explaining routing strategy)

## Track 2: Video Captioning Pipeline

### What the Submission Must Do
- Take a short video clip (30 seconds to 2 minutes) and generate 4 distinct captions:
  1. formal — Professional, factual, objective
  2. sarcastic — Dry, ironic, cynical humor
  3. humorous_tech — Funny with programming/tech/AI references
  4. humorous_non_tech — Everyday, relatable humor without jargon

### Output Format
```json
{
  "video_id": "unique_identifier_from_tasks_json",
  "captions": {
    "formal": "A factual, professional description.",
    "sarcastic": "A dry, ironic take.",
    "humorous_tech": "A humorous caption with tech jargon.",
    "humorous_non_tech": "A lighthearted, relatable caption."
  },
  "metadata": {
    "model_used": "e.g., qwen3p7-plus",
    "timestamp": "2026-07-11T00:00:00Z"
  }
}
```

## Track 3: Unicorn Track (Open-Ended)
- Creativity and Originality (PRIMARY)
- Product/Market Potential
- Overall Impact

## Docker Submission Requirements
- Architecture: linux/amd64 (MANDATORY)
- Public Docker Hub image
- Proper ENTRYPOINT/CMD
- Exit code 0 on success
- Environment variables injected: FIREWORKS_API_KEY, FIREWORKS_BASE_URL, ALLOWED_MODELS
- No hardcoded credentials
- ~30 seconds per-task timeout, ~10-minute total runtime budget

## Submission Materials
- Public GitHub repository with clear README
- Docker image on public registry
- Max 5-minute video demo (MP4)
- Slide deck (PDF)
- Cover image (16:9, PNG/JPG)
- Project title + description
