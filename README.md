# Advanced Multi-Agent AI Systems Training
## Two Half-Day Sessions for Support & Meta Engineers

This course teaches production-grade multi-agent systems for large-scale incident management, log analysis, and automated triage.

## 🎯 Target Audience
Support and meta engineers handling:
- Large-scale log & metric analysis
- Incident triage, deduplication, clustering
- Root cause analysis with evidence
- Policy/runbook/SLA compliance
- Safe automation with strict guardrails

## 📚 Course Structure

### Day 1: Foundations & Incident Triage (4 hours)
- Multi-agent architecture patterns
- Agent communication & coordination
- Building an automated incident triage system
- Hands-on: 3-agent triage pipeline

### Day 2: Advanced Patterns & Production RCA (4 hours)
- Hierarchical agent systems
- Evidence-based root cause analysis
- Guardrails & safety mechanisms
- Hands-on: 5-agent RCA system

## 🚀 Quick Start

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd advanced-multi-agent-ai-systems-2-half-days

# Install dependencies
pip install -r requirements.txt
```

### Running WITHOUT API Keys (Default)
The labs work out-of-the-box with **MockLLM** - no API keys required!

```bash
# Just start Jupyter
jupyter notebook
```

All notebooks will automatically use MockLLM with deterministic responses.

### Running WITH OpenAI (Optional)
To use real LLMs:

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your OpenAI API key:
```
OPENAI_API_KEY=sk-...your-actual-key...
OPENAI_MODEL=gpt-4o-mini
```

3. Start Jupyter:
```bash
jupyter notebook
```

The system will automatically detect the API key and use OpenAI.

## 🔒 Security & API Keys

**IMPORTANT**: This course follows security best practices:
- ✅ NO hardcoded API keys anywhere
- ✅ All keys read from environment variables only
- ✅ Automatic fallback to MockLLM if no key present
- ✅ `.env` file is gitignored
- ✅ Only `.env.example` is committed (with placeholders)

## 📓 Notebooks

1. **`day1_foundations_and_triage.ipynb`**
   - Multi-agent fundamentals
   - Communication patterns
   - 3-agent incident triage system
   - Exercises with real-world scenarios

2. **`day2_advanced_patterns_and_rca.ipynb`**
   - Hierarchical coordination
   - Evidence-based reasoning
   - 5-agent root cause analysis system
   - Production guardrails

## 🧪 MockLLM Features

The built-in MockLLM provides:
- **Deterministic mode** (default): Same inputs → same outputs
- **Probabilistic mode**: Controlled randomness for evaluation
- **Zero dependencies**: No API calls, no network
- **Same interface**: Drop-in replacement for real LLMs

## 📊 What You'll Build

### Day 1: Incident Triage System
- **Classifier Agent**: Categorizes incidents (P0-P4)
- **Deduplication Agent**: Finds similar incidents
- **Router Agent**: Routes to correct team

### Day 2: Root Cause Analysis System
- **Log Parser Agent**: Extracts structured data
- **Pattern Detector Agent**: Finds anomalies
- **Correlation Agent**: Links related events
- **Hypothesis Agent**: Generates RCA hypotheses
- **Validator Agent**: Validates against evidence

## 🎓 Learning Outcomes

After this course, you will:
- ✅ Design multi-agent systems for production incidents
- ✅ Implement agent communication & coordination
- ✅ Build evidence-based reasoning pipelines
- ✅ Apply guardrails for safe automation
- ✅ Handle large-scale log analysis with agents
- ✅ Deploy production-ready agent systems

## 🛠️ Project Structure

```
.
├── README.md
├── requirements.txt
├── .env.example
├── day1_foundations_and_triage.ipynb
├── day2_advanced_patterns_and_rca.ipynb
├── src/
│   ├── llm/
│   │   ├── mock_llm.py          # MockLLM implementation
│   │   ├── openai_llm.py        # OpenAI wrapper
│   │   └── llm_factory.py       # Factory pattern
│   ├── agents/
│   │   ├── base_agent.py        # Agent base class
│   │   ├── communication.py     # Message passing
│   │   └── orchestrator.py      # Coordination logic
│   └── utils/
│       ├── log_parser.py        # Log parsing utilities
│       └── metrics.py           # Evaluation metrics
└── data/
    ├── sample_incidents.json    # Sample incident data
    └── sample_logs.txt          # Sample log files
```

## 💡 Tips for Instructors

1. **Start with MockLLM**: Let students understand the architecture without API costs
2. **Switch to real LLMs**: For advanced exercises, enable OpenAI to show real behavior
3. **Cost control**: Use `gpt-4o-mini` (default) to minimize costs
4. **Exercises**: Each notebook has 3-5 hands-on exercises
5. **Time management**: Each half-day is designed for 4 hours (3h teaching + 1h exercises)

## 🐛 Troubleshooting

### "No module named 'src'"
Make sure you're running Jupyter from the project root directory.

### "API key not found" (when using OpenAI)
Check that:
1. `.env` file exists (not `.env.example`)
2. `OPENAI_API_KEY` is set in `.env`
3. The key starts with `sk-`

### Notebooks run but show "Running with MockLLM"
This is normal! MockLLM is the default. To use OpenAI, set up `.env` as described above.

## 📝 License

This training material is provided for educational purposes.

## 🤝 Contributing

Feedback and improvements welcome! Please open an issue or PR.
