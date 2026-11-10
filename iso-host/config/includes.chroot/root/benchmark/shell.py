import subprocess

def shell_on_host(cmd: str, check: bool = True, capture: bool = False, timeout: int | None = None):
    return subprocess.run(cmd, shell=True, check=check, timeout=timeout, capture_output=capture, text=True)

def shell_on_guest(handle: str, cmd: str, check: bool = True, capture: bool = False, timeout: int | None = None):
    return subprocess.run(["ssh", handle, cmd], check=check, timeout=timeout, capture_output=capture, text=True)
