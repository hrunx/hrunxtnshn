"""
Agent Graph Nodes
"""

from typing import Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
import json
from .state import AgentState
from .tools import ExtensionTools


class AgentNodes:
    """Agent graph nodes"""
    
    def __init__(self, llm: ChatOpenAI, tools: ExtensionTools):
        self.llm = llm
        self.tools = tools
    
    async def plan(self, state: AgentState) -> AgentState:
        """
        Plan the task execution
        
        Creates a list of actions to execute based on the task
        """
        task = state["task"]
        
        # Create planning prompt
        tool_descriptions = self.tools.get_tool_descriptions()
        tools_text = "\n".join([
            f"- {tool['name']}: {tool['description']}"
            for tool in tool_descriptions
        ])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an autonomous browsing agent. You can interact with web pages and extract data.

Available tools:
{tools}

Your task is to create a plan to accomplish the user's request. Respond with a JSON array of actions.

Each action should have:
- action: The action type (LOAD_PAGE, FETCH, EXTRACT_LINKEDIN, EXTRACT_INSTAGRAM, EXTRACT_MAPS, WAIT)
- url: The URL to act on (if applicable)
- duration: Duration in milliseconds (for WAIT action)

Example response:
[
  {{"action": "LOAD_PAGE", "url": "https://linkedin.com/in/example"}},
  {{"action": "EXTRACT_LINKEDIN", "url": "https://linkedin.com/in/example"}}
]

Respond ONLY with the JSON array, no other text."""),
            ("user", "{task}")
        ])
        
        # Get plan from LLM
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "tools": tools_text,
            "task": task
        })
        
        # Parse plan
        try:
            content = response.content
            # Try to extract JSON from markdown code blocks
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            plan = json.loads(content)
            
            if not isinstance(plan, list):
                plan = [plan]
            
            state["plan"] = plan
            state["current_step"] = 0
            state["metadata"]["plan_created"] = True
            
        except Exception as e:
            state["error"] = f"Failed to parse plan: {str(e)}"
            state["plan"] = []
        
        return state
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute the planned actions
        """
        plan = state["plan"]
        current_step = state["current_step"]
        
        if current_step >= len(plan):
            # All steps executed
            return state
        
        action = plan[current_step]
        action_type = action.get("action")
        
        try:
            # Execute action using tools
            if action_type == "LOAD_PAGE":
                result = await self.tools.load_page(action["url"])
            elif action_type == "FETCH":
                result = await self.tools.fetch_with_session(action["url"])
            elif action_type == "EXTRACT_LINKEDIN":
                result = await self.tools.extract_linkedin(action["url"])
            elif action_type == "EXTRACT_INSTAGRAM":
                result = await self.tools.extract_instagram(action["url"])
            elif action_type == "EXTRACT_MAPS":
                result = await self.tools.extract_maps(action["url"])
            elif action_type == "WAIT":
                result = await self.tools.wait(action.get("duration", 1000))
            else:
                result = {"error": f"Unknown action: {action_type}"}
            
            # Store result
            state["actions_executed"].append(action)
            state["results"].append(result)
            state["current_step"] += 1
            
        except Exception as e:
            state["error"] = f"Action execution failed: {str(e)}"
        
        return state
    
    async def synthesize(self, state: AgentState) -> AgentState:
        """
        Synthesize the final result from all executed actions
        """
        results = state["results"]
        task = state["task"]
        
        # If only one result, return it directly
        if len(results) == 1:
            state["final_result"] = results[0]
            return state
        
        # If multiple results, ask LLM to synthesize
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a data synthesis agent. Combine the following results into a coherent response for the user's task."),
            ("user", """Task: {task}

Results:
{results}

Provide a clear, structured summary of the results.""")
        ])
        
        chain = prompt | self.llm
        response = await chain.ainvoke({
            "task": task,
            "results": json.dumps(results, indent=2)
        })
        
        state["final_result"] = {
            "summary": response.content,
            "raw_results": results
        }
        
        return state
    
    def should_continue(self, state: AgentState) -> str:
        """
        Decide whether to continue execution or finish
        """
        if state.get("error"):
            return "error"
        
        if state["current_step"] >= len(state["plan"]):
            return "synthesize"
        
        return "execute"
