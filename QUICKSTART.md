# Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Run the Test Suite

Verify everything works without API keys:

```bash
python test_system.py
```

You should see:
```
ALL TESTS PASSED ✅
System is ready for use!
```

### Step 3: Start Jupyter

```bash
jupyter notebook
```

### Step 4: Open the Notebooks

1. **Day 1**: `day1_foundations_and_triage.ipynb`
   - Multi-agent fundamentals
   - 3-agent incident triage system
   - Hands-on exercises

2. **Day 2**: `day2_advanced_patterns_and_rca.ipynb`
   - Advanced patterns
   - 5-agent root cause analysis system
   - Production guardrails

### Step 5: Run All Cells

Both notebooks work **out-of-the-box** with MockLLM (no API key needed).

---

## 🔑 Optional: Use Real LLMs

To use OpenAI instead of MockLLM:

### 1. Create `.env` file

```bash
cp .env.example .env
```

### 2. Edit `.env` and add your API key

```
OPENAI_API_KEY=sk-your-actual-key-here
OPENAI_MODEL=gpt-4o-mini
```

### 3. Restart Jupyter

The system will automatically detect the API key and use OpenAI.

---

## 📁 Project Structure

```
.
├── day1_foundations_and_triage.ipynb    # Day 1 lab
├── day2_advanced_patterns_and_rca.ipynb # Day 2 lab
├── test_system.py                       # Verification tests
├── requirements.txt                     # Dependencies
├── README.md                            # Full documentation
├── QUICKSTART.md                        # This file
├── .env.example                         # Environment template
├── src/
│   ├── llm/                            # LLM infrastructure
│   │   ├── mock_llm.py                 # MockLLM (no API needed)
│   │   ├── openai_llm.py               # OpenAI wrapper
│   │   └── llm_factory.py              # Auto-detection
│   ├── agents/                         # Agent framework
│   │   ├── base_agent.py               # Agent base class
│   │   ├── communication.py            # Message passing
│   │   └── orchestrator.py             # Workflow coordination
│   └── utils/                          # Utilities
│       ├── log_parser.py               # Log parsing
│       └── metrics.py                  # Performance tracking
└── data/
    ├── sample_incidents.json           # Sample incidents
    └── sample_logs.txt                 # Sample logs
```

---

## 🎯 What You'll Build

### Day 1: Incident Triage System
- **Classifier Agent**: Assigns severity (P0-P4) and category
- **Deduplication Agent**: Finds similar incidents
- **Router Agent**: Routes to appropriate team

### Day 2: Root Cause Analysis System
- **Log Parser Agent**: Extracts structured data
- **Pattern Detector Agent**: Identifies anomalies
- **Correlation Agent**: Links related events
- **Hypothesis Agent**: Generates RCA hypotheses
- **Validator Agent**: Validates against evidence

---

## 🔒 Security Note

**IMPORTANT**: The OpenAI API key you provided in your request has been **intentionally excluded** from all files. 

✅ **What we did**:
- NO hardcoded API keys anywhere in the code
- `.env.example` contains only placeholders
- `.env` is in `.gitignore` (never committed)
- All notebooks work without any API key
- System auto-detects and falls back to MockLLM

✅ **To use your API key safely**:
1. Create `.env` file (not tracked by git)
2. Add your key to `.env` only
3. Never commit `.env` to version control

---

## 🧪 Testing

Run the test suite anytime:

```bash
python test_system.py
```

This verifies:
- ✅ MockLLM works correctly
- ✅ All agents function properly
- ✅ Workflows execute successfully
- ✅ Both Day 1 and Day 2 systems operational

---

## 💡 Tips

1. **Start with MockLLM**: Understand the architecture without API costs
2. **Complete exercises**: Each notebook has 3 hands-on exercises
3. **Experiment**: Modify agents, add new ones, try different workflows
4. **Use real LLMs**: Enable OpenAI for production-quality responses
5. **Check the code**: Explore `src/` to understand implementation

---

## 🐛 Troubleshooting

### "ModuleNotFoundError: No module named 'src'"
Run Jupyter from the project root directory.

### "Cannot import name 'get_llm'"
Make sure you installed dependencies: `pip install -r requirements.txt`

### Notebooks show "Running with MockLLM"
This is normal! To use OpenAI, set up `.env` with your API key.

---

## 📚 Next Steps

1. ✅ Complete Day 1 notebook
2. ✅ Complete Day 2 notebook
3. ✅ Try the exercises
4. ✅ Adapt to your use cases
5. ✅ Deploy to production (follow deployment checklist in Day 2)

---

## 🤝 Support

- **Documentation**: See `README.md` for detailed information
- **Code**: All source code is in `src/` with comments
- **Examples**: Sample data in `data/` directory

---

## 🎉 You're Ready!

Everything is set up and tested. Start with Day 1 and enjoy building multi-agent systems!

```bash
jupyter notebook day1_foundations_and_triage.ipynb
```
