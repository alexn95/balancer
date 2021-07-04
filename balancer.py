import numpy as np


class Balancer:
	
	def __init__(self, free_records, max_size_deviation, max_load_deviation):
		self.free_records = free_records
		self.max_size_deviation = max_size_deviation
		self.max_load_deviation = max_load_deviation
		self.deviations = (self.max_size_deviation, self.max_load_deviation)
		self.receive_count = 0
		self.donate_count = 0
		self.stats = {
			'donate': 0,
			'receive': 0,
			'soft_donate': 0,
			'soft_receive': 0,
		}

	def _closest_record(self, target, nodes) -> int:
		deltas = nodes - target
		dist_2 = np.einsum('ij,ij->i', deltas, deltas)
		return int(np.argmin(dist_2))

	def _target_weight(self, target):
		return abs(target[0]) + abs(target[1])

	def is_complete(self, containers):
		if self.free_records:
			return False
		for container in containers:
			if abs(container['size_diff']) > self.max_size_deviation:
				return False
			if abs(container['load_diff']) > self.max_load_deviation:
				return False

		print('COMPLETE')
		return True

	def donate(self, container, soft=False, param=0):
		target = (container['size_diff'], container['load_diff'])
		if soft and target[param] < self.max_load_deviation:
			return
		if not soft and target[0] < 0 and target[1] < 0:
			return

		records = np.asarray([(record['size'], record['average_load']) for record in container['records']])

		while len(records):
			record_index = self._closest_record(target, records)
			record = records[record_index]
			new_target = (target[0] - record[0], target[1] - record[1])

			if not soft and self._target_weight(new_target) >= self._target_weight(target):
				break

			if soft and target[param] < self.deviations[param]:
				break

			target = new_target
			records = np.delete(records, record_index, axis=0)
			self.free_records.append(container['records'].pop(record_index))
			self.donate_count += 1
			if soft:
				self.stats['soft_donate'] += 1
			else:
				self.stats['donate'] += 1

		container['size_diff'], container['load_diff'] = target

	def receive(self, container, soft=False, param=0):
		target = (container['size_diff'], container['load_diff'])
		if soft and target[param] > 0:
			return
		if not soft and target[0] > 0 and target[1] > 0:
			return

		records = np.asarray([(record['size'], record['average_load']) for record in self.free_records])

		while len(records):
			record_index = self._closest_record(target, records)
			record = records[record_index]
			new_target = (target[0] + record[0], target[1] + record[1])

			if not soft and self._target_weight(new_target) >= self._target_weight(target):
				break

			if soft and target[param] > 0:
				break

			target = new_target
			records = np.delete(records, record_index, axis=0)
			container['records'].append(self.free_records.pop(record_index))
			self.receive_count += 1
			if soft:
				self.stats['soft_receive'] += 1
			else:
				self.stats['receive'] += 1

		container['size_diff'], container['load_diff'] = target


def prepare_data(containers, max_percent_deviation):
	total_size = 0
	total_load = 0
	container_count = len(containers)

	# Сумма и среднее по каждому контейнеру
	for container in containers:
		container['size_sum'] = sum([record['size'] for record in container['records']])
		container['load_sum'] = sum([record['average_load'] for record in container['records']])

		total_size += container['size_sum']
		total_load += container['load_sum']

	# Средние суммы по всем контейнерам вместе
	avg_size = total_size // container_count
	avg_load = total_load // container_count

	# Разница среднего каждого контейнера от общего среднего
	for container in containers:
		container['size_diff'] = container['size_sum'] - avg_size
		container['load_diff'] = container['load_sum'] - avg_load

	# Максимальное доступное отклонение
	max_size_deviation = avg_size * max_percent_deviation / 100
	max_load_deviation = avg_load * max_percent_deviation / 100

	return avg_size, avg_load, max_size_deviation, max_load_deviation
