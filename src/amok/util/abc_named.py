from abc import ABC

class ABC_named(ABC):
	name: str
	
	def __init_subclass__(cls, name = None, **kwargs):
		super().__init_subclass__(**kwargs)
		if ABC_named in cls.__bases__:
			cls._registry: dict[str, type] = {}
		if name is not None:
			cls.name = name
			cls._registry[name] = cls
	
	@classmethod
	def registry(cls):
		return cls._registry
		# return frozendict(cls._registry)
