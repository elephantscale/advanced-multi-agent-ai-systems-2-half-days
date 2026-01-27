from typing import Dict, Any, List, Optional, Callable
from enum import Enum
from datetime import datetime
from dataclasses import dataclass
import json


class WorkflowStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class WorkflowStep:
    name: str
    agent_name: str
    depends_on: List[str] = None
    condition: Optional[Callable] = None
    retry_count: int = 0
    max_retries: int = 3
    
    def __post_init__(self):
        if self.depends_on is None:
            self.depends_on = []


class Orchestrator:
    
    def __init__(self, name: str = "MainOrchestrator"):
        self.name = name
        self.agents: Dict[str, Any] = {}
        self.workflow_steps: List[WorkflowStep] = []
        self.execution_results: Dict[str, Any] = {}
        self.step_status: Dict[str, WorkflowStatus] = {}
        self.execution_history: List[Dict[str, Any]] = []
        self.shared_context: Dict[str, Any] = {}
    
    def register_agent(self, agent_name: str, agent: Any):
        self.agents[agent_name] = agent
        print(f"✓ Registered agent: {agent_name} ({agent.role.value})")
    
    def add_workflow_step(self, step: WorkflowStep):
        self.workflow_steps.append(step)
        self.step_status[step.name] = WorkflowStatus.PENDING
    
    def build_workflow(self, steps: List[WorkflowStep]):
        self.workflow_steps = steps
        for step in steps:
            self.step_status[step.name] = WorkflowStatus.PENDING
    
    def execute_workflow(self, initial_input: Dict[str, Any], verbose: bool = True) -> Dict[str, Any]:
        if verbose:
            print(f"\n{'='*60}")
            print(f"🚀 Starting Workflow: {self.name}")
            print(f"{'='*60}\n")
        
        start_time = datetime.now()
        self.shared_context['initial_input'] = initial_input
        self.shared_context['workflow_start'] = start_time.isoformat()
        
        for step in self.workflow_steps:
            if not self._can_execute_step(step):
                if verbose:
                    print(f"⏭️  Skipping step: {step.name} (dependencies not met)")
                self.step_status[step.name] = WorkflowStatus.SKIPPED
                continue
            
            if step.condition and not step.condition(self.shared_context):
                if verbose:
                    print(f"⏭️  Skipping step: {step.name} (condition not met)")
                self.step_status[step.name] = WorkflowStatus.SKIPPED
                continue
            
            success = self._execute_step(step, verbose)
            
            if not success and step.retry_count < step.max_retries:
                if verbose:
                    print(f"🔄 Retrying step: {step.name} (attempt {step.retry_count + 1}/{step.max_retries})")
                step.retry_count += 1
                success = self._execute_step(step, verbose)
            
            if not success:
                if verbose:
                    print(f"❌ Step failed: {step.name}")
                self.step_status[step.name] = WorkflowStatus.FAILED
                break
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        workflow_result = {
            'workflow_name': self.name,
            'status': self._get_overall_status(),
            'duration_seconds': duration,
            'steps_executed': len([s for s in self.step_status.values() if s == WorkflowStatus.COMPLETED]),
            'steps_failed': len([s for s in self.step_status.values() if s == WorkflowStatus.FAILED]),
            'steps_skipped': len([s for s in self.step_status.values() if s == WorkflowStatus.SKIPPED]),
            'step_results': self.execution_results,
            'shared_context': self.shared_context,
            'timestamp': end_time.isoformat()
        }
        
        self.execution_history.append(workflow_result)
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"✅ Workflow Complete: {workflow_result['status']}")
            print(f"   Duration: {duration:.2f}s")
            print(f"   Steps: {workflow_result['steps_executed']} completed, "
                  f"{workflow_result['steps_failed']} failed, "
                  f"{workflow_result['steps_skipped']} skipped")
            print(f"{'='*60}\n")
        
        return workflow_result
    
    def _can_execute_step(self, step: WorkflowStep) -> bool:
        for dependency in step.depends_on:
            if dependency not in self.step_status:
                return False
            if self.step_status[dependency] != WorkflowStatus.COMPLETED:
                return False
        return True
    
    def _execute_step(self, step: WorkflowStep, verbose: bool) -> bool:
        if verbose:
            print(f"▶️  Executing: {step.name}")
        
        self.step_status[step.name] = WorkflowStatus.IN_PROGRESS
        step_start = datetime.now()
        
        try:
            agent = self.agents.get(step.agent_name)
            if not agent:
                raise ValueError(f"Agent not found: {step.agent_name}")
            
            input_data = self._prepare_step_input(step)
            
            result = agent.process(input_data, context=self.shared_context)
            
            self.execution_results[step.name] = result
            self.shared_context[f"{step.name}_result"] = result
            
            self.step_status[step.name] = WorkflowStatus.COMPLETED
            
            duration = (datetime.now() - step_start).total_seconds()
            if verbose:
                print(f"   ✓ Completed in {duration:.2f}s")
            
            return True
        
        except Exception as e:
            if verbose:
                print(f"   ✗ Error: {str(e)}")
            
            self.execution_results[step.name] = {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            self.step_status[step.name] = WorkflowStatus.FAILED
            return False
    
    def _prepare_step_input(self, step: WorkflowStep) -> Dict[str, Any]:
        if not step.depends_on:
            return self.shared_context.get('initial_input', {})
        
        input_data = {}
        for dependency in step.depends_on:
            if dependency in self.execution_results:
                input_data[dependency] = self.execution_results[dependency]
        
        if 'initial_input' in self.shared_context:
            input_data['original_input'] = self.shared_context['initial_input']
        
        return input_data
    
    def _get_overall_status(self) -> str:
        if any(status == WorkflowStatus.FAILED for status in self.step_status.values()):
            return "FAILED"
        if all(status in [WorkflowStatus.COMPLETED, WorkflowStatus.SKIPPED] for status in self.step_status.values()):
            return "COMPLETED"
        return "PARTIAL"
    
    def get_step_result(self, step_name: str) -> Optional[Dict[str, Any]]:
        return self.execution_results.get(step_name)
    
    def get_workflow_summary(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'total_agents': len(self.agents),
            'total_steps': len(self.workflow_steps),
            'step_status': {name: status.value for name, status in self.step_status.items()},
            'executions': len(self.execution_history)
        }
    
    def visualize_workflow(self) -> str:
        lines = [f"Workflow: {self.name}", "=" * 60]
        
        for i, step in enumerate(self.workflow_steps, 1):
            status = self.step_status.get(step.name, WorkflowStatus.PENDING)
            status_icon = {
                WorkflowStatus.PENDING: "⏸️",
                WorkflowStatus.IN_PROGRESS: "▶️",
                WorkflowStatus.COMPLETED: "✅",
                WorkflowStatus.FAILED: "❌",
                WorkflowStatus.SKIPPED: "⏭️"
            }[status]
            
            deps = f" (depends on: {', '.join(step.depends_on)})" if step.depends_on else ""
            lines.append(f"{i}. {status_icon} {step.name} [{step.agent_name}]{deps}")
        
        lines.append("=" * 60)
        return "\n".join(lines)
    
    def reset(self):
        self.execution_results = {}
        self.step_status = {step.name: WorkflowStatus.PENDING for step in self.workflow_steps}
        self.shared_context = {}
        for step in self.workflow_steps:
            step.retry_count = 0
    
    def __repr__(self) -> str:
        return f"Orchestrator(name='{self.name}', agents={len(self.agents)}, steps={len(self.workflow_steps)})"
