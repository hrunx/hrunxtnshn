"""
Extension Bridge V2 - WebSocket-based communication with extension
Supports orchestrator-driven invisible browsing
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Callable, List
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)


class ExtensionBridge:
    """Bridge for communication between orchestrator and browser extension"""
    
    def __init__(self):
        self.connections: Dict[str, 'WebSocket'] = {}
        self.pending_commands: Dict[str, asyncio.Future] = {}
        self.command_timeout = 120  # 2 minutes for long-running tasks
        self.event_handlers: Dict[str, List[Callable]] = {}
        logger.info("Extension bridge initialized")
    
    async def register_connection(self, websocket, connection_id: str):
        """
        Register extension connection
        
        Args:
            websocket: WebSocket connection
            connection_id: Unique connection identifier
        """
        self.connections[connection_id] = websocket
        logger.info(f"Extension connected: {connection_id}")
        
        # Emit connection event
        await self.emit_event("extension_connected", {
            "connection_id": connection_id,
            "connected_at": datetime.now().isoformat()
        })
    
    async def unregister_connection(self, connection_id: str):
        """Unregister extension connection"""
        if connection_id in self.connections:
            del self.connections[connection_id]
            logger.info(f"Extension disconnected: {connection_id}")
            
            await self.emit_event("extension_disconnected", {
                "connection_id": connection_id,
                "disconnected_at": datetime.now().isoformat()
            })
    
    async def send_command(
        self,
        command: Dict,
        connection_id: Optional[str] = None,
        timeout: Optional[int] = None
    ) -> Dict:
        """
        Send command to extension and wait for response
        
        Args:
            command: Command dictionary
            connection_id: Specific connection to send to (or first available)
            timeout: Command timeout in seconds
        
        Returns:
            Command response
        """
        if not self.connections:
            raise Exception("No extension connected")
        
        # Get target connection
        if connection_id and connection_id in self.connections:
            websocket = self.connections[connection_id]
        else:
            # Use first available connection
            websocket = next(iter(self.connections.values()))
        
        # Generate command ID
        command_id = command.get("command_id") or str(uuid.uuid4())
        command["command_id"] = command_id
        
        # Create future for response
        future = asyncio.Future()
        self.pending_commands[command_id] = future
        
        try:
            # Send command
            logger.info(f"Sending command {command_id}: {command.get('action')}")
            await websocket.send_json(command)
            
            # Wait for response with timeout
            timeout_val = timeout or self.command_timeout
            response = await asyncio.wait_for(future, timeout=timeout_val)
            
            logger.info(f"Command {command_id} completed")
            return response
        
        except asyncio.TimeoutError:
            logger.error(f"Command {command_id} timed out")
            return {"success": False, "error": "Command timeout"}
        
        except Exception as e:
            logger.error(f"Command {command_id} error: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            # Clean up
            if command_id in self.pending_commands:
                del self.pending_commands[command_id]
    
    async def handle_response(self, response: Dict):
        """
        Handle response from extension
        
        Args:
            response: Response dictionary
        """
        command_id = response.get("command_id")
        
        if command_id and command_id in self.pending_commands:
            future = self.pending_commands[command_id]
            if not future.done():
                future.set_result(response)
        else:
            logger.warning(f"Received response for unknown command: {command_id}")
    
    async def handle_event(self, event: Dict):
        """
        Handle event from extension
        
        Args:
            event: Event dictionary
        """
        event_type = event.get("event")
        event_data = event.get("data", {})
        
        logger.info(f"Received event: {event_type}")
        
        # Emit to registered handlers
        await self.emit_event(event_type, event_data)
    
    def on_event(self, event_type: str, handler: Callable):
        """
        Register event handler
        
        Args:
            event_type: Event type to listen for
            handler: Async handler function
        """
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        
        self.event_handlers[event_type].append(handler)
        logger.info(f"Registered handler for event: {event_type}")
    
    async def emit_event(self, event_type: str, data: Dict):
        """
        Emit event to registered handlers
        
        Args:
            event_type: Event type
            data: Event data
        """
        handlers = self.event_handlers.get(event_type, [])
        
        for handler in handlers:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Error in event handler for {event_type}: {e}")
    
    async def broadcast(self, message: Dict):
        """
        Broadcast message to all connected extensions
        
        Args:
            message: Message to broadcast
        """
        for connection_id, websocket in self.connections.items():
            try:
                await websocket.send_json(message)
            except Exception as e:
                logger.error(f"Error broadcasting to {connection_id}: {e}")
    
    def is_connected(self) -> bool:
        """Check if any extension is connected"""
        return len(self.connections) > 0
    
    def get_connection_count(self) -> int:
        """Get number of connected extensions"""
        return len(self.connections)
    
    def get_connection_ids(self) -> List[str]:
        """Get list of connected extension IDs"""
        return list(self.connections.keys())


# WebSocket endpoint handler
async def websocket_endpoint(websocket, extension_bridge: ExtensionBridge):
    """
    WebSocket endpoint for extension communication
    
    Args:
        websocket: WebSocket connection
        extension_bridge: Extension bridge instance
    """
    connection_id = str(uuid.uuid4())
    
    try:
        await extension_bridge.register_connection(websocket, connection_id)
        
        # Handle messages
        async for message in websocket:
            try:
                if isinstance(message, str):
                    data = json.loads(message)
                else:
                    data = message
                
                message_type = data.get("type")
                
                if message_type == "response":
                    await extension_bridge.handle_response(data)
                elif message_type == "event":
                    await extension_bridge.handle_event(data)
                else:
                    logger.warning(f"Unknown message type: {message_type}")
            
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from extension: {e}")
            except Exception as e:
                logger.error(f"Error handling message: {e}")
    
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    
    finally:
        await extension_bridge.unregister_connection(connection_id)
