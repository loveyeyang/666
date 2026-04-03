"""
PK Tracker - Handles PK (battle) operations
Including: opponent info tracking, guest detection, statistics
"""

import asyncio
from datetime import datetime
from loguru import logger
from typing import Dict, List, Optional, Set


class PKTracker:
    """Track and manage PK battles"""
    
    def __init__(self, config, db_session=None):
        self.config = config
        self.db_session = db_session
        self.logger = logger
        
        self.is_in_pk = False
        self.current_opponent = None
        self.pk_start_time = None
        self.pk_history = []
        
        self.opponent_users: Set[int] = set()
        self.guest_users: Set[int] = set()
        self.guest_activity = {}
    
    async def start_pk(self, opponent_id: str, opponent_name: str):
        """Handle PK start event"""
        try:
            self.is_in_pk = True
            self.pk_start_time = datetime.now()
            self.current_opponent = {
                "opponent_id": opponent_id,
                "opponent_name": opponent_name,
                "start_time": self.pk_start_time.isoformat()
            }
            
            self.logger.info(f"🔥 PK Started! Opponent: {opponent_name} (ID: {opponent_id})")
        
        except Exception as e:
            self.logger.error(f"Error starting PK: {e}")
    
    async def end_pk(self, result: Optional[str] = None):
        """Handle PK end event"""
        try:
            if not self.is_in_pk:
                self.logger.warning("PK not in progress")
                return
            
            pk_duration = (datetime.now() - self.pk_start_time).total_seconds()
            
            pk_record = {
                **self.current_opponent,
                "end_time": datetime.now().isoformat(),
                "duration": pk_duration,
                "result": result,
                "guests_detected": len(self.guest_users)
            }
            
            self.pk_history.append(pk_record)
            
            self.logger.info(f"PK Ended! Result: {result}, Duration: {pk_duration}s, Guests detected: {len(self.guest_users)}")
            
            self.is_in_pk = False
            self.current_opponent = None
            self.opponent_users.clear()
            self.guest_users.clear()
            self.guest_activity.clear()
        
        except Exception as e:
            self.logger.error(f"Error ending PK: {e}")
    
    async def detect_guest_user(self, user_id: int, username: str, action: str = "join") -> bool:
        """Detect if a user is a guest from opponent's stream"""
        try:
            if not self.is_in_pk:
                return False
            
            if user_id not in self.guest_activity:
                self.guest_activity[user_id] = {
                    "username": username,
                    "first_seen": datetime.now().isoformat(),
                    "actions": []
                }
            
            self.guest_activity[user_id]["actions"].append({
                "action": action,
                "timestamp": datetime.now().isoformat()
            })
            
            is_guest = await self._identify_guest(user_id)
            
            if is_guest and user_id not in self.guest_users:
                self.guest_users.add(user_id)
                self.logger.info(f"🚪 Guest detected: {username} (ID: {user_id})")
            
            return is_guest
        
        except Exception as e:
            self.logger.error(f"Error detecting guest: {e}")
            return False
    
    async def _identify_guest(self, user_id: int) -> bool:
        """Identify if a user is likely a guest from opponent stream"""
        try:
            if user_id not in self.guest_activity:
                return False
            
            activity = self.guest_activity[user_id]
            actions = [a["action"] for a in activity["actions"]]
            
            if "gift" in actions or "comment" in actions or "join" in actions:
                return True
            
            return False
        
        except Exception as e:
            self.logger.error(f"Error identifying guest: {e}")
            return False
    
    async def get_opponent_info(self) -> Optional[Dict]:
        """Get current opponent information"""
        try:
            if self.is_in_pk and self.current_opponent:
                return {
                    **self.current_opponent,
                    "guest_count": len(self.guest_users),
                    "is_active": True
                }
            return None
        
        except Exception as e:
            self.logger.error(f"Error getting opponent info: {e}")
            return None
    
    async def get_guest_list(self) -> List[Dict]:
        """Get list of identified guests"""
        try:
            guests = []
            for user_id in self.guest_users:
                if user_id in self.guest_activity:
                    guests.append({
                        "user_id": user_id,
                        **self.guest_activity[user_id]
                    })
            
            self.logger.info(f"Retrieved {len(guests)} guest records")
            return guests
        
        except Exception as e:
            self.logger.error(f"Error getting guest list: {e}")
            return []
    
    async def get_pk_statistics(self) -> Dict:
        """Get PK statistics"""
        try:
            if not self.pk_history:
                return {"total_pks": 0}
            
            total_pks = len(self.pk_history)
            wins = sum(1 for pk in self.pk_history if pk.get("result") == "win")
            losses = sum(1 for pk in self.pk_history if pk.get("result") == "lose")
            
            stats = {
                "total_pks": total_pks,
                "wins": wins,
                "losses": losses,
                "current_pk_active": self.is_in_pk
            }
            
            self.logger.info(f"PK statistics: {stats}")
            return stats
        
        except Exception as e:
            self.logger.error(f"Error getting PK statistics: {e}")
            return {}
    
    def reset_session(self):
        """Reset session data"""
        self.is_in_pk = False
        self.current_opponent = None
        self.opponent_users.clear()
        self.guest_users.clear()
        self.guest_activity.clear()
        self.pk_history.clear()
        self.logger.info("PK session data reset")
