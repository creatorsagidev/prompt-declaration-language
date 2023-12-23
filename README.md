# Prompt Description Language

Prompt Decription Language (PDL) is a language to specify interactions between a user (prompts) and LLMs, and to compose their use with other tools. It is a declarative language to describe the shape of interactions and provide a way to specify constraints that must be satisfied. PDL scripts can be used for inference, LLM chaining, as well as composition with other tools such as code and APIs. Currently, PDL has an interpreter (`pdl/pdl.py`) that can be used for inference and to render scripts into documents. 

In the future, we plan to provide checking and validation, as well as code generation (e.g., data synthesis, data processing pipelines) since PDL scripts can serve as a single-source of truth. The specified constraints can further be used for constrained decoding when using an LLM.

You can find a demo video of PDL [here](https://ibm.box.com/s/g3x5zbd7b56o223mtqte3sr5e0xkttnl).

## Interpreter Installation

The interpreter has been tested with Python version 3.11.6.

To install the requirements for `pdl.py`, execute the command:

```
pip3 install -r requirements.txt
```

In order to run the examples that use BAM models, you need to set up 2 environment variables:
- `GENAI_API` set to `https://bam-api.res.ibm.com/v1/`
- `GENAI_KEY` set to your BAM API key. To obtain your key, go to the [BAM](https://bam.res.ibm.com/) main page. On the right and under the "Documentation" section, you will see a button to copy your API key.

To run the interpreter:

```
python3 pdl/pdl.py <path/to/example.json>
```

The folder `examples` contains some examples of PDL scripts. Several of these examples have been adapted from the LMQL [paper](https://arxiv.org/abs/2212.06094) by Beurer-Kellner et al. 


The following section is an introduction to PDL.

## Introduction to PDL

PDL scipts are specified in JSON, which reflects their declarative nature. JSON is also easy to write and to consume by other tools, unlike DSLs that require a suite of tools. Unlike other LLM programming frameworks, PDL is agnostic of any programming language. The user describes the shape of a document, elements of which capture interactions with LLMs and other tools. 

The following is a simple `hello, world` script:

```
{
    "title": "Hello world!",
    "prompts": [
        "Hello, world!\n",
        "This is your first prompt descriptor!\n"
    ]
}
```

This script has a `title` and specifies the `prompts` of the document. In this case, there are no calls to an LLM or other tools.
To render the script into an actual document, we have a PDL interpreter that can be invoked as follows:

```
cd pdl
python3 pdl.py ../examples/hello/hello.json 
```

This results in the following output:

```
Hello, world!
This is your first prompt descriptor!
```

### Prompt Blocks

PDL scripts can have nested `block`s of prompts indicated with braces `{}`. A block of prompts can have various properties including `repeats`, `repeats_until`, and `condition`.

The following example shows a block of prompts that is repeated 3 times.

```
{
    "title": "Hello world with a nested block",
    "prompts": [
        "Hello, world!\n",
        "This is your first prompt descriptor!\n",
        {
            "prompts": [
                "This sentence repeats!\n"
            ],
            "repeats": 3
        }
    ]
}

```

It results in the following document, when ran through the interpreter:

```
Hello, world!
This is your first prompt descriptor!
This sentence repeats!
This sentence repeats!
This sentence repeats!
```

The property `repeats_until` indicates repetition of the block until a condition is satisfied, and `condition` specifies that the block is executed only if the condition is true. Currently, the only supported conditions are `ends_with` and `contains`. See examples of these properties in `examples/arith/Arith.json`.

### Variable Definition and LLM Call

In the next example, a prompt block is used to call into an LLM. The `var` field indicates that we are introducing a variable named
`NAME` and the `lookup` section indicates how to fill that variable. In this case, we are requesting a call to the `ibm/granite-20b-code-instruct-v1` model on BAM with
`greedy` decoding scheme. The field `input` indicates what input is to be passed to the model. In this case, the entire context is passed, meaning all the text generated from the start of the script. The field `stop_sequences` indicates strings that cause generation to stop.

```
{
    "title": "Hello world with a variable to call into a model",
    "prompts": [
        "Hello,",
        {
            "var": "NAME",
            "lookup": {
                "model": "ibm/granite-20b-code-instruct-v1",
                "decoding": "greedy",
                "input": "context",
                "stop_sequences": [
                    "!"
                ]
            }
        },
        "!\n"
    ]
}

```

This results in the following document, where the text `world` has been generated by granite. 

```
Hello, world!
```

### Variable Value

The value of variables can be recalled after their definition, as in the following example:

```
{
    "title": "Hello world with variable use",
    "prompts": [
        "Hello,",
        {
            "var": "NAME",
            "lookup": {
                "model": "ibm/granite-20b-code-instruct-v1",
                "decoding": "argmax",
                "input": "context",
                "stop_sequences": [
                    "!"
                ]
            }
        },
        "!\n",
        "Who is",
        {
            "value": "NAME"
        },
        "?\n"
    ]
}
```

This results in the following document:
```
Hello, world!
Who is world?
```

### Model Chaining

PDL also allows multiple models to be chained together as in the following example, where 2 different models are called.

```
{
    "title": "Hello world showing model chaining",
    "prompts": [
        "Hello,",
        {
            "var": "NAME",
            "lookup": {
                "model": "ibm/granite-20b-code-instruct-v1",
                "decoding": "argmax",
                "input": "context",
                "stop_sequences": [
                    "!"
                ]
            }
        },
        "!\n",
        "Who is",
        {
            "value": "NAME"
        },
        "?\n",
        {
            "var": "RESULT",
            "lookup": {
                "model": "google/flan-t5-xl",
                "decoding": "argmax",
                "input": "context",
                "stop_sequences": [
                    "!"
                ]
            }
        },
        "\n"
    ]
}
```

This results in the following document:

```
Hello, world!
Who is world?
Hello, world
```

where the last line is the output of the second model `google/flan-t5-xl`, when given the first 2 lines as input.

### Python Code

The following script shows how variable lookup could be done with python code instead. Currently, the python code is executed locally. In the future, we plan to use a serverless cloud engine to execute snippets of code. So in principle, PDL is agnostic of any specific programming language. For the result of the code to be assigned to variable `NAME`, it must be assigned to a variable `result` internally.


```
{
    "title": "Hello world showing call out to python code",
    "prompts": [
        "Hello, ",
        {
            "var": "NAME",
            "lookup": {
                "lan": "python",
                "code": [
                    "import random\n",
                    "import string\n",
                    
                    "result = random.choices(string.ascii_lowercase)[0]"
                ]
            }
        },
        "!\n"
    ]
}
```

This results in the following output:
```
Hello, r!
```

### API Calls

PDL variables can also be fulfilled by making API calls. Consider a simple weather app (`examples/hello/weather.json`), where the user asks a question about the weather in some location. Then we make one call to an LLM to extract the location entity, use it to make an API call to get real-time weather information for that location, and then make a final call to an LLM to interpret the JSON output and return an English text to the user with the weather information. In this example, the call to the API is made with the following block:

```
{
    "var": "WEATHER",
    "lookup": {
        "api": "https",
        "url": "https://api.weatherapi.com/v1/current.json?key=XXXXXX",
        "input": {
            "value": "LOCATION"
        },
        "show_result": false
    }
},
```

Notice that by setting `show_result` to `false`, we exclude the text resulting from this interaction from the final output document. This can be handy to compute intermediate results that can be passed to other calls.

See a [demo](https://ibm.box.com/s/g3x5zbd7b56o223mtqte3sr5e0xkttnl) video of this example.



## Additional Notes and Future Work

- Currently, the parameters for calling models are hard-wired to the following. In the future, we will support user-provided parameters.
    - decoding_method="greedy",
    - max_new_tokens=200,
    - min_new_tokens=1,
    - repetition_penalty=1.07

- Only simple GETs are supported for API calls currently (see example: `examples/hello/weather.json`). We plan to more fully support API calls in the future.

- The example `examples/react/React.json` is work-in-progress.

- PDL scripts can also contain constraints for the output of an LLM. This can be used for constrained decoding and is part of future work (not currently supported).
In the following example, the variable `NAME` is constrained to consist of a single word.

```
{
    "title": "Hello world with a constraint",
    "prompts": [
        "Hello,",
        {
            "var": "NAME",
            "lookup": {
                "model": "ibm/granite-20b-code-instruct-v1",
                "decoding": "argmax",
                "input": "context",
                "stop_sequences": [
                    "!"
                ],
                "constraints": [
                    {
                        "words_len": 1
                    }
                ]
            }
        },
        "!\n"
    ]
}
```
