#!/usr/bin/env python3
"""
Maximum concurrency load testing script to overwhelm Flask.
Uses unlimited threads and async requests for maximum rate.

Usage:
  python load_test.py sync 1000                           # 1000 requests via nginx
  python load_test.py sync 1000 --direct                  # 1000 requests direct to Flask
  python load_test.py async 500 --direct                  # 500 async requests direct to Flask
  python load_test.py sync 100 --duration 30              # 100 req/s for 30 seconds
  python load_test.py sync 50 --duration 60 --direct      # 50 req/s for 60s direct to Flask
"""

import sys
import time
import asyncio
import aiohttp
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import queue
import argparse

class MaxLoadTester:
    def __init__(self, endpoint_type, concurrent_requests, direct=False, duration=None):
        self.endpoint_type = endpoint_type
        self.concurrent_requests = concurrent_requests
        self.duration = duration  # Duration in seconds for sustained load
        
        # Set base URL - direct Flask or via nginx
        if direct:
            self.base_url = "http://127.0.0.1:5000"
            print(f"🎯 DIRECT MODE: Targeting Flask directly (bypassing nginx)")
        else:
            self.base_url = "http://localhost:80"
            print(f"🌐 NGINX MODE: Targeting Flask via nginx reverse proxy")
        
        # Set up endpoint
        if endpoint_type == 'sync':
            self.url = f"{self.base_url}/call-tornado"
        elif endpoint_type == 'async':
            self.url = f"{self.base_url}/call-tornado-async"
        else:
            raise ValueError("endpoint_type must be 'sync' or 'async'")
        
        # Results tracking
        self.results = []
        self.start_time = None
        self.lock = threading.Lock()
        
    async def async_request(self, session, request_id):
        """Make async HTTP request for maximum performance."""
        request_start = time.time()
        try:
            async with session.post(
                self.url,
                data={'endpoint': '/'},
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                await response.text()
                request_end = time.time()
                duration = request_end - request_start
                time_since_start = request_start - self.start_time
                
                result = {
                    'id': request_id,
                    'status_code': response.status,
                    'duration': duration,
                    'time_since_start': time_since_start,
                    'success': response.status == 200
                }
                
                with self.lock:
                    self.results.append(result)
                
                # Reduced logging for performance
                if request_id % 100 == 0:
                    print(f"Request {request_id:4d}: {response.status} in {duration:.2f}s")
                
        except Exception as e:
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
            
            with self.lock:
                self.results.append(result)
            
            if request_id % 100 == 0:
                print(f"Request {request_id:4d}: FAILED in {duration:.2f}s")
    
    async def run_async_burst(self):
        """Use asyncio for unlimited request rate."""
        print(f"🚀 Launching {self.concurrent_requests} requests with MAXIMUM concurrency...")
        
        # Unlimited connection pooling for maximum rate
        connector = aiohttp.TCPConnector(
            limit=0,  # No limit on total connections
            limit_per_host=0,  # No limit per host
            keepalive_timeout=120,
            enable_cleanup_closed=True,
            force_close=False,
            use_dns_cache=True
        )
        
        timeout = aiohttp.ClientTimeout(total=120, connect=10)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout
        ) as session:
            # Create ALL tasks immediately for maximum burst
            print(f"📦 Creating {self.concurrent_requests} async tasks...")
            tasks = []
            task_start = time.time()
            
            for request_id in range(1, self.concurrent_requests + 1):
                task = asyncio.create_task(
                    self.async_request(session, request_id)
                )
                tasks.append(task)
            
            task_creation_time = time.time() - task_start
            submission_time = time.time() - self.start_time
            
            print(f"✅ {self.concurrent_requests} tasks created in {task_creation_time:.3f}s")
            print(f"🚀 All requests launching in {submission_time:.3f}s")
            print("⏳ Maximum rate burst in progress...\n")
            
            # Wait for completion with progress
            completed = 0
            for task in asyncio.as_completed(tasks):
                await task
                completed += 1
                if completed % 200 == 0 or completed == self.concurrent_requests:
                    elapsed = time.time() - self.start_time
                    rate = completed / elapsed if elapsed > 0 else 0
                    print(f"Progress: {completed}/{self.concurrent_requests} ({rate:.0f} req/s)")
    
    async def run_sustained_load(self):
        """Run sustained load for specified duration."""
        print(f"🚀 Running sustained load for {self.duration} seconds...")
        
        connector = aiohttp.TCPConnector(
            limit=0,
            limit_per_host=0,
            keepalive_timeout=120,
            enable_cleanup_closed=True
        )
        
        timeout = aiohttp.ClientTimeout(total=120, connect=10)
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
            request_id = 1
            end_time = self.start_time + self.duration
            
            while time.time() < end_time:
                # Launch requests in batches to maintain sustained load
                batch_size = min(self.concurrent_requests, 50)  # Reasonable batch size
                tasks = []
                
                for _ in range(batch_size):
                    if time.time() >= end_time:
                        break
                    task = asyncio.create_task(self.async_request(session, request_id))
                    tasks.append(task)
                    request_id += 1
                
                # Don't wait for batch completion - keep firing
                if tasks:
                    # Fire and forget - don't wait
                    pass
                
                # Small delay to prevent overwhelming the system
                await asyncio.sleep(0.1)
                
                # Show progress
                if request_id % 100 == 0:
                    elapsed = time.time() - self.start_time
                    remaining = self.duration - elapsed
                    print(f"Sustained load: {request_id} requests sent, {remaining:.0f}s remaining")
            
            print(f"⏳ Duration complete, waiting for final responses...")
            # Give some time for final responses
            await asyncio.sleep(5)

    def run_unlimited_load_test(self):
        """Execute load test - burst or sustained based on duration."""
        test_type = "SUSTAINED" if self.duration else "BURST"
        print(f"💥 {self.endpoint_type.upper()} {test_type} LOAD TEST")
        print(f"   Target: {self.url}")
        
        if self.duration:
            print(f"   Mode: Sustained load for {self.duration} seconds")
            print(f"   Rate: ~{self.concurrent_requests} requests/batch every 0.1s")
        else:
            print(f"   Mode: Single burst of {self.concurrent_requests} requests")
            print(f"   Strategy: All requests fired simultaneously")
        print()
        
        if self.endpoint_type == 'sync':
            print("🔥 SYNC ENDPOINT - MAXIMUM ATTACK!")
            print("   Every request blocks a Flask thread")
            test_url = self.base_url if self.base_url != "http://localhost:80" else "http://localhost:5000"
            print(f"   🌐 TEST NOW: Open {test_url} in browser")
            print("   📱 Expect unresponsiveness")
        else:
            print("⚡ ASYNC ENDPOINT - ASYNC STRESS TEST!")
            print("   Testing Flask's async handling limits") 
            test_url = self.base_url if self.base_url != "http://localhost:80" else "http://localhost:5000"
            print(f"   🌐 TEST NOW: Open {test_url} in browser")
            print("   📱 Should be more responsive than sync")
        
        print(f"\n🚀 Starting {test_type} test at {time.strftime('%H:%M:%S')}...")
        print("💡 OPEN YOUR BROWSER NOW!\n")
        
        self.start_time = time.time()
        
        try:
            if self.duration:
                asyncio.run(self.run_sustained_load())
            else:
                asyncio.run(self.run_async_burst())
        except KeyboardInterrupt:
            print("\n🛑 Test interrupted")
        
        total_time = time.time() - self.start_time
        print(f"\n🏁 Test completed in {total_time:.2f}s")
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive results."""
        if not self.results:
            print("❌ No results collected!")
            return
        
        self.results.sort(key=lambda x: x['id'])
        
        total_time = time.time() - self.start_time
        successful = [r for r in self.results if r['success']]
        failed = [r for r in self.results if not r['success']]
        
        print(f"\n📊 UNLIMITED RATE TEST RESULTS:")
        print(f"   Total time: {total_time:.2f}s")
        print(f"   Requests sent: {len(self.results)}")
        print(f"   Successful: {len(successful)}")
        print(f"   Failed: {len(failed)}")
        
        if len(self.results) > 0:
            success_rate = len(successful) / len(self.results) * 100
            actual_rate = len(self.results) / total_time if total_time > 0 else 0
            print(f"   Success rate: {success_rate:.1f}%")
            print(f"   Achieved rate: {actual_rate:.0f} requests/second")
            
        if successful:
            durations = [r['duration'] for r in successful]
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            print(f"\n⏱️  RESPONSE TIMES:")
            print(f"   Min: {min_duration:.2f}s | Max: {max_duration:.2f}s | Avg: {avg_duration:.2f}s")
            
            # Response time analysis
            ranges = [
                (0, 3, "Fast (<3s)"),
                (3, 10, "Slow (3-10s)"), 
                (10, 30, "Very slow (10-30s)"),
                (30, float('inf'), "Extremely slow (>30s)")
            ]
            
            for min_t, max_t, label in ranges:
                count = len([r for r in successful if min_t <= r['duration'] < max_t])
                if count > 0:
                    print(f"   {label}: {count}")
        
        print(f"\n🔍 FLASK CRUSHING ANALYSIS:")
        target_desc = "direct Flask" if "5000" in self.base_url else "Flask via nginx"
        
        if self.endpoint_type == 'sync':
            print(f"   SYNC results against {target_desc}:")
            if len(failed) > 0:
                print(f"   🎯 {len(failed)} failures = Flask overwhelmed!")
            if successful and max([r['duration'] for r in successful]) > 10:
                print("   🎯 Long response times = severe blocking!")
            print("   🌐 Browser test results?")
        else:
            print(f"   ASYNC results against {target_desc}:")
            failure_rate = len(failed) / len(self.results) if self.results else 0
            if failure_rate < 0.3:
                print("   ✅ Lower failure rate shows async benefits")
            print("   🌐 Browser more responsive than sync test?")

def main():
    parser = argparse.ArgumentParser(description='Maximum rate Flask load tester')
    parser.add_argument('endpoint', choices=['sync', 'async'], help='Endpoint type to test')
    parser.add_argument('requests', type=int, help='Number of concurrent requests (or requests/batch if using --duration)')
    parser.add_argument('--direct', action='store_true', help='Target Flask directly (port 5000) instead of nginx (port 80)')
    parser.add_argument('--duration', type=int, help='Duration in seconds for sustained load test')
    
    args = parser.parse_args()
    
    if args.requests <= 0:
        print("Error: Number of requests must be positive")
        sys.exit(1)
    
    if args.requests > 50000:
        print("Error: Maximum 50,000 requests (system protection)")
        sys.exit(1)
    
    if args.requests > 5000:
        print(f"⚠️  WARNING: {args.requests} requests may overwhelm your entire system")
        response = input("Continue with extreme test? (y/N): ")
        if response.lower() != 'y':
            sys.exit(1)
    
    print("🔥 MAXIMUM RATE LOAD TESTER")
    print("Flask should be running in single-threaded mode for best demo")
    if args.direct:
        print("Direct mode: Make sure Flask is accessible on port 5000")
    else:
        print("Nginx mode: Testing through reverse proxy on port 80")
    print()
    
    tester = MaxLoadTester(args.endpoint, args.requests, args.direct, args.duration)
    tester.run_unlimited_load_test()

if __name__ == "__main__":
    main()