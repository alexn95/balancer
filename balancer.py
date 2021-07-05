import numpy as np


SIZE = 0
LOAD = 1


class Conditions:

	def __init__(self, deviations):
		self.deviations = deviations

	def _target_weight(self, target):
		return abs(target[SIZE]) + abs(target[LOAD])

	def donate_return_condition(self, target):
		return target[SIZE] < 0 and target[LOAD] < 0

	def donate_break_condition(self, target, new_target):
		return self._target_weight(new_target) >= self._target_weight(target)

	def receive_return_condition(self, target):
		return target[SIZE] > 0 and target[LOAD] > 0

	def receive_break_condition(self, target, new_target):
		return self._target_weight(new_target) >= self._target_weight(target)


class PickUpConditions(Conditions):
	def __init__(self, deviations, receive_param):
		super().__init__(deviations)
		self.receive_param = receive_param

	def donate_return_condition(self, target):
		return target[self.receive_param] < 0

	def donate_break_condition(self, target, new_target):
		return new_target[self.receive_param] < 0

	def receive_return_condition(self, target):
		return target[self.receive_param] > 0

	def receive_break_condition(self, target, new_target):
		return new_target[self.receive_param] > 0


class Balancer:
	
	def __init__(self, free_records, max_size_deviation, max_load_deviation):
		self.free_records = free_records
		self.max_size_deviation = max_size_deviation
		self.max_load_deviation = max_load_deviation
		self.deviations = (self.max_size_deviation, self.max_load_deviation)
		self.receive_count = 0
		self.donate_count = 0
		self.stats = {
			'default_donate': 0,
			'default_receive': 0,
			'pick_up_donate': 0,
			'pick_up_receive': 0,
		}

	def _closest_record(self, target, nodes) -> int:
		deltas = nodes - target
		dist_2 = np.einsum('ij,ij->i', deltas, deltas)
		return int(np.argmin(dist_2))

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

	def donate(self, container, conditions: Conditions):
		target = (container['size_diff'], container['load_diff'])
		if conditions.donate_return_condition(target):
			return

		records = np.asarray([(record['size'], record['average_load']) for record in container['records']])

		while len(records):
			record_index = self._closest_record(target, records)
			record = records[record_index]
			new_target = (target[0] - record[0], target[1] - record[1])

			if conditions.donate_break_condition(target, new_target):
				break

			target = new_target
			records = np.delete(records, record_index, axis=0)
			self.free_records.append(container['records'].pop(record_index))
			self.donate_count += 1
			if isinstance(conditions, PickUpConditions):
				self.stats['pick_up_donate'] += 1
			else:
				self.stats['default_donate'] += 1

		container['size_diff'], container['load_diff'] = target

	def receive(self, container, conditions: Conditions):
		target = (container['size_diff'], container['load_diff'])
		if conditions.receive_return_condition(target):
			return

		records = np.asarray([(record['size'], record['average_load']) for record in self.free_records])

		while len(records):
			record_index = self._closest_record(target, records)
			record = records[record_index]
			new_target = (target[0] + record[0], target[1] + record[1])

			if conditions.receive_break_condition(target, new_target):
				break

			target = new_target
			records = np.delete(records, record_index, axis=0)
			container['records'].append(self.free_records.pop(record_index))
			self.receive_count += 1
			if isinstance(conditions, PickUpConditions):
				self.stats['pick_up_receive'] += 1
			else:
				self.stats['default_receive'] += 1

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
