from functools import reduce
from typing import TypeVar, Optional

T = TypeVar('T')

def coalesce(*arg:Optional[T]) -> T:
    return reduce(lambda x, y: x if x is not None else y, arg)

def clamp(n:T, minn:T, maxn:T) -> T:
    return max(min(maxn, n), minn)
