"""
Debug logging utility for Eventuri-AI
Provides configurable logging levels to reduce console spam
"""
import time
from datetime import datetime

class DebugLogger:
    """Centralized debug logging with configurable verbosity levels"""
    
    LEVEL_ERROR = 0    # Only errors
    LEVEL_WARN = 1     # Errors and warnings  
    LEVEL_INFO = 2     # Errors, warnings, and info
    LEVEL_DEBUG = 3    # Everything including debug
    
    def __init__(self, level=LEVEL_INFO):
        self.level = level
        self._last_debug_count = {}
        self._debug_spam_limit = 10  # Limit repeated debug messages
        
    def set_level(self, level):
        """Set the logging level"""
        self.level = level
        
    def error(self, message, tag="ERROR"):
        """Always log errors"""
        self._log(f"[{tag}] {message}")
        
    def warn(self, message, tag="WARN"):
        """Log warnings if level >= WARN"""
        if self.level >= self.LEVEL_WARN:
            self._log(f"[{tag}] {message}")
            
    def info(self, message, tag="INFO"):
        """Log info if level >= INFO"""
        if self.level >= self.LEVEL_INFO:
            self._log(f"[{tag}] {message}")
            
    def debug(self, message, tag="DEBUG", limit_spam=False):
        """Log debug if level >= DEBUG, with optional spam limiting"""
        if self.level >= self.LEVEL_DEBUG:
            if limit_spam:
                count = self._last_debug_count.get(message, 0)
                if count >= self._debug_spam_limit:
                    return  # Skip this debug message
                self._last_debug_count[message] = count + 1
                
            self._log(f"[{tag}] {message}")
            
    def _log(self, message):
        """Internal logging method"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        print(f"{timestamp} {message}")
        
    def clear_spam_counters(self):
        """Reset spam counters for debug messages"""
        self._last_debug_count.clear()

# Global logger instance
logger = DebugLogger()

# Convenience functions for global access
def set_debug_level(level):
    logger.set_level(level)
    
def log_error(message, tag="ERROR"):
    logger.error(message, tag)
    
def log_warn(message, tag="WARN"):
    logger.warn(message, tag)
    
def log_info(message, tag="INFO"):
    logger.info(message, tag)
    
def log_debug(message, tag="DEBUG", limit_spam=False):
    logger.debug(message, tag, limit_spam)