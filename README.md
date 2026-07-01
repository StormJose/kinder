# Kinder Converter

## Installation
<br>

You must have Python 3.11 and have [Calibre](https://calibre-ebook.com/download) ebook management application installed to run the project.

### macOS

To achieve this, create a virtual environment (MacOS):
```
    python3.11 -m venv .venv
```
<br>

Using pyenv:
```
    /Users/[User]/.pyenv/versions/3.11.15/bin/python -m venv myenv 
```
<br>

Then, activate the environment running:
```
    myenv\Scripts\activate
```
<br>

Go to the root of the project and install the dependencies:
```
    pip install -r requirements.txt
```
<br>

### Windows

To achieve this, create a virtual environment:
```
    py -3.11 -m venv .venv
```
<br>

Using pyenv (pyenv-win):
```
    C:\Users\[User]\.pyenv\pyenv-win\versions\3.11.15\python.exe -m venv myenv
```
<br>

Then, activate the environment running:
```
    myenv\Scripts\activate
```
<br>

Go to the root of the project and install the dependencies:
```
    pip install -r requirements.txt
```
<br>

### Linux

To achieve this, create a virtual environment:
```
    python3.11 -m venv .venv
```
<br>

Using pyenv:
```
    ~/.pyenv/versions/3.11.15/bin/python -m venv myenv
```
<br>

Then, activate the environment running:
```
    source myenv/bin/activate
```
<br>

Go to the root of the project and install the dependencies:
```
    pip install -r requirements.txt
```
<br>
<br>

## Usage
<br>

To convert pdf files directly in the project, add it to the root and reference it by running the command:
```
    kinder "book_name.pdf" -a "Author"
```
