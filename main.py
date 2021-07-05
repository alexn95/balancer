from balancer import Balancer, prepare_data, Conditions, PickUpConditions, SIZE, LOAD
from data_factory import data_factory
from helper import print_status, timer


in_data = data_factory(
    params_tuple=(1, 100),
    container_count=50,
    records_count=10000,
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
    print(output_stats)

    balancer = Balancer(list(), max_size_deviation, max_load_deviation)
    deviations = (max_size_deviation, max_load_deviation)
    print_status(containers, output_stats, balancer)

    conditions = Conditions(deviations)
    for container in containers:
        balancer.donate(container, conditions)
        balancer.receive(container, conditions)

    if balancer.is_complete(containers):
        print_status(containers, output_stats, balancer)
        return

    print_status(containers, output_stats, balancer)

    size_conditions = PickUpConditions(deviations, SIZE)
    load_conditions = PickUpConditions(deviations, LOAD)

    for container in containers:
        balancer.donate(container, size_conditions)
        balancer.donate(container, load_conditions)

        balancer.receive(container, size_conditions)
        balancer.receive(container, load_conditions)

        if balancer.is_complete(containers):
            print_status(containers, output_stats, balancer)
            return

    print_status(containers, output_stats, balancer)

    return containers


rebalance(in_data, 5)
