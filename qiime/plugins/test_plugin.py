
from . import qiime

@qiime.register_method("some method")
def some_method(a: int, b: str) -> dict:
	pass
