"""
API Configuration Module

This module manages configuration settings for the Weather.gov API integration,
including API settings, feature flags, and environment variable support.
"""

import os
import logging
from typing import Dict, Any, Optional
from dataclasses import dataclass, field

_LOGGER = logging.getLogger(__name__)


@dataclass
class APIConfig:
    """Configuration settings for the Weather.gov API."""
    base_url: str = "https://api.weather.gov"
    user_agent: str = "SatComForecast/1.0"
    timeout: int = 10
    retry_attempts: int = 3
    retry_delay: float = 1.0
    rate_limit_delay: float = 0.5
    enable_alerts: bool = False
    cache_duration: int = 300  # 5 minutes in seconds
    max_cache_size: int = 1000


@dataclass
class FeatureFlags:
    """Feature flags for controlling API behavior."""
    use_api: bool = False
    fallback_to_html: bool = True
    enable_alerts: bool = False
    enable_caching: bool = True
    enable_metrics: bool = True
    debug_mode: bool = False


class ConfigManager:
    """Manages configuration loading and validation."""
    
    def __init__(self):
        self.api_config = APIConfig()
        self.feature_flags = FeatureFlags()
        self._load_from_environment()
        
    def _load_from_environment(self):
        """Load configuration from environment variables."""
        # API Configuration
        self.api_config.base_url = os.getenv(
            'WEATHER_API_BASE_URL', 
            self.api_config.base_url
        )
        self.api_config.user_agent = os.getenv(
            'WEATHER_API_USER_AGENT', 
            self.api_config.user_agent
        )
        self.api_config.timeout = int(os.getenv(
            'WEATHER_API_TIMEOUT', 
            str(self.api_config.timeout)
        ))
        self.api_config.retry_attempts = int(os.getenv(
            'WEATHER_API_RETRY_ATTEMPTS', 
            str(self.api_config.retry_attempts)
        ))
        self.api_config.retry_delay = float(os.getenv(
            'WEATHER_API_RETRY_DELAY', 
            str(self.api_config.retry_delay)
        ))
        self.api_config.rate_limit_delay = float(os.getenv(
            'WEATHER_API_RATE_LIMIT_DELAY', 
            str(self.api_config.rate_limit_delay)
        ))
        self.api_config.enable_alerts = os.getenv(
            'WEATHER_API_ENABLE_ALERTS', 
            'false'
        ).lower() == 'true'
        self.api_config.cache_duration = int(os.getenv(
            'WEATHER_API_CACHE_DURATION', 
            str(self.api_config.cache_duration)
        ))
        self.api_config.max_cache_size = int(os.getenv(
            'WEATHER_API_MAX_CACHE_SIZE', 
            str(self.api_config.max_cache_size)
        ))
        
        # Feature Flags
        self.feature_flags.use_api = os.getenv(
            'WEATHER_USE_API', 
            'false'
        ).lower() == 'true'
        self.feature_flags.fallback_to_html = os.getenv(
            'WEATHER_FALLBACK_HTML', 
            'true'
        ).lower() == 'true'
        self.feature_flags.enable_alerts = os.getenv(
            'WEATHER_ENABLE_ALERTS', 
            'false'
        ).lower() == 'true'
        self.feature_flags.enable_caching = os.getenv(
            'WEATHER_ENABLE_CACHING', 
            'true'
        ).lower() == 'true'
        self.feature_flags.enable_metrics = os.getenv(
            'WEATHER_ENABLE_METRICS', 
            'true'
        ).lower() == 'true'
        self.feature_flags.debug_mode = os.getenv(
            'WEATHER_DEBUG_MODE', 
            'false'
        ).lower() == 'true'
        
        _LOGGER.debug("Configuration loaded from environment variables")
        
    def validate_config(self) -> bool:
        """
        Validate configuration settings.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        errors = []
        
        # Validate API configuration
        if not self.api_config.base_url.startswith(('http://', 'https://')):
            errors.append("API base URL must start with http:// or https://")
            
        if self.api_config.timeout <= 0:
            errors.append("API timeout must be positive")
            
        if self.api_config.retry_attempts < 0:
            errors.append("Retry attempts must be non-negative")
            
        if self.api_config.retry_delay < 0:
            errors.append("Retry delay must be non-negative")
            
        if self.api_config.rate_limit_delay < 0:
            errors.append("Rate limit delay must be non-negative")
            
        if self.api_config.cache_duration <= 0:
            errors.append("Cache duration must be positive")
            
        if self.api_config.max_cache_size <= 0:
            errors.append("Max cache size must be positive")
            
        # Validate feature flags
        if not isinstance(self.feature_flags.use_api, bool):
            errors.append("use_api must be a boolean")
            
        if not isinstance(self.feature_flags.fallback_to_html, bool):
            errors.append("fallback_to_html must be a boolean")
            
        if not isinstance(self.feature_flags.enable_alerts, bool):
            errors.append("enable_alerts must be a boolean")
            
        if not isinstance(self.feature_flags.enable_caching, bool):
            errors.append("enable_caching must be a boolean")
            
        if not isinstance(self.feature_flags.enable_metrics, bool):
            errors.append("enable_metrics must be a boolean")
            
        if not isinstance(self.feature_flags.debug_mode, bool):
            errors.append("debug_mode must be a boolean")
            
        if errors:
            for error in errors:
                _LOGGER.error(f"Configuration validation error: {error}")
            return False
            
        _LOGGER.debug("Configuration validation passed")
        return True
        
    def get_api_config_dict(self) -> Dict[str, Any]:
        """Get API configuration as dictionary."""
        return {
            'base_url': self.api_config.base_url,
            'user_agent': self.api_config.user_agent,
            'timeout': self.api_config.timeout,
            'retry_attempts': self.api_config.retry_attempts,
            'retry_delay': self.api_config.retry_delay,
            'rate_limit_delay': self.api_config.rate_limit_delay,
            'enable_alerts': self.api_config.enable_alerts,
            'cache_duration': self.api_config.cache_duration,
            'max_cache_size': self.api_config.max_cache_size
        }
        
    def get_feature_flags_dict(self) -> Dict[str, bool]:
        """Get feature flags as dictionary."""
        return {
            'use_api': self.feature_flags.use_api,
            'fallback_to_html': self.feature_flags.fallback_to_html,
            'enable_alerts': self.feature_flags.enable_alerts,
            'enable_caching': self.feature_flags.enable_caching,
            'enable_metrics': self.feature_flags.enable_metrics,
            'debug_mode': self.feature_flags.debug_mode
        }
        
    def update_feature_flag(self, flag_name: str, value: bool) -> bool:
        """
        Update a feature flag at runtime.
        
        Args:
            flag_name: Name of the feature flag
            value: New value for the flag
            
        Returns:
            True if flag was updated, False if flag doesn't exist
        """
        if hasattr(self.feature_flags, flag_name):
            setattr(self.feature_flags, flag_name, value)
            _LOGGER.info(f"Updated feature flag {flag_name} to {value}")
            return True
        else:
            _LOGGER.warning(f"Unknown feature flag: {flag_name}")
            return False
            
    def is_api_enabled(self) -> bool:
        """Check if API mode is enabled."""
        return self.feature_flags.use_api
        
    def is_fallback_enabled(self) -> bool:
        """Check if HTML fallback is enabled."""
        return self.feature_flags.fallback_to_html
        
    def is_caching_enabled(self) -> bool:
        """Check if caching is enabled."""
        return self.feature_flags.enable_caching
        
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.feature_flags.debug_mode


# Global configuration manager instance
config_manager = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration manager."""
    return config_manager


def reload_config():
    """Reload configuration from environment variables."""
    global config_manager
    config_manager = ConfigManager()
    _LOGGER.info("Configuration reloaded from environment variables")


# Convenience functions
def get_api_config() -> APIConfig:
    """Get API configuration."""
    return config_manager.api_config


def get_feature_flags() -> FeatureFlags:
    """Get feature flags."""
    return config_manager.feature_flags


def is_api_enabled() -> bool:
    """Check if API mode is enabled."""
    return config_manager.is_api_enabled()


def is_fallback_enabled() -> bool:
    """Check if HTML fallback is enabled."""
    return config_manager.is_fallback_enabled()


def is_caching_enabled() -> bool:
    """Check if caching is enabled."""
    return config_manager.is_caching_enabled()


def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return config_manager.is_debug_mode()