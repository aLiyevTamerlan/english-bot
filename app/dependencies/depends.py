from functools import wraps
from inspect import isawaitable, signature, Parameter
from typing import Callable, AsyncGenerator


class Depends:
    def __init__(self, dependency: Callable):
        self.dependency = dependency

    def __call__(self):
        return self.dependency


def inject_dependencies(handler_func: Callable) -> Callable:
    @wraps(handler_func)
    async def wrapper(update, context, *args, **kwargs):
        async def resolve_dependency(dependency_func, parent_kwargs=None):
            # Prepare kwargs to pass to the dependency
            dep_kwargs = parent_kwargs or {}
            dep_sig = signature(dependency_func)
            
            # Add update and context if the dependency needs them
            if 'update' in dep_sig.parameters:
                dep_kwargs['update'] = update
            if 'context' in dep_sig.parameters:
                dep_kwargs['context'] = context
            
            # Resolve nested dependencies
            for param_name, param in dep_sig.parameters.items():
                if (param.default is not Parameter.empty and 
                    isinstance(param.default, Depends) and 
                    param_name not in dep_kwargs):
                    nested_dep_func = param.default.dependency
                    dep_kwargs[param_name] = await resolve_dependency(nested_dep_func)
            
            # Execute the dependency with resolved parameters
            dep_result = dependency_func(**dep_kwargs)
            
            # Handle async generator
            if hasattr(dep_result, '__aiter__'):
                async for dep_value in dep_result:
                    return dep_value
            # Handle coroutines
            elif isawaitable(dep_result):
                return await dep_result
            # Handle regular values
            else:
                return dep_result
        
        # Resolve dependencies for handler function
        sig = signature(handler_func)
        deps_to_inject = {}
        
        for param_name, param in sig.parameters.items():
            if param.default is not Parameter.empty and isinstance(param.default, Depends):
                dependency_func = param.default.dependency
                deps_to_inject[param_name] = await resolve_dependency(dependency_func)
        
        return await handler_func(update, context, **deps_to_inject)
    
    return wrapper




# def inject_dependencies(handler_func: Callable) -> Callable:
#     @wraps(handler_func)
#     async def wrapper(update, context, *args, **kwargs):
#         sig = signature(handler_func)
#         deps_to_inject = {}
#         for param_name, param in sig.parameters.items():
#             ...
#             # if param_name in ('update', 'context'):
#             #     continue
#             # print(param.default)
#             if param.default is not Parameter.empty and isinstance(param.default, Depends):
#                 dep_gen = param.default.dependency(update, context)
#                 if hasattr(dep_gen, '__aiter__'):
#                     async for dep_value in dep_gen:
#                         deps_to_inject[param_name] = dep_value
#                         break

        
#         return await handler_func(update, context, **deps_to_inject)
    
#     return wrapper