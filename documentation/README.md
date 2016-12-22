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
sphinx-apidoc -f -o _modules/ .. #1
sphinx-build -b html -d build/doctrees   . build/html #2

```
The first line (#1) is going to create the skeleton of the doc withing some .rst files (in _models)

The second line (#1) is going to read the code and build the html
