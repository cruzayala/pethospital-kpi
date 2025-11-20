"""Kill all processes listening on port 8000"""
import psutil

killed = []
for proc in psutil.process_iter(['pid', 'name']):
    try:
        connections = proc.connections()
        for conn in connections:
            if hasattr(conn, 'laddr') and conn.laddr.port == 8000:
                print(f"Killing PID {proc.pid} ({proc.info['name']})")
                proc.kill()
                killed.append(proc.pid)
                break
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess, AttributeError):
        pass

if killed:
    print(f"\nKilled {len(killed)} processes: {killed}")
else:
    print("No processes found on port 8000")
