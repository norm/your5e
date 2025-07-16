# parser returns objects, tests compare the dict form
def into_dicts(result):
    return [item.asdict() if hasattr(item, "asdict") else item for item in result]
