import random


def data_factory(container_count=50, records_count=50000, params_tuple=None):
    data = list()
    record_counter = 0
    if not params_tuple:
        params_tuple = (1, 100)

    for container_number in range(container_count):
        cur_records_count = random.randint(round(records_count / 1.5), records_count)
        records = list()
        for _ in range(cur_records_count):
            records.append({
                'id': record_counter,
                'size': random.randint(*params_tuple),
                'average_load': random.randint(*params_tuple),
            })
            record_counter += 1
        data.append({
            'name': container_number,
            'records': records
        })

    return data
