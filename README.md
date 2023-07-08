# FriendlyFL

A federated learning (FL) system that is friendly to users with diverse backgrounds, for instance, in healthcare

## Environment

### Mac

#### Prerequisites

##### brew
We are going to use [brew](https://brew.sh/) to install some tools. If you don't have brew installed on your Mac, run the following command:
```shell
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

##### Pyenv

We would suggest to use [pyenv](https://github.com/pyenv/pyenv) to manage and switch multiple versions of Python.
To install follow steps below.
```shell
brew update
brew install pyenv
```
If this didn't work for you try these [fixes](https://github.com/pyenv/pyenv#homebrew-in-macos).

To test if this was installed correctly try running the following in your terminal:
```shell
pyenv versions
```

We are going to be using Python version 3.10.10, so let's get that installed.
```shell
pyenv install 3.10.10
```

##### Poetry
We are going to use [poetry](https://python-poetry.org/) to manage dependencies. 

Run the following command in your terminal to install poetry:
```shell
curl -sSL https://install.python-poetry.org | python3 -
```

### Windows
Todo
### Linux
Todo


## Development

### With Docker
#### Build docker image
```shell
docker build -t friendlyfl:latest .
```

#### Start
```shell
docker run -it -p 8000:8000 docker.io/library/friendlyfl:latest
```



### Without Docker

#### Create a virtual environment
```shell
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies
```shell
poetry install
```

#### Database Migration
```shell
python3 manage.py migrate
```

#### Start Development Server
```shell
python3 manage.py runserver
```

#### De-active virtual environment
Type `deactivate` in your terminal
