# Kinder Converter


## Installation
<br>

You must have Python 3.11 and have [Calibre](https://calibre-ebook.com/download) ebook management application installed to run the project.

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


## Usage
<br>
Inside the virtual environment, add the pdf version of the book and run the following command:

```
    kinder "book_name.pdf" -a "Author"
```
