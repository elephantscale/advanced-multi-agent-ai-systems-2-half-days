from typing import Dict, Any, List, Optional
from enum import Enum
from datetime import datetime
from collections import defaultdict
import json


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class Message:
    
    def __init__(
        self,
        sender: str,
        receiver: str,
        content: Dict[str, Any],
        message_type: str = "data",
        priority: MessagePriority = MessagePriority.NORMAL,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.id = f"msg_{datetime.now().timestamp()}_{sender}_{receiver}"
        self.sender = sender
        self.receiver = receiver
        self.content = content
        self.message_type = message_type
        self.priority = priority
        self.metadata = metadata or {}
        self.timestamp = datetime.now().isoformat()
        self.delivered = False
        self.processed = False
    
    def mark_delivered(self):
        self.delivered = True
        self.metadata['delivered_at'] = datetime.now().isoformat()
    
    def mark_processed(self):
        self.processed = True
        self.metadata['processed_at'] = datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'sender': self.sender,
            'receiver': self.receiver,
            'content': self.content,
            'message_type': self.message_type,
            'priority': self.priority.value,
            'metadata': self.metadata,
            'timestamp': self.timestamp,
            'delivered': self.delivered,
            'processed': self.processed
        }
    
    def __repr__(self) -> str:
        return f"Message(from={self.sender}, to={self.receiver}, type={self.message_type}, priority={self.priority.name})"


class MessageBus:
    
    def __init__(self):
        self.messages: List[Message] = []
        self.agent_inboxes: Dict[str, List[Message]] = defaultdict(list)
        self.message_history: List[Message] = []
    
    def send(self, message: Message) -> str:
        self.messages.append(message)
        self.agent_inboxes[message.receiver].append(message)
        message.mark_delivered()
        return message.id
    
    def send_to_multiple(self, sender: str, receivers: List[str], content: Dict[str, Any], **kwargs) -> List[str]:
        message_ids = []
        for receiver in receivers:
            message = Message(sender=sender, receiver=receiver, content=content, **kwargs)
            message_id = self.send(message)
            message_ids.append(message_id)
        return message_ids
    
    def receive(self, agent_name: str, mark_processed: bool = True) -> List[Message]:
        messages = self.agent_inboxes[agent_name]
        
        if mark_processed:
            for msg in messages:
                msg.mark_processed()
                self.message_history.append(msg)
            self.agent_inboxes[agent_name] = []
        
        return sorted(messages, key=lambda m: m.priority.value, reverse=True)
    
    def peek(self, agent_name: str) -> List[Message]:
        return self.agent_inboxes[agent_name]
    
    def has_messages(self, agent_name: str) -> bool:
        return len(self.agent_inboxes[agent_name]) > 0
    
    def get_message_by_id(self, message_id: str) -> Optional[Message]:
        for msg in self.messages:
            if msg.id == message_id:
                return msg
        for msg in self.message_history:
            if msg.id == message_id:
                return msg
        return None
    
    def get_conversation(self, agent1: str, agent2: str) -> List[Message]:
        conversation = []
        all_messages = self.messages + self.message_history
        
        for msg in all_messages:
            if (msg.sender == agent1 and msg.receiver == agent2) or \
               (msg.sender == agent2 and msg.receiver == agent1):
                conversation.append(msg)
        
        return sorted(conversation, key=lambda m: m.timestamp)
    
    def get_stats(self) -> Dict[str, Any]:
        total_messages = len(self.messages) + len(self.message_history)
        
        by_priority = defaultdict(int)
        by_type = defaultdict(int)
        by_agent = defaultdict(int)
        
        for msg in self.messages + self.message_history:
            by_priority[msg.priority.name] += 1
            by_type[msg.message_type] += 1
            by_agent[msg.sender] += 1
        
        return {
            'total_messages': total_messages,
            'pending_messages': len(self.messages),
            'processed_messages': len(self.message_history),
            'by_priority': dict(by_priority),
            'by_type': dict(by_type),
            'by_sender': dict(by_agent)
        }
    
    def clear(self):
        self.messages = []
        self.agent_inboxes = defaultdict(list)
        self.message_history = []
    
    def visualize_flow(self) -> str:
        lines = ["Message Flow Visualization", "=" * 50]
        
        all_messages = sorted(
            self.messages + self.message_history,
            key=lambda m: m.timestamp
        )
        
        for i, msg in enumerate(all_messages, 1):
            status = "✓" if msg.processed else "○"
            priority_icon = "🔴" if msg.priority == MessagePriority.CRITICAL else \
                          "🟡" if msg.priority == MessagePriority.HIGH else \
                          "🟢" if msg.priority == MessagePriority.NORMAL else "⚪"
            
            lines.append(f"{i}. {status} {priority_icon} {msg.sender} → {msg.receiver} [{msg.message_type}]")
        
        lines.append("=" * 50)
        return "\n".join(lines)
    
    def __repr__(self) -> str:
        return f"MessageBus(pending={len(self.messages)}, processed={len(self.message_history)})"
