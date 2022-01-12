import os.path
import json
import subprocess
from collections import defaultdict

class ArgumentsParser:
    def __init__(self, argv):
        self.argv = argv

    def get_arg_index(self, arg_name):
        return self.argv.index("--" + arg_name) + 1

    def get_arg_value(self, arg_name, cast=None):
        index = self.get_arg_index(self.argv, "--" + arg_name)
        if cast is None:
            return json.loads(self.argv[index])
        else:
            return cast(json.loads(self.argv[index]))

    def get_arg_values(self, arg_name, next_arg_name=None, cast=None):
        start = self.get_arg_index(self.argv, arg_name)
        stop = self.get_arg_index(self.argv, next_arg_name) if next_arg_name is not None else len(self.argv)
        values = []
        for i in range(start, stop):
            if cast is None:        
                values.append(json.loads(self.argv[i]))
            else:
                values.append(cast(json.loads(self.argv[i])))
        return values


class CommandCaller:
    def __init__(self, script_filepath) -> None:
        directory = script_filepath.parent
        self.command_path = os.path.join(directory, "command.py")
        self.expression =  ""
        self.expression_built 
        self.args = defaultdict(list)

    def build_expression(self):
        self.expression = "blender --python " + json.dumps(self.command_path) + " --"
        # defaultdic is ordered so we can do this reliably https://stackoverflow.com/a/52174324/7092409        
        for arg in self.args.keys():            
            self.expression += " --" + json.dumps(arg)
            for value in self.args[arg]:
                self.expression += " " + json.dumps(value)

    def add_arg_value(self, arg_name, value):
        self.args[arg_name].append(value)

    def call(self):
        self.build_expression()
        subprocess.call(self.expression)