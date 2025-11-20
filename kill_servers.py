import subprocess
import time

pids = [24452, 35948, 37072]

for pid in pids:
    try:
        subprocess.run(f"taskkill /F /PID {pid}", shell=True, check=False)
        print(f"Killed PID {pid}")
        time.sleep(0.5)
    except Exception as e:
        print(f"Error killing {pid}: {e}")

print("\nDone!")
