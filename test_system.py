#!/usr/bin/env python3
"""
Test script to verify the multi-agent system works end-to-end without API keys.
This should run successfully with MockLLM (no OPENAI_API_KEY required).
"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.llm import get_llm, print_llm_stats
from src.agents import Agent, AgentRole, Orchestrator, WorkflowStep, MessageBus, Message, MessagePriority
from src.utils import LogParser, MetricsCollector

def test_llm_initialization():
    print("\n" + "="*60)
    print("TEST 1: LLM Initialization")
    print("="*60)
    
    llm = get_llm(force_mock=True, deterministic=True, verbose=True)
    
    response = llm.generate("Test prompt", temperature=0.3, max_tokens=100)
    
    assert response['model'] == 'MockLLM', "Should use MockLLM"
    assert 'response' in response, "Should have response"
    assert response['cost'] == 0.0, "MockLLM should have zero cost"
    
    print("✅ LLM initialization test passed")
    return llm

def test_agent_creation(llm):
    print("\n" + "="*60)
    print("TEST 2: Agent Creation")
    print("="*60)
    
    agent = Agent(
        name="TestAgent",
        role=AgentRole.CLASSIFIER,
        llm=llm
    )
    
    assert agent.name == "TestAgent"
    assert agent.role == AgentRole.CLASSIFIER
    assert len(agent.execution_history) == 0
    
    print("✅ Agent creation test passed")
    return agent

def test_agent_processing(agent):
    print("\n" + "="*60)
    print("TEST 3: Agent Processing")
    print("="*60)
    
    test_input = {
        "title": "Test Incident",
        "description": "Database connection timeout"
    }
    
    result = agent.process(test_input)
    
    assert 'agent' in result
    assert 'response' in result
    assert len(agent.execution_history) == 1
    
    print("✅ Agent processing test passed")

def test_message_bus():
    print("\n" + "="*60)
    print("TEST 4: Message Bus")
    print("="*60)
    
    bus = MessageBus()
    
    msg = Message(
        sender="Agent1",
        receiver="Agent2",
        content={"data": "test"},
        priority=MessagePriority.HIGH
    )
    
    msg_id = bus.send(msg)
    assert msg_id is not None
    
    messages = bus.receive("Agent2")
    assert len(messages) == 1
    assert messages[0].sender == "Agent1"
    
    print("✅ Message bus test passed")

def test_orchestrator(llm):
    print("\n" + "="*60)
    print("TEST 5: Orchestrator & Workflow")
    print("="*60)
    
    agent1 = Agent("Agent1", AgentRole.CLASSIFIER, llm)
    agent2 = Agent("Agent2", AgentRole.ROUTER, llm)
    
    orchestrator = Orchestrator("TestWorkflow")
    orchestrator.register_agent("agent1", agent1)
    orchestrator.register_agent("agent2", agent2)
    
    workflow = [
        WorkflowStep(name="step1", agent_name="agent1"),
        WorkflowStep(name="step2", agent_name="agent2", depends_on=["step1"])
    ]
    
    orchestrator.build_workflow(workflow)
    
    test_input = {"test": "data"}
    result = orchestrator.execute_workflow(test_input, verbose=False)
    
    assert result['status'] in ['COMPLETED', 'PARTIAL']
    assert result['steps_executed'] >= 1
    
    print("✅ Orchestrator test passed")

def test_triage_system(llm):
    print("\n" + "="*60)
    print("TEST 6: Incident Triage System (Day 1)")
    print("="*60)
    
    with open('data/sample_incidents.json', 'r') as f:
        incidents = json.load(f)
    
    classifier = Agent("Classifier", AgentRole.CLASSIFIER, llm)
    deduplicator = Agent("Deduplicator", AgentRole.DEDUPLICATOR, llm)
    router = Agent("Router", AgentRole.ROUTER, llm)
    
    orchestrator = Orchestrator("TriageWorkflow")
    orchestrator.register_agent("classifier", classifier)
    orchestrator.register_agent("deduplicator", deduplicator)
    orchestrator.register_agent("router", router)
    
    workflow = [
        WorkflowStep(name="classify", agent_name="classifier"),
        WorkflowStep(name="deduplicate", agent_name="deduplicator", depends_on=["classify"]),
        WorkflowStep(name="route", agent_name="router", depends_on=["classify", "deduplicate"])
    ]
    
    orchestrator.build_workflow(workflow)
    
    result = orchestrator.execute_workflow(incidents[0], verbose=False)
    
    assert result['status'] == 'COMPLETED'
    assert result['steps_executed'] == 3
    
    print("✅ Triage system test passed")

def test_rca_system(llm):
    print("\n" + "="*60)
    print("TEST 7: Root Cause Analysis System (Day 2)")
    print("="*60)
    
    with open('data/sample_incidents.json', 'r') as f:
        incidents = json.load(f)
    
    with open('data/sample_logs.txt', 'r') as f:
        logs = f.read()
    
    log_parser = Agent("LogParser", AgentRole.LOG_PARSER, llm)
    pattern_detector = Agent("PatternDetector", AgentRole.PATTERN_DETECTOR, llm)
    correlator = Agent("Correlator", AgentRole.CORRELATOR, llm)
    hypothesis_gen = Agent("HypothesisGen", AgentRole.HYPOTHESIS_GENERATOR, llm)
    validator = Agent("Validator", AgentRole.VALIDATOR, llm)
    
    orchestrator = Orchestrator("RCAWorkflow")
    orchestrator.register_agent("log_parser", log_parser)
    orchestrator.register_agent("pattern_detector", pattern_detector)
    orchestrator.register_agent("correlator", correlator)
    orchestrator.register_agent("hypothesis_gen", hypothesis_gen)
    orchestrator.register_agent("validator", validator)
    
    workflow = [
        WorkflowStep(name="parse", agent_name="log_parser"),
        WorkflowStep(name="detect", agent_name="pattern_detector", depends_on=["parse"]),
        WorkflowStep(name="correlate", agent_name="correlator", depends_on=["parse", "detect"]),
        WorkflowStep(name="hypothesize", agent_name="hypothesis_gen", depends_on=["correlate"]),
        WorkflowStep(name="validate", agent_name="validator", depends_on=["hypothesize"])
    ]
    
    orchestrator.build_workflow(workflow)
    
    rca_input = {
        'incident': incidents[0],
        'logs': logs
    }
    
    result = orchestrator.execute_workflow(rca_input, verbose=False)
    
    assert result['status'] == 'COMPLETED'
    assert result['steps_executed'] == 5
    
    print("✅ RCA system test passed")

def test_log_parser():
    print("\n" + "="*60)
    print("TEST 8: Log Parser Utility")
    print("="*60)
    
    with open('data/sample_logs.txt', 'r') as f:
        logs = f.read()
    
    parser = LogParser()
    entries = parser.parse_logs(logs)
    
    assert len(entries) > 0, "Should parse log entries"
    
    analysis = parser.analyze_logs(entries)
    assert 'total_entries' in analysis
    assert 'error_count' in analysis
    
    print(f"  Parsed {len(entries)} log entries")
    print(f"  Found {analysis['error_count']} errors")
    print("✅ Log parser test passed")

def test_metrics_collector():
    print("\n" + "="*60)
    print("TEST 9: Metrics Collector")
    print("="*60)
    
    collector = MetricsCollector()
    metric = collector.start_tracking("TestMetric")
    
    metric.record_metric("test_value", 42)
    metric.increment_counter("test_counter", 5)
    metric.record_timing("test_timing", 123.45)
    
    collector.stop_tracking()
    
    stats = collector.get_aggregate_stats()
    assert stats['total_metrics'] == 1
    
    print("✅ Metrics collector test passed")

def run_all_tests():
    print("\n" + "="*70)
    print("MULTI-AGENT AI SYSTEMS - END-TO-END TEST SUITE")
    print("="*70)
    print("\nTesting with MockLLM (no API key required)")
    
    try:
        llm = test_llm_initialization()
        agent = test_agent_creation(llm)
        test_agent_processing(agent)
        test_message_bus()
        test_orchestrator(llm)
        test_triage_system(llm)
        test_rca_system(llm)
        test_log_parser()
        test_metrics_collector()
        
        print("\n" + "="*70)
        print("ALL TESTS PASSED ✅")
        print("="*70)
        
        print("\nLLM Usage Statistics:")
        print_llm_stats(llm)
        
        print("\n✅ System is ready for use!")
        print("   - All components working correctly")
        print("   - MockLLM functioning as expected")
        print("   - Both Day 1 and Day 2 systems operational")
        print("\nYou can now:")
        print("   1. Run the Jupyter notebooks")
        print("   2. Optionally set up .env with OPENAI_API_KEY for real LLMs")
        print("   3. Start building your own multi-agent systems!")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
