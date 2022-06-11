from asset_browser_utilities.core.console.parser import ArgumentsParser

from asset_browser_utilities.module.asset.test import mark, unmark, copy
from asset_browser_utilities.module.author.test import set

from inspect import getmembers, isfunction

_test_modules = (
    mark,
    unmark,
    copy,
    set,
)


if __name__ == "__main__":
    parser = ArgumentsParser()
    source_filepath = parser.get_arg_value("source_filepath")
    tests = 0
    for module in _test_modules:
        for func_name, func in getmembers(module, isfunction):
            if str(func_name).startswith("test"):
                print(f"~~~ {func.__name__} from {module.__name__} ~~~")
                func(source_filepath)
                tests += 1
    print(f"\n~~~ All {tests} tests have sucessfully completed ~~~")
