import psutil
from datetime import datetime

def ps(top: int = 10):
    procs = []
    for p in psutil.process_iter(["pid", "name", "cpu_percent", "memory_percent"]):
        try:
            info = p.info
            procs.append(info)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    procs.sort(key=lambda x: (x["cpu_percent"] or 0.0), reverse=True)
    procs = procs[:top]
    lines = ["PID   CPU%   MEM%   NAME"]
    for i in procs:
        lines.append(f'{i["pid"]:<5} {i["cpu_percent"] or 0:>5.1f} {i["memory_percent"] or 0:>6.2f}  {i["name"]}')
    return "\n".join(lines)

def cpu():
    return f"CPU percent: {psutil.cpu_percent(interval=0.2)}%  |  Cores: {psutil.cpu_count(logical=True)}"

def mem():
    v = psutil.virtual_memory()
    return f"Memory: {round(v.used/1e9,2)}GB / {round(v.total/1e9,2)}GB  ({v.percent}%)"

def banner():
    return f"PyTerminal ready  |  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
