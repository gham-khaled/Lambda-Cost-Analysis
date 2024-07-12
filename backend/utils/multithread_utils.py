import concurrent.futures


def multi_thread(function, iterators, max_workers=50, *args, **kwargs):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(function, iterator, *args, **kwargs) for iterator in iterators]

    for future in concurrent.futures.as_completed(futures):
        results.append(future.result())

    return results
