"""
Session Manager - Manages browser sessions and authentication
Handles LinkedIn login persistence and cookie management
"""

import json
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages browser sessions and authentication state"""
    
    def __init__(self, storage_path: str = "./data/sessions"):
        """
        Initialize session manager
        
        Args:
            storage_path: Path to store session data
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.sessions: Dict[str, Dict] = {}
        self.load_sessions()
        logger.info(f"Session manager initialized: {self.storage_path}")
    
    def load_sessions(self):
        """Load saved sessions from disk"""
        session_file = self.storage_path / "sessions.json"
        
        if session_file.exists():
            try:
                with open(session_file, 'r') as f:
                    self.sessions = json.load(f)
                logger.info(f"Loaded {len(self.sessions)} sessions")
            except Exception as e:
                logger.error(f"Error loading sessions: {e}")
                self.sessions = {}
    
    def save_sessions(self):
        """Save sessions to disk"""
        session_file = self.storage_path / "sessions.json"
        
        try:
            with open(session_file, 'w') as f:
                json.dump(self.sessions, f, indent=2)
            logger.info("Sessions saved")
        except Exception as e:
            logger.error(f"Error saving sessions: {e}")
    
    def store_linkedin_session(self, cookies: List[Dict], user_id: str = "default"):
        """
        Store LinkedIn session cookies
        
        Args:
            cookies: List of cookie dictionaries from browser
            user_id: User identifier
        """
        session_data = {
            "platform": "linkedin",
            "cookies": cookies,
            "stored_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(days=30)).isoformat(),
            "user_id": user_id
        }
        
        self.sessions["linkedin"] = session_data
        self.save_sessions()
        logger.info(f"LinkedIn session stored for user: {user_id}")
    
    def get_linkedin_session(self) -> Optional[Dict]:
        """
        Get LinkedIn session if available and valid
        
        Returns:
            Session data or None
        """
        session = self.sessions.get("linkedin")
        
        if not session:
            logger.warning("No LinkedIn session found")
            return None
        
        # Check if expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now() > expires_at:
            logger.warning("LinkedIn session expired")
            del self.sessions["linkedin"]
            self.save_sessions()
            return None
        
        logger.info("LinkedIn session retrieved")
        return session
    
    def has_linkedin_session(self) -> bool:
        """Check if valid LinkedIn session exists"""
        return self.get_linkedin_session() is not None
    
    def clear_linkedin_session(self):
        """Clear LinkedIn session"""
        if "linkedin" in self.sessions:
            del self.sessions["linkedin"]
            self.save_sessions()
            logger.info("LinkedIn session cleared")
    
    def get_session_cookies(self, platform: str = "linkedin") -> List[Dict]:
        """
        Get cookies for a platform
        
        Args:
            platform: Platform name (linkedin, instagram, etc.)
        
        Returns:
            List of cookie dictionaries
        """
        session = self.sessions.get(platform)
        if session:
            return session.get("cookies", [])
        return []
    
    def request_linkedin_login(self) -> Dict:
        """
        Request user to log in to LinkedIn
        
        Returns:
            Login request information
        """
        return {
            "action": "REQUEST_LOGIN",
            "platform": "linkedin",
            "url": "https://www.linkedin.com/login",
            "instructions": [
                "Please log in to LinkedIn in your browser",
                "The extension will capture your session automatically",
                "This session will be reused for all future tasks"
            ],
            "status": "waiting_for_login"
        }
    
    def get_session_status(self) -> Dict:
        """
        Get status of all sessions
        
        Returns:
            Dictionary of session statuses
        """
        status = {}
        
        for platform, session in self.sessions.items():
            expires_at = datetime.fromisoformat(session["expires_at"])
            is_valid = datetime.now() < expires_at
            
            status[platform] = {
                "valid": is_valid,
                "stored_at": session["stored_at"],
                "expires_at": session["expires_at"],
                "user_id": session.get("user_id", "unknown")
            }
        
        return status


class BrowserSessionBridge:
    """Bridge between orchestrator and browser extension for session management"""
    
    def __init__(self, session_manager: SessionManager):
        self.session_manager = session_manager
        self.pending_logins: Dict[str, Dict] = {}
    
    async def ensure_linkedin_session(self, extension_bridge) -> bool:
        """
        Ensure LinkedIn session is available, request login if needed
        
        Args:
            extension_bridge: Extension bridge instance
        
        Returns:
            True if session available, False if login needed
        """
        if self.session_manager.has_linkedin_session():
            logger.info("LinkedIn session available")
            return True
        
        logger.info("LinkedIn session not available, requesting login")
        
        # Request login from extension
        login_request = self.session_manager.request_linkedin_login()
        
        # Send to extension
        await extension_bridge.send_command({
            "action": "REQUEST_LOGIN",
            "platform": "linkedin",
            "url": "https://www.linkedin.com/login"
        })
        
        # Mark as pending
        self.pending_logins["linkedin"] = {
            "requested_at": datetime.now().isoformat(),
            "status": "pending"
        }
        
        return False
    
    async def handle_session_captured(self, platform: str, cookies: List[Dict], user_id: str = "default"):
        """
        Handle session captured from extension
        
        Args:
            platform: Platform name
            cookies: Session cookies
            user_id: User identifier
        """
        logger.info(f"Session captured for {platform}")
        
        if platform == "linkedin":
            self.session_manager.store_linkedin_session(cookies, user_id)
            
            # Mark login as complete
            if platform in self.pending_logins:
                self.pending_logins[platform]["status"] = "complete"
                self.pending_logins[platform]["completed_at"] = datetime.now().isoformat()
        
        return {"success": True, "platform": platform}
    
    def get_pending_logins(self) -> Dict:
        """Get pending login requests"""
        return self.pending_logins
