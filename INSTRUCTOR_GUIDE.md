# Instructor Guide: Advanced Multi-Agent AI Systems Training

## 🎓 Course Overview

This guide helps instructors deliver the two-day multi-agent AI systems training course effectively.

---

## 📋 Pre-Course Preparation

### 1 Week Before

- [ ] **Test the environment**
  ```bash
  pip install -r requirements.txt
  python test_system.py
  ```

- [ ] **Decide on LLM strategy**
  - Option A: Use MockLLM only (zero cost, deterministic)
  - Option B: Use real LLMs for demos (requires API key)
  - Option C: Hybrid (MockLLM for exercises, real LLM for demos)

- [ ] **Prepare API keys** (if using real LLMs)
  - Create `.env` file with `OPENAI_API_KEY`
  - Test with a few sample calls
  - Estimate costs: ~$0.001-0.003 per incident

- [ ] **Review notebooks**
  - Run all cells in both notebooks
  - Complete all exercises
  - Note any customizations needed

- [ ] **Prepare environment**
  - Ensure Jupyter works on presentation machine
  - Test screen sharing/projection
  - Verify internet connectivity (if using real LLMs)

### 1 Day Before

- [ ] **Send pre-work to students**
  - Installation instructions
  - `requirements.txt`
  - Link to repository
  - Request they run `test_system.py`

- [ ] **Prepare backup plan**
  - Offline copy of notebooks
  - Pre-run cell outputs (in case of issues)
  - MockLLM as fallback

---

## 📅 Day 1: Foundations & Incident Triage

### Session Structure (4 hours)

#### Part 1: Introduction (30 min)

**Objectives:**
- Set expectations
- Explain multi-agent concepts
- Motivate the use case

**Key Points:**
- Why single-agent systems fail for complex tasks
- Benefits of specialized agents
- Real-world incident management challenges

**Demo:**
- Show the final triage system in action
- Process 2-3 sample incidents
- Highlight agent collaboration

**Tips:**
- Start with a relatable incident story
- Use diagrams to explain architecture
- Emphasize production relevance

#### Part 2: LLM Infrastructure (20 min)

**Objectives:**
- Explain MockLLM vs real LLMs
- Show factory pattern
- Demonstrate cost tracking

**Key Points:**
- MockLLM enables testing without costs
- Deterministic vs probabilistic modes
- Automatic fallback mechanism

**Demo:**
- Show LLM initialization with/without API key
- Compare MockLLM and OpenAI responses
- Display usage statistics

**Tips:**
- Emphasize security (no hardcoded keys)
- Show `.env.example` vs `.env`
- Explain when to use each mode

#### Part 3: Agent Architecture (40 min)

**Objectives:**
- Understand Agent base class
- Learn about roles and state
- See execution history

**Key Points:**
- Agent = LLM + Role + System Prompt + State
- 10 predefined roles
- State management for stateful agents

**Demo:**
- Create a classifier agent
- Process an incident
- Show execution history

**Tips:**
- Live code the agent creation
- Show how system prompts affect behavior
- Demonstrate state updates

**Break (10 min)**

#### Part 4: Communication (30 min)

**Objectives:**
- Understand message passing
- Learn message bus architecture
- See priority queuing

**Key Points:**
- Agents communicate via messages
- Priority-based delivery
- Conversation tracking

**Demo:**
- Create message bus
- Send messages between agents
- Visualize message flow

**Tips:**
- Draw message flow on whiteboard
- Show priority ordering in action
- Explain when to use different priorities

#### Part 5: Building Triage System (60 min)

**Objectives:**
- Build complete 3-agent system
- Orchestrate workflow
- Process real incidents

**Key Points:**
- Classifier → Deduplicator → Router
- Workflow dependencies
- Shared context

**Demo:**
- Create all three agents
- Build workflow with orchestrator
- Process multiple incidents
- Show results

**Tips:**
- Build incrementally (one agent at a time)
- Test each agent before adding next
- Show how dependencies work
- Highlight error handling

**Break (10 min)**

#### Part 6: Hands-on Exercises (50 min)

**Exercise 1: Add Summarizer Agent (15 min)**
- Students add 4th agent
- Integrate into workflow
- Generate summary reports

**Exercise 2: Priority-Based Routing (15 min)**
- Modify router with custom logic
- Route based on severity
- Test with different incidents

**Exercise 3: Batch Processing (20 min)**
- Process all 10 incidents
- Collect metrics
- Generate summary report

**Instructor Role:**
- Circulate and help students
- Answer questions
- Share solutions after each exercise
- Highlight interesting approaches

