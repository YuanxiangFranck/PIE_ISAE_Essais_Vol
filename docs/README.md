# Build code documentation

This documentation is build automatically by reading the docsting within the code.
It uses sphinx in order to build the html pages.

## How to build it

From the **documentation** folder, run the following commands:
```shell
make html
```

## How it works

make html only run the following lines:
```shell
sphinx-apidoc -f -o _modules/ ..
sphinx-build -b html -d build/doctrees   . build/html
cp -r build/html/*.html build/html/_static
```
The first line is going to create the skeleton of the doc withing some .rst files (in _models)

The second line is going to read the code and build the html

The last line is to copy the html / css / js files to the /docs folder in order to let github gh-pages find it
