"""
LangGraph Agent Definition
"""

from langgraph.graph import StateGraph, END
from langchain_openai import ChatOpenAI
from .state import AgentState
from .nodes import AgentNodes
from .tools import ExtensionTools
from config import settings


class BrowsingAgent:
    """Autonomous browsing agent using LangGraph"""
    
    def __init__(self, extension_bridge):
        # Initialize LLM
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            temperature=0.7
        )
        
        # Initialize tools
        self.tools = ExtensionTools(extension_bridge)
        
        # Initialize nodes
        self.nodes = AgentNodes(self.llm, self.tools)
        
        # Build graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the agent graph"""
        
        # Create graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("plan", self.nodes.plan)
        workflow.add_node("execute", self.nodes.execute)
        workflow.add_node("synthesize", self.nodes.synthesize)
        
        # Set entry point
        workflow.set_entry_point("plan")
        
        # Add edges
        workflow.add_conditional_edges(
            "plan",
            lambda state: "execute" if not state.get("error") else "error",
            {
                "execute": "execute",
                "error": END
            }
        )
        
        workflow.add_conditional_edges(
            "execute",
            self.nodes.should_continue,
            {
                "execute": "execute",
                "synthesize": "synthesize",
                "error": END
            }
        )
        
        workflow.add_edge("synthesize", END)
        
        return workflow.compile()
    
    async def execute_task(self, task: str, metadata: dict = None) -> dict:
        """
        Execute a task
        
        Args:
            task: Task description
            metadata: Optional metadata
            
        Returns:
            Task result
        """
        # Initialize state
        initial_state = {
            "task": task,
            "task_type": None,
            "plan": [],
            "current_step": 0,
            "actions_executed": [],
            "results": [],
            "context": {},
            "final_result": None,
            "error": None,
            "metadata": metadata or {}
        }
        
        # Run graph
        final_state = await self.graph.ainvoke(initial_state)
        
        return {
            "result": final_state.get("final_result"),
            "plan": final_state.get("plan"),
            "actions_executed": final_state.get("actions_executed"),
            "error": final_state.get("error"),
            "metadata": final_state.get("metadata")
        }
    
    async def stream_task(self, task: str, metadata: dict = None):
        """
        Stream task execution
        
        Args:
            task: Task description
            metadata: Optional metadata
            
        Yields:
            State updates
        """
        # Initialize state
        initial_state = {
            "task": task,
            "task_type": None,
            "plan": [],
            "current_step": 0,
            "actions_executed": [],
            "results": [],
            "context": {},
            "final_result": None,
            "error": None,
            "metadata": metadata or {}
        }
        
        # Stream graph execution
        async for state in self.graph.astream(initial_state):
            yield state
