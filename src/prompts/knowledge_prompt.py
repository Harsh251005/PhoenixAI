from model.schema import State
from src.model.schema import State

KNOWLEDGE_INPUT = {
    "user_input": State.user_input,
    "success": State.executor.success,
    "attempts": State.executor.retry_count,
    
}