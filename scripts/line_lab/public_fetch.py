"""Bounded concurrent fetch of independent, public, unmetered sources only."""
from concurrent.futures import ThreadPoolExecutor,as_completed


def prefetch(urls,getter,timeout=10,workers=6):
    cache={}
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pending={pool.submit(getter,url,timeout):url for url in dict.fromkeys(urls)}
        for task in as_completed(pending):
            url=pending[task]
            try:cache[url]=(task.result(),None)
            except Exception as exc:cache[url]=(None,exc)
    def fetch(url,timeout=10):
        if url not in cache:return getter(url,timeout)
        value,error=cache[url]
        if error is not None:raise error
        return value
    return fetch
