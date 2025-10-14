"""Multithreading utility for parallel execution."""

import concurrent.futures
from typing import Any, Callable, Iterable


def multi_thread(
    function: Callable[..., Any],
    iterators: Iterable[Any],
    max_workers: int = 50,
    *args: Any,
    **kwargs: Any,
) -> list[Any]:
    """
    Execute function on multiple items in parallel.

    Parameters
    ----------
    function : Callable
        Function to execute
    iterators : Iterable
        Items to process
    max_workers : int, default=50
        Maximum number of worker threads
    *args : Any
        Additional positional arguments for function
    **kwargs : Any
        Additional keyword arguments for function

    Returns
    -------
    list
        Results from all executions
    """
    results: list[Any] = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [
            executor.submit(function, iterator, *args, **kwargs)
            for iterator in iterators
        ]

    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

    return results
