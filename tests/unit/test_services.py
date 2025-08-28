#!/usr/bin/env python3
"""
Test services to debug dashboard issues
"""

try:
    from services.recommendations import RecommendationService
    print("RecommendationService imported successfully")
    
    rec = RecommendationService()
    print("RecommendationService instantiated successfully")
    
except Exception as e:
    print(f"RecommendationService error: {e}")

try:
    from services.analytics import AnalyticsService
    print("AnalyticsService imported successfully")
    
    analytics = AnalyticsService()
    print("AnalyticsService instantiated successfully")
    
except Exception as e:
    print(f"AnalyticsService error: {e}")

try:
    from services.ollama_client import OllamaClient
    print("OllamaClient imported successfully")
    
    client = OllamaClient("http://localhost:11434")
    print("OllamaClient instantiated successfully")
    
except Exception as e:
    print(f"OllamaClient error: {e}")