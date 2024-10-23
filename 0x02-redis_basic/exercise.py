#!/usr/bin/env python3
"""
Create a Redis instance
"""
import redis
from typing import Union, Callable, Optional
import uuid
from functools import wraps

def count_calls(method: Callable) -> Callable:
    """
    A decorator that counts the number of calls to Cache class
    Arg:
      method: the passed method
    return: inner fuunction
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> str:
        """
        Increments the count by 1 everytime the class cache is called
        """
        self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper

def call_history(method: Callable) -> Callable:
    """
    A decorator that stores the history of inputs
    and outputs for a particular function
    Arg:
      method: the passed method
    return: inner fuunction
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> str:
        """
        create input and output list keys
        """
        list1 = method.__qualname__ + ":inputs"
        list2 = method.__qualname__ + ":outputs"
        input_data = f"(\'{args[0]}\',)"
        self._redis.rpush(list1, input_data)
        stored_data_key = method(self, *args, **kwargs)
        self._redis.rpush(list2, stored_data_key)
        return stored_data_key
    return wrapper


def replay(method: Callable) -> None:
    """
    display the history of calls of a particular function
    """
    @wraps(method)
    def wrapper(*args, **kwargs) -> None:
        """
        Display information
        """
        list1_name = method.__qualname__ + ":inputs"
        list2_name = method.__qualname__ + ":ouputs"
        result1 = args[0]._redis.lrange(list1_name, 0, -1)
        result2 = args[0]._redis.lrange(list2_name, 0, -1)

        gen_dict = dict(zip(result1, result2))
        print(f"""
        {method.__qualname__} was called {len(gen_dict.keys())} times:
        """)
        for key, value in gen_dict.items():
            print(f"{method.__qualname__}(*({key},)) -> {value}")
    return wrapper()

class Cache:
    """
    working with the redis server
    """
    def __init__(self) -> None:
        """
        Intialise cache class
        """
        self._redis = redis.Redis()
        self._redis.flushdb()

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        store input data into the redis sever
        Arg:
          data: the input data to store
        return: key(str) for the stored value
        """
        key = str(uuid.uuid4())
        self._redis.set(key, data)
        return key
    
    def get(self, key: str, fn: Optional[callable] = None) -> Union[str, int, float]:
         """
        Get a value from the redis database and convert is in the right form
        Arg:
          key: the key to use
          fn: function to convert the retrieved data to the correct format
        return: the value from the redis database
        """
         data = self._redis.get(key)
         if fn:
            data = fn(data)
         return data
    
    def get_int(data: bytes) -> int:
        """
        convert bytes to int
        Arg:
          data: the data to convert
        return: the new converted data
        """
        return int(data.decode('utf-8'))

    def get_str(data: bytes) -> str:
        """
        convert bytes to str
        Arg:
          data: the data to convert
        return: the new converted data
        """
        return data.decode('utf-8')