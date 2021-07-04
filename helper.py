import timeit


def timer(func):
    def wrapper(*args, **kwargs):
        start = timeit.default_timer()
        func_response = func(*args, **kwargs)
        stop = timeit.default_timer()
        print('Time: ', stop - start)
        return func_response

    return wrapper


def validate_result(result, stats):
    for container in result:
        if abs(container['size_diff']) > stats['max_size_deviation']:
            print(f'Несбалансирован по размеру: {container["name"]}')
            print(f'Отклонение по размеру: {container["size_diff"]}. Допустимо: {stats["max_size_deviation"]}')
            print()

        if abs(container['load_diff']) > stats['max_load_deviation']:
            print(f'Несбалансирован по нагрузке: {container["name"]}')
            print(f'Отклонение по нагрузке: {container["load_diff"]}. Допустимо: {stats["max_load_deviation"]}')
            print()


def print_stats(stats):
    print(f'Максимальное доступное отклонение размера {stats["max_size_deviation"]}')
    print(f'Максимальное доступное отклонение нагрузки {stats["max_load_deviation"]}')
    print()

    print(f'Средний вес контейнера {stats["avg_size"]}')
    print(f'Средняя загрузка контейнера {stats["avg_load"]}')
    print()


def print_diffs(containers):
    for container in containers:
        print(container['name'])
        print(f'Отклонение по размеру: {container["size_diff"]}')
        print(f'Отклонение по нагрузке: {container["load_diff"]}')
        print()

    print()


def print_status(containers, stats, balancer):
    size_disbalance = 0
    load_disbalance = 0
    not_balanced = []
    for container in containers:
        if abs(container['size_diff']) > stats['max_size_deviation']:
            size_disbalance += 1

        if abs(container['load_diff']) > stats['max_load_deviation']:
            load_disbalance += 1
            not_balanced.append((container['size_diff'], container['load_diff']))

    print(f'Несбалансированно по размеру: {size_disbalance}')
    print(f'Несбалансированно по нагрузке: {load_disbalance}')
    print(f'Несбалансированные контейнеры: {not_balanced}')
    print(f'free_records: {len(balancer.free_records)}')
    print(f'pop_count: {balancer.donate_count}')
    print(f'insert_count: {balancer.receive_count}')
    print(f'stats: {balancer.stats}')
    print()

