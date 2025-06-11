#!/usr/bin/env python3
"""
High-volume load testing script to overwhelm Flask's thread pool.

Usage:
  python load_test.py sync 100       # 100 requests/sec to sync endpoint
  python load_test.py async 100      # 100 requests/sec to async endpoint
  python load_test.py sync 50 30     # 50 requests/sec for 30 seconds
"""

import sys
import time
import threading
import requests
from concurrent.futures import ThreadPoolExecutor
import queue

class LoadTester:
    def __init__(self, endpoint_type, requests_per_second, duration_seconds=10, base_url="http://localhost:5000"):
        self.endpoint_type = endpoint_type
        self.requests_per_second = requests_per_second
        self.duration_seconds = duration_seconds
        self.base_url = base_url
        
        # Calculate total requests
        self.total_requests = requests_per_second * duration_seconds
        
        # Set up endpoint
        if endpoint_type == 'sync':
            self.url = f"{base_url}/call-tornado"
        elif endpoint_type == 'async':
            self.url = f"{base_url}/call-tornado-async"
        else:
            raise ValueError("endpoint_type must be 'sync' or 'async'")
        
        # Results tracking
        self.results = queue.Queue()
        self.request_counter = 0
        self.start_time = None
        
    def make_request(self, request_id):
        """Make a single request and track timing."""
        request_start = time.time()
        try:
            response = requests.post(
                self.url, 
                data={'endpoint': '/'}, 
                timeout=60
            )
            request_end = time.time()
            duration = request_end - request_start
            
            # Calculate how long since load test started
            time_since_start = request_start - self.start_time
            
            result = {
                'id': request_id,
                'status_code': response.status_code,
                'duration': duration,
                'time_since_start': time_since_start,
                'success': response.status_code == 200
            }
            
            self.results.put(result)
            print(f"Request {request_id:4d}: {response.status_code} in {duration:.2f}s (at T+{time_since_start:.1f}s)")
            
        except requests.RequestException as e:
            request_end = time.time()
            duration = request_end - request_start
            time_since_start = request_start - self.start_time
            
            result = {
                'id': request_id,
                'status_code': None,
                'duration': duration,
                'time_since_start': time_since_start,
                'success': False,
                'error': str(e)
            }
            
            self.results.put(result)
            print(f"Request {request_id:4d}: FAILED ({e}) after {duration:.2f}s (at T+{time_since_start:.1f}s)")
    
    def run_load_test(self):
        """Execute the high-volume load test."""
        print(f"🔥 {self.endpoint_type.upper()} Load Test Configuration:")
        print(f"   Target: {self.url}")
        print(f"   Rate: {self.requests_per_second} requests/second")
        print(f"   Duration: {self.duration_seconds} seconds")
        print(f"   Total requests: {self.total_requests}")
        print()
        
        if self.endpoint_type == 'sync':
            print("⚠️  SYNC ENDPOINT - This should overwhelm Flask's thread pool!")
            print("   🌐 Try loading http://localhost:5000 in your browser during the test")
            print("   📱 You should see delays/timeouts on new page loads")
        else:
            print("⚡ ASYNC ENDPOINT - This should handle load more gracefully")
            print("   🌐 Try loading http://localhost:5000 in your browser during the test") 
            print("   📱 Page loads should remain responsive")
        
        print(f"\n🚀 Starting load test at {time.strftime('%H:%M:%S')}...")
        print("💡 Open your browser to http://localhost:5000 NOW!\n")
        
        # Use a large thread pool to generate high concurrency
        max_workers = min(self.requests_per_second * 2, 5000)  # Cap at 5000 threads
        
        self.start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            request_id = 1
            
            for second in range(self.duration_seconds):
                second_start = time.time()
                
                # Submit all requests for this second
                for _ in range(self.requests_per_second):
                    executor.submit(self.make_request, request_id)
                    request_id += 1
                
                # Wait until the next second (maintain rate limiting)
                elapsed = time.time() - second_start
                if elapsed < 1.0:
                    time.sleep(1.0 - elapsed)
                
                print(f"--- Completed second {second + 1}/{self.duration_seconds} ---")
        
        # Wait a bit for final requests to complete
        print("\n⏳ Waiting for final requests to complete...")
        time.sleep(5)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary."""
        # Collect all results
        results = []
        while not self.results.empty():
            results.append(self.results.get())
        
        if not results:
            print("❌ No results collected!")
            return
        
        # Sort by request ID
        results.sort(key=lambda x: x['id'])
        
        # Calculate statistics
        total_time = time.time() - self.start_time
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        print(f"\n📊 LOAD TEST SUMMARY:")
        print(f"   Total test time: {total_time:.2f} seconds")
        print(f"   Requests sent: {len(results)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        print(f"   Success rate: {len(successful)/len(results)*100:.1f}%")
        
        if successful:
            durations = [r['duration'] for r in successful]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"\n⏱️  RESPONSE TIMES:")
            print(f"   Min: {min_duration:.2f}s")
            print(f"   Max: {max_duration:.2f}s") 
            print(f"   Avg: {avg_duration:.2f}s")
            
            # Show response time distribution
            slow_requests = [r for r in successful if r['duration'] > 5.0]
            if slow_requests:
                print(f"   Slow requests (>5s): {len(slow_requests)}")
        
        print(f"\n🔍 ANALYSIS:")
        if self.endpoint_type == 'sync':
            print("   SYNC endpoint analysis:")
            print("   - High response times indicate thread pool exhaustion")
            print("   - Browser should be slow/unresponsive during test")
            print("   - Failed requests indicate Flask couldn't handle the load")
        else:
            print("   ASYNC endpoint analysis:")
            print("   - Response times should be more consistent")
            print("   - Browser should remain more responsive")
            print("   - Better handling of concurrent load")

def main():
    if len(sys.argv) < 3:
        print("Usage: python load_test.py [sync|async] <requests_per_second> [duration_seconds]")
        print()
        print("Examples:")
        print("  python load_test.py sync 50        # 50 req/s for 10 seconds (default)")
        print("  python load_test.py async 100      # 100 req/s for 10 seconds")  
        print("  python load_test.py sync 30 20     # 30 req/s for 20 seconds")
        print()
        print("Recommended tests:")
        print("  python load_test.py sync 20        # Should overwhelm Flask")
        print("  python load_test.py async 20       # Should handle better")
        sys.exit(1)
    
    endpoint_type = sys.argv[1]
    if endpoint_type not in ['sync', 'async']:
        print("Error: First argument must be 'sync' or 'async'")
        sys.exit(1)
    
    try:
        requests_per_second = int(sys.argv[2])
    except ValueError:
        print("Error: requests_per_second must be an integer")
        sys.exit(1)
    
    duration_seconds = 10  # default
    if len(sys.argv) > 3:
        try:
            duration_seconds = int(sys.argv[3])
        except ValueError:
            print("Error: duration_seconds must be an integer")
            sys.exit(1)
    
    if requests_per_second <= 0 or duration_seconds <= 0:
        print("Error: requests_per_second and duration_seconds must be positive")
        sys.exit(1)
    
    tester = LoadTester(endpoint_type, requests_per_second, duration_seconds)
    tester.run_load_test()

if __name__ == "__main__":
    main()