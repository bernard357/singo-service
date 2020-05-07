from copy import deepcopy


class Store:

    def __init__(self):
        self.records = {}

    def get(self, id, default=None):
        return deepcopy(self.records.get(id, default))

    def put(self, id, **kwargs):
        record = deepcopy(kwargs)
        record['id'] = id
        self.records[id] = record

    def delete(self, id):
        self.records.pop(id, None)

    def ids(self):
        return list(self.records.keys())

    def ids_by(self, key, reverse=True):
        return sorted(list(self.records.keys()),
                      key=lambda id: self.records[id][key],
                      reverse=reverse)