---

## 📅 Day 2: Advanced Patterns & RCA

### Session Structure (4 hours)

#### Part 1: Recap & Advanced Patterns (20 min)

**Objectives:**
- Recap Day 1 concepts
- Introduce hierarchical systems
- Preview evidence-based reasoning

**Key Points:**
- Coordinator-worker pattern
- Evidence chains
- Production considerations

**Demo:**
- Quick demo of Day 1 triage system
- Show hierarchical architecture diagram
- Preview RCA system

**Tips:**
- Quick Q&A on Day 1 material
- Connect to Day 2 topics
- Set expectations for complexity

#### Part 2: Hierarchical Systems (30 min)

**Objectives:**
- Understand coordinator pattern
- Learn parallel execution
- See dynamic task allocation

**Key Points:**
- Coordinator manages workers
- Parallel vs sequential execution
- Performance benefits

**Demo:**
- Create coordinator agent
- Show parallel workflow
- Compare timing

**Tips:**
- Emphasize scalability benefits
- Show when to use hierarchical vs flat
- Discuss trade-offs

#### Part 3: Evidence-Based Reasoning (30 min)

**Objectives:**
- Learn evidence chain pattern
- Understand hypothesis validation
- See confidence scoring

**Key Points:**
- Evidence → Hypothesis → Validation
- All conclusions need evidence
- Confidence thresholds

**Demo:**
- Build evidence chain
- Add evidence items
- Generate and validate hypothesis

**Tips:**
- Emphasize importance for production
- Show examples of good/bad evidence
- Discuss confidence thresholds

**Break (10 min)**

#### Part 4: Building RCA System (60 min)

**Objectives:**
- Build 5-agent RCA system
- Process logs and metrics
- Generate RCA reports

**Key Points:**
- Log Parser → Pattern Detector → Correlator → Hypothesis → Validator
- Evidence-based reasoning
- Comprehensive RCA reports

**Demo:**
- Create all 5 agents
- Build complex workflow
- Process incident with logs
- Generate RCA report

**Tips:**
- Build incrementally
- Show log parsing utility first
- Demonstrate pattern detection
- Highlight evidence correlation
- Show complete RCA report

**Break (10 min)**

#### Part 5: Production Guardrails (30 min)

**Objectives:**
- Implement confidence scoring
- Add evidence validation
- Create audit trails

**Key Points:**
- Confidence thresholds
- Human-in-the-loop
- Rate limiting and circuit breakers
- Comprehensive logging

**Demo:**
- Extract confidence scores
- Validate evidence chains
- Show rate limiter in action
- Display audit trail

**Tips:**
- Emphasize safety first
- Show real production scenarios
- Discuss regulatory requirements
- Share war stories

#### Part 6: Advanced Exercises (50 min)

**Exercise 1: Add Metric Analysis (15 min)**
- Create metric analyzer agent
- Integrate into RCA workflow
- Analyze synthetic metrics

**Exercise 2: Parallel Execution (15 min)**
- Modify workflow for parallelism
- Measure performance improvement
- Compare sequential vs parallel

**Exercise 3: Multi-Incident Batch RCA (20 min)**
- Process 5 incidents
- Identify common patterns
- Generate batch summary

**Instructor Role:**
- Help with complex workflows
- Debug issues
- Share best practices
- Discuss production deployment

---

## 💡 Teaching Tips

### General Advice

1. **Start Simple**: Build complexity gradually
2. **Live Code**: Don't just show slides - write code
3. **Make Mistakes**: Show debugging process
4. **Encourage Questions**: Pause frequently
5. **Use Real Examples**: Share production stories
6. **Be Flexible**: Adjust pace based on audience

### Common Student Questions

**Q: Why not just use one powerful agent?**
A: Show example of context overflow, lack of specialization, debugging difficulty.

**Q: How do I know when to use multi-agent?**
A: Complex tasks, multiple expertise areas, need for modularity, parallel opportunities.

**Q: What about latency?**
A: Discuss trade-offs, show parallel execution, mention caching strategies.

**Q: How do I test this?**
A: Show MockLLM, unit tests, integration tests, explain testing strategy.

**Q: What about costs?**
A: Show cost tracking, discuss optimization, mention caching and batching.

**Q: How do I deploy this?**
A: Walk through deployment checklist, discuss infrastructure needs.

### Handling Different Skill Levels

**Beginners:**
- Spend more time on fundamentals
- Provide more guided exercises
- Offer additional examples
- Be patient with questions

**Advanced:**
- Move faster through basics
- Focus on advanced patterns
- Encourage experimentation
- Discuss edge cases

