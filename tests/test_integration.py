#!/usr/bin/env python3
"""
Integration test for the entire multi-service application.
This test starts all services, runs tests against them, and then stops them.
"""

import subprocess
import time
import requests
import pytest
import os
import sys


class TestIntegration:
    """Integration test suite for all services."""

    @classmethod
    def setup_class(cls):
        """Start all services before running tests."""
        print("Starting all services...")
        
        # Stop any existing services
        subprocess.run(["docker", "compose", "down"], 
                      capture_output=True, cwd=cls._get_project_root())
        
        # Start services in background
        result = subprocess.run(
            ["docker", "compose", "up", "--build", "-d"],
            capture_output=True,
            text=True,
            cwd=cls._get_project_root()
        )
        
        if result.returncode != 0:
            raise Exception(f"Failed to start services: {result.stderr}")
        
        print("Services started. Waiting for them to be ready...")
        cls._wait_for_services()

    @classmethod
    def teardown_class(cls):
        """Stop all services after running tests."""
        print("Stopping all services...")
        subprocess.run(["docker", "compose", "down"], 
                      capture_output=True, cwd=cls._get_project_root())
        print("Services stopped.")

    @staticmethod
    def _get_project_root():
        """Get the project root directory."""
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    @classmethod
    def _wait_for_services(cls, max_retries=30, delay=2):
        """Wait for all services to be ready."""
        for attempt in range(max_retries):
            try:
                # Check nginx health endpoint
                response = requests.get("http://localhost:80/health", timeout=5)
                if response.status_code == 200:
                    print("All services are ready!")
                    return
            except requests.exceptions.RequestException:
                pass
            
            print(f"Waiting for services... (attempt {attempt + 1}/{max_retries})")
            time.sleep(delay)
        
        raise Exception("Services failed to start within expected time")

    def test_nginx_health_endpoint(self):
        """Test nginx health endpoint."""
        response = requests.get("http://localhost:80/health")
        assert response.status_code == 200
        assert "healthy" in response.text

    def test_flask_app_via_nginx(self):
        """Test Flask app through nginx reverse proxy."""
        response = requests.get("http://localhost:80/")
        assert response.status_code == 200
        assert "html" in response.text.lower()

    def test_tornado_app_via_nginx(self):
        """Test Tornado app through nginx reverse proxy."""
        response = requests.get("http://localhost:80/tornado/")
        assert response.status_code == 200
        assert "Hello, world" in response.text


    def test_flask_to_tornado_communication(self):
        """Test Flask app's ability to communicate with Tornado app."""
        # Test sync request to Tornado via Flask
        response = requests.post("http://localhost:80/call-tornado", 
                                data={'endpoint': '/'})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Hello, world" in data["response_text"]
        
        # Test async request to Tornado via Flask
        response = requests.post("http://localhost:80/call-tornado-async", 
                                data={'endpoint': '/'})
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "Hello, world" in data["response_text"]

    def test_all_services_running(self):
        """Verify all containers are running."""
        result = subprocess.run(
            ["docker", "compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            cwd=self._get_project_root()
        )
        
        assert result.returncode == 0
        
        # Check that we have 3 services running
        import json
        services = []
        for line in result.stdout.strip().split('\n'):
            if line.strip():
                services.append(json.loads(line))
        
        assert len(services) == 3
        
        # Check all services are running
        service_names = {service['Service'] for service in services}
        expected_services = {'flask-app', 'tornado-app', 'nginx'}
        assert service_names == expected_services
        
        # Check all services have "running" state
        for service in services:
            assert service['State'] == 'running'


if __name__ == "__main__":
    # Run the integration test
    pytest.main([__file__, "-v"])