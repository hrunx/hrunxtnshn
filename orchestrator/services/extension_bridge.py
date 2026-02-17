"""
Extension Bridge Service
Handles communication with the browser extension
"""

import asyncio
from typing import Dict, Any, Optional
import uuid


class ExtensionBridge:
    """Bridge for communicating with browser extension"""
    
    def __init__(self):
        self.pending_requests: Dict[str, asyncio.Future] = {}
        self.extension_connected = False
        self.extension_id: Optional[str] = None
    
    def register_extension(self, extension_id: str):
        """Register a connected extension"""
        self.extension_id = extension_id
        self.extension_connected = True
        print(f"Extension registered: {extension_id}")
    
    def unregister_extension(self):
        """Unregister the extension"""
        self.extension_connected = False
        self.extension_id = None
        print("Extension unregistered")
    
    async def send_action(self, action: Dict[str, Any], timeout: int = 30) -> Dict[str, Any]:
        """
        Send an action to the extension and wait for response
        
        Args:
            action: Action to send
            timeout: Timeout in seconds
            
        Returns:
            Action result
        """
        if not self.extension_connected:
            raise Exception("Extension not connected")
        
        # Generate request ID
        request_id = str(uuid.uuid4())
        
        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future
        
        # In a real implementation, this would send the action to the extension
        # For now, we'll simulate it
        # TODO: Implement WebSocket or HTTP callback mechanism
        
        try:
            # Wait for response with timeout
            result = await asyncio.wait_for(future, timeout=timeout)
            return result
        except asyncio.TimeoutError:
            raise Exception(f"Action timeout after {timeout}s")
        finally:
            # Clean up
            if request_id in self.pending_requests:
                del self.pending_requests[request_id]
    
    def receive_response(self, request_id: str, response: Dict[str, Any]):
        """
        Receive a response from the extension
        
        Args:
            request_id: Request ID
            response: Response data
        """
        if request_id in self.pending_requests:
            future = self.pending_requests[request_id]
            if not future.done():
                future.set_result(response)
    
    def receive_error(self, request_id: str, error: str):
        """
        Receive an error from the extension
        
        Args:
            request_id: Request ID
            error: Error message
        """
        if request_id in self.pending_requests:
            future = self.pending_requests[request_id]
            if not future.done():
                future.set_exception(Exception(error))
    
    def is_connected(self) -> bool:
        """Check if extension is connected"""
        return self.extension_connected


# Global extension bridge instance
extension_bridge = ExtensionBridge()
