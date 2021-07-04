from balancer import Balancer, prepare_data
from data_factory import data_factory
from helper import print_status, timer


in_data = data_factory(
    params_tuple=(1, 100),
    container_count=50,
    records_count=50000,
)


@timer
def rebalance(containers, max_percent_deviation=10):
    avg_size, avg_load, max_size_deviation, max_load_deviation = \
        prepare_data(containers, max_percent_deviation)
    output_stats = {
        'avg_size': avg_size,
        'avg_load': avg_load,
        'max_size_deviation': max_size_deviation,
        'max_load_deviation': max_load_deviation,
    }

    balancer = Balancer(list(), max_size_deviation, max_load_deviation)
    print_status(containers, output_stats, balancer)

    for container in containers:
        balancer.donate(container)
        balancer.receive(container)

    if balancer.is_complete(containers):
        print_status(containers, output_stats, balancer)
        return

    # Раскладываем оставшиеся записи по контейнерам
    for container in containers:
        balancer.receive(container, True, 0)
        balancer.receive(container, True, 1)

        if balancer.is_complete(containers):
            print_status(containers, output_stats, balancer)
            return

    print_status(containers, output_stats, balancer)

    return containers


rebalance(in_data, 10)