**Mixed:**
- Pair programming for exercises
- Provide optional advanced challenges
- Offer additional resources
- Use breakout sessions

---

## 🎯 Learning Objectives Checklist

By end of course, students should be able to:

### Day 1
- [ ] Explain multi-agent architecture benefits
- [ ] Create agents with specialized roles
- [ ] Implement message passing between agents
- [ ] Build workflow with orchestrator
- [ ] Process incidents through pipeline
- [ ] Handle errors and retries

### Day 2
- [ ] Design hierarchical agent systems
- [ ] Implement evidence-based reasoning
- [ ] Build complex 5-agent RCA system
- [ ] Add production guardrails
- [ ] Create audit trails
- [ ] Deploy safely to production

---

## 📊 Assessment Ideas

### Informal Assessment
- Observe exercise completion
- Review code quality
- Check understanding via questions
- Monitor participation

### Formal Assessment (Optional)
- **Project**: Build custom multi-agent system
- **Quiz**: Key concepts and patterns
- **Presentation**: Share use case design
- **Code Review**: Evaluate implementation

---

## 🔧 Troubleshooting

### Common Issues

**Issue: Jupyter won't start**
- Check Python version (3.8+)
- Verify installation: `pip list | grep jupyter`
- Try: `python -m jupyter notebook`

**Issue: Import errors**
- Ensure running from project root
- Check sys.path in notebook
- Verify requirements installed

**Issue: MockLLM not working**
- Check src/llm/__init__.py imports
- Verify no syntax errors
- Run test_system.py

**Issue: Slow performance**
- Expected with real LLMs (1-3s per call)
- Use MockLLM for exercises
- Consider caching responses

**Issue: Students stuck on exercises**
- Provide hints without full solution
- Pair students up
- Show similar example
- Offer to debug together

---

## 📈 Feedback Collection

### During Course
- Quick pulse checks after each section
- Ask for questions frequently
- Monitor body language and engagement
- Adjust pace as needed

### End of Day 1
- Quick survey (3-5 questions)
- What worked well?
- What needs improvement?
- Adjust Day 2 accordingly

### End of Course
- Comprehensive feedback form
- Rate each section
- Suggest improvements
- Capture use cases
- Request testimonials

---

## 🎁 Bonus Content

### If Time Permits

**Advanced Topics:**
- Custom agent roles
- Agent memory and context
- Multi-turn conversations
- Streaming responses
- Alternative LLM providers

**Production Topics:**
- Kubernetes deployment
- Monitoring and alerting
- Cost optimization
- A/B testing agents
- Continuous improvement

**Hands-on Challenges:**
- Build custom use case
- Optimize for performance
- Add new agent types
- Integrate with existing systems

---

## 📚 Additional Resources

### For Students
- Course repository with all code
- README.md for reference
- QUICKSTART.md for setup
- Sample data for practice

### For Instructors
- This guide
- Slide deck (if created)
- Additional exercises
- Real-world case studies

---

## 🎉 Post-Course Follow-up

### Immediately After
- [ ] Share course materials
- [ ] Send feedback survey
- [ ] Provide certificate (if applicable)
- [ ] Share additional resources

### 1 Week Later
- [ ] Check in on progress
- [ ] Answer follow-up questions
- [ ] Share advanced resources
- [ ] Invite to community/forum

### 1 Month Later
- [ ] Request use case updates
- [ ] Gather success stories
- [ ] Offer advanced session
- [ ] Collect testimonials

---

## 📞 Instructor Support

### Before Course
- Review all materials thoroughly
- Run through exercises yourself
- Test with real LLMs if using
- Prepare backup plans

### During Course
- Stay flexible and adaptive
- Encourage participation
- Create safe learning environment
- Have fun!

### After Course
- Reflect on what worked
- Update materials based on feedback
- Share learnings with other instructors
- Celebrate success!

---

## ✅ Final Checklist

### Day Before
- [ ] Environment tested
- [ ] Notebooks reviewed
- [ ] API keys ready (if needed)
- [ ] Backup plan prepared
- [ ] Materials printed/shared
- [ ] Room/setup confirmed

### Day Of
- [ ] Arrive early
- [ ] Test projection/screen share
- [ ] Verify internet (if needed)
- [ ] Welcome students
- [ ] Set expectations
- [ ] Have fun teaching!

---

**Good luck with your training! You've got this! 🚀**

Remember: The goal is not perfection, but learning. Create a supportive environment where students feel comfortable experimenting and making mistakes. That's where the real learning happens.
