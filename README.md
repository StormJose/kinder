# Kinder Converter


## Installation
<br>

You must have Python 3.11^ at least and install [Calibre](https://calibre-ebook.com/download) ebook management application to run the project.

To achieve this, create a virtual environment:

```
    python -m venv .venv
```
```
    .venv\Scripts\Activate.ps1
```
<br>

Navigate inside the virtual environment and install the dependencies:
```
pip install -r requirements.txt

```
<br>
<br>
## Usage
<br>
Inside the virtual environment, add the pdf version of the book and run the following command:
```
kinder "book_name.pdf" -a "Author"
```