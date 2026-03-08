from functools import wraps

def schema(method):
    @wraps(method)
    def wrapper(self, *args, **kwargs):

        if not getattr(self, "_field_mapping", None):
            return method(self, *args, **kwargs)

        def map_dict(data: dict):
            return {
                self._field_mapping.get(k, k): v
                for k, v in data.items()
            }

        # Map records (list or dict)
        if "records" in kwargs and kwargs["records"] is not None:
            records = kwargs["records"]
            if isinstance(records, list):
                kwargs["records"] = [map_dict(r) for r in records]
            elif isinstance(records, dict):
                kwargs["records"] = map_dict(records)

        # Map params
        if "params" in kwargs and kwargs["params"] is not None:
            kwargs["params"] = map_dict(kwargs["params"])

        # Map unique_key
        if "unique_key" in kwargs and kwargs["unique_key"] is not None:
            kwargs["unique_key"] = [
                self._field_mapping.get(k, k)
                for k in kwargs["unique_key"]
            ]

        return method(self, *args, **kwargs)

    return wrapper