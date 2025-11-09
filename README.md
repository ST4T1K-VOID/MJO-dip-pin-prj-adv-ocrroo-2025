# Overview

Include a brief overview of the project, include:

- How do you deploy and run the project?
- What are its core dependencies?
- Who is it for and why?

# Guides
## Installation

### 1. Install UV
use either:   
```bash
pip install uv
```  
or:  
```bash
pipx install uv
```   
this will install uv in an 'isolated environment' which is recommended by UV   
for more information on installing or alternative methods, visit: [UV installation docs](https://docs.astral.sh/uv/getting-started/installation/)   
***   
***create a venv using UV***

```bash
uv venv
```

### 2. Install Dependencies

before beginning ensure you have downloaded [Tesseract](https://github.com/UB-Mannheim/tesseract/releases). Download the .exe from the latest release and follow the install instructions  
***   
to install the project dependecies, run this command:
```bash
uv pip install -r pyproject.toml
```
### 3. Provide project with Tesseract location
locate this line:
```python
pytesseract.pytesseract.tesseract_cmd = r""
```
replace `r""` with the ___absolute___ path for your tesseract installation (specifically the .exe)  
## set-up / running

### 1. Running the API
to run the API use:
```bash
uv run fastapi dev [relative file location]
```
`[file location]` will be wherever `FastAPO` is instantiaded, in our case `./preliminary/simple_api.py`  
you can test if the API is running by running a `curl` command from a diffferent terminal window/tab:
```bash
curl 127.0.0.1:8000/[endpooint]
```
`127.0.0.1:8000` may not work if you are running from a different port, you can check the terminal running the API.  
for `endpoints` check [simple_api.py](./preliminary/simple_api.py)
