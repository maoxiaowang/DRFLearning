import asyncio
import re


async def run_command(shell_cmd, html=False) -> (int, str):
    proc = await asyncio.create_subprocess_shell(
        shell_cmd,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )

    stdout, stderr = await proc.communicate()
    stdout = stdout.decode()
    if html:
        stdout = re.sub(r'\n', '<br>', stdout)
    return proc.returncode, stdout


async def ping(address) -> (bool, str):
    code, output = await run_command(f'ping {address} -c 1')
    succeeded = True if code == 0 else False
    res = re.findall(r'icmp_seq=1.*?time=([\d|.]+\s(ms|s))', output)
    delay = res[0][0] if res else 'Unknown'
    return succeeded, delay
