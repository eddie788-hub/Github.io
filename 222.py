import os
import pty
import subprocess
import threading
import signal

class ShellSession:
    def __init__(self, cols=120, rows=30):
        self.master_fd, self.slave_fd = pty.openpty()
        self.proc = subprocess.Popen(
            ["bash", "--login"],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            env=os.environ.copy(),
        )
        self.resize(cols, rows)

    def resize(self, cols, rows):
        import fcntl, termios, struct
        fcntl.ioctl(self.master_fd, termios.TIOCSWINSZ,
                    struct.pack("HHHH", rows, cols, 0, 0))

    def read_loop(self, callback):
        def _loop():
            while True:
                try:
                    data = os.read(self.master_fd, 4096)
                    if not data:
                        break
                    callback(data.decode(errors="ignore"))
                except OSError:
                    break
        threading.Thread(target=_loop, daemon=True).start()

    def write(self, cmd: str):
        os.write(self.master_fd, cmd.encode())

    def send_signal(self, sig=signal.SIGINT):
        self.proc.send_signal(sig)

    def close(self):
        self.proc.terminate()
        os.close(self.master_fd)
        os.close(self.slave_fd)