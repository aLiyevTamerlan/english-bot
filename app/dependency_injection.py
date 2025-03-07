from functools import wraps
from inspect import signature, Parameter
import inspect
from typing import Callable, Any, AsyncGenerator

class Depends:
    def __init__(self, dependency: Callable[..., AsyncGenerator]):
        self.dependency = dependency

    def __call__(self):
        return self


def inject_dependencies(handler_func: Callable) -> Callable:
    @wraps(handler_func)
    async def wrapper(update, context, *args, **kwargs):
        sig = signature(handler_func)
        deps_to_inject = {}
        
        for param_name, param in sig.parameters.items():

            if param_name in ('update', 'context'):
                continue
                

            if param.default is not Parameter.empty and isinstance(param.default, Depends):
                dep_gen = param.default.dependency()

                async for dep_value in dep_gen:

                    deps_to_inject[param_name] = dep_value
                    print(deps_to_inject)
                    break
        
        return await handler_func(update, context, **deps_to_inject)
    
    return wrapper