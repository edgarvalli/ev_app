import sys, inspect

__import__('app.modules2.base')

mod = sys.modules['app.modules2.base']
members = [member for member in inspect.getmembers(mod, inspect.isclass)]

name, obj = members[0]

method = getattr(obj, 'render2')

print(method())