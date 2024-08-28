import os

from jinja2 import Template

from topcoder_problems.types import (TOPCODER_LIST_TYPES, TopCoderProblem,
                                     TopCoderType)
from topcoder_problems.utils import PROJECT_ROOT

method_boilerplate = """
\"\"\"
{{ description }}
\"\"\"

{% if needs_import %}
from typing import List
{% endif %}

def {{ func_name }}({{ args }}) -> {{ return_type }}:
    pass
"""

test_boilerplate = """
from .{{ func_name }} import {{ func_name }}

{% for test in test_cases %}
def test_{{ func_name }}_{{ loop.index0 }}():
    inputs = {{ test.inputs }}
    expected_output = {{ test.output }}

    assert {{ func_name }}(*inputs) == expected_output

{% endfor %}
"""

method_template = Template(method_boilerplate)
test_template = Template(test_boilerplate)


def _escape_values(value: str, type: TopCoderType) -> str:
    return str(value).replace("{", "[").replace("}", "]")


def generate_method_file(problem: TopCoderProblem):
    needs_import = problem["return_type"] in TOPCODER_LIST_TYPES
    args = []
    for param in problem["parameters"]:
        if param["type"] in TOPCODER_LIST_TYPES:
            needs_import = True
        
        args.append(f"{param['name']}: {param['type']}")

    rendered_code = method_template.render({
        "description": problem["description"],
        "func_name": problem["func_name"],
        "args": ", ".join(args),
        "return_type": problem["return_type"],
        "needs_import": needs_import
    })

    return rendered_code


def generate_test_file(problem: TopCoderProblem):
    for test in problem["test_cases"]:
        test["output"] = _escape_values(test["output"], problem["return_type"])
        test["inputs"] = [
            _escape_values(inp, problem["parameters"][i]["type"]) 
            for i , inp in enumerate(test["inputs"])
        ]
    
    rendered_code = test_template.render({
        "func_name": problem["func_name"],
        "test_cases": [
            {
                "inputs": f"[{', '.join([str(inp) for inp in test['inputs']])}]",
                "output": test["output"]
            }
            for test in problem["test_cases"]
        ]
    })

    return rendered_code


def create_problem_files(problem: TopCoderProblem, problems_dir: str = None):
    if not problems_dir:
        problems_dir = os.path.join(PROJECT_ROOT, "problems", problem["id"])

    if not os.path.exists(problems_dir):
        os.makedirs(problems_dir)

    open(os.path.join(problems_dir, "__init__.py"), 'a').close()

    method_file = generate_method_file(problem)
    
    with open(os.path.join(problems_dir, f"{problem['func_name']}.py"), "w") as f:
        f.write(method_file)
    
    test_file = generate_test_file(problem)

    with open(os.path.join(problems_dir, f"test_{problem['func_name']}.py"), "w") as f:
        f.write(test_file)
