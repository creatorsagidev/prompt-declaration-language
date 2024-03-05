from pdl.pdl.pdl_ast import Program  # pyright: ignore
from pdl.pdl.pdl_interpreter import empty_scope  # pyright: ignore
from pdl.pdl.pdl_interpreter import process_block  # pyright: ignore

var_data = {
    "description": "Hello world with variable use",
    "document": [
        "Hello,",
        {
            "def": "NAME",
            "document": [
                {
                    "model": "ibm/granite-20b-code-instruct-v1",
                    "parameters": {
                        "decoding_method": "greedy",
                        "stop_sequences": ["!"],
                        "include_stop_sequence": False,
                    },
                }
            ],
        },
        "!\n",
        "Tell me about",
        {"get": "NAME"},
        "?\n",
    ],
}


def test_var():
    log = []
    data = Program.model_validate(var_data)
    _, document, _, _ = process_block(log, empty_scope, data.root)
    assert document == "Hello, world!\nTell me about world?\n"


code_var_data = {
    "description": "simple python",
    "document": [
        {
            "def": "I",
            "document": [
                {
                    "lan": "python",
                    "code": ["result = 0"],
                }
            ],
            "show_result": True,
        },
    ],
}


def test_code_var():
    log = []
    data = Program.model_validate(code_var_data)
    _, document, scope, _ = process_block(log, empty_scope, data.root)
    assert scope == {"context": document, "I": 0}
    assert document == "0"
