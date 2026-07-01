import os
from concurrent.futures import ThreadPoolExecutor, Future
from typing import Any, Callable


class ConcurrentTaskExecutor:
    """后台任务线程池执行器。

    历史版本只有串行锁，所以外部导出名仍叫 task_serial_executor/SerialTaskExecutor；
    当前实现允许有限并发，默认 3 个 worker，可通过 TASK_MAX_WORKERS 调整。
    """

    def __init__(self, max_workers: int | None = None):
        self._max_workers = max_workers or int(os.getenv("TASK_MAX_WORKERS", "3"))
        self._pool = ThreadPoolExecutor(max_workers=self._max_workers)

    def run(self, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """提交任务并等待结果。

        BackgroundTasks 已经把执行挪到请求返回之后，这里等待 future 不会阻塞用户的
        generate_note 请求，只会占用后台工作线程。
        """
        future: Future = self._pool.submit(fn, *args, **kwargs)
        return future.result()

    def shutdown(self, wait: bool = True):
        self._pool.shutdown(wait=wait)


# 保持向后兼容的导出名
SerialTaskExecutor = ConcurrentTaskExecutor
task_serial_executor = ConcurrentTaskExecutor()
