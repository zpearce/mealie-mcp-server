from typing import Any, Optional


class ParamBuilder:
    def __init__(self, param_dict: Optional[dict[str, Any]] = None) -> None:
        self.param_dict = param_dict

    def add(self, key: str, value: Optional[Any]) -> None:
        if key in self.param_dict:
            raise ValueError(f"Key '{key}' already exists in the parameter dictionary.")
        self.param_dict[key] = value

    def build(self) -> dict:
        output = {}
        for k, v in self.param_dict.items():
            if v is None:
                continue
            if isinstance(v, list):
                output[k] = ",".join(v)
            else:
                output[k] = v
        return output
