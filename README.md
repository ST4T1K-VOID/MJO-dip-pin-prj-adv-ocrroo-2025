# Overview (WIP)
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
`[file location]` will be wherever `FastAPI` is instantiaded, in our case `./preliminary/simple_api.py`  
you can test if the API is running by running a `curl` command from a diffferent terminal window/tab:
```bash
curl 127.0.0.1:8000/[endpooint]
```
`127.0.0.1:8000` may not work if you are running from a different port, you can check the terminal running the API.  
for `endpoints` check [simple_api.py](./api/simple_api.py)

# How to Contribute

## Issues
When creating an issue, please use the provided template ([Issues](https://github.com/ST4T1K-VOID/MJO-dip-pin-prj-adv-ocrroo-2025/issues) > new issues > Issue Template), it should be the first option.  
If, for whatever reason, the template is not available, a copy is provided [here](./docs/templates/issue-template.md).

## Codebase Contributions

if you find an issue you want to work on, please say so in comments of the issue.

### Expected Workflow
- fork this repo,
  - [optional] create a branch (this is useful for being able to get any changes from the upstream repo (this one)),
- work on your issue(s),
- create a pull request (there is  template for this, if it is not appearing please grab the copy from [here](./docs/templates/pull_request_template.md),
- before pushing, run either commands below to lint your work. (code will also be automatically tested when pushed)
  your work wont be accepted if it fails linting.
  ```bash
     pylint --output="./pylint_output.txt" --generated-member=cv2 $(git ls-files '*.py')
  ```
  pylint report is placed into a file.
  
  ```bash
     pylint --generated-member=cv2 $(git ls-files '*.py')
  ```
  pylint report is place directly in the console, will allow you to jump to the file and line of code to fix.
  
- wait for review, if needed implement requested changes.

If you want, you can create a draft pull request, this will allow others to see your work before it is ready.
