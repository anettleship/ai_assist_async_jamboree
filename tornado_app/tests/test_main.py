import pytest
import asyncio
import unittest
from tornado.testing import AsyncHTTPTestCase
from tornado.web import Application

from tornado_app.main import make_app

# For AsyncHTTPTestCase, we need to use unittest-style classes
# This is because AsyncHTTPTestCase is specifically designed for unittest
class TestMainHandlerHTTP(AsyncHTTPTestCase):
    """Test the MainHandler class using Tornado's AsyncHTTPTestCase"""
    
    def get_app(self):
        """Return the Application instance for testing"""
        return make_app()
    
    def test_get_hello_world(self):
        """Test that GET request to root returns 'Hello, world'"""
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        self.assertEqual(response.body.decode('utf-8'), "Hello, world")
    
    def test_content_type(self):
        """Test that the response has the correct content type"""
        response = self.fetch('/')
        self.assertEqual(response.code, 200)
        # Tornado sets text/html as default content-type
        self.assertIn('text/html', response.headers.get('Content-Type', ''))
    
    def test_404_for_unknown_route(self):
        """Test that unknown routes return 404"""
        response = self.fetch('/unknown')
        self.assertEqual(response.code, 404)


class TestIntegration:
    """Integration tests using pytest fixtures"""
    
    def test_app_can_be_created_multiple_times(self):
        """Test that multiple app instances can be created"""
        app1 = make_app()
        app2 = make_app()
        assert app1 is not app2
        assert isinstance(app1, Application)
        assert isinstance(app2, Application)

