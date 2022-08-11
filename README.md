# workonsh
A live synchronizer local and remote machine. Similar to lsyncd

## Install
Requirements: `fswatch` and `rsync`.

To install from pypi

```
pip install workonsh
```

From git repo

```
pip install git+https://github.com/ngocbh/workonsh
```

## Usage

Run ```workonsh --help```

An example to create a session:

```
workonsh -n <project_name> -s <source-dir> -d <dest-dir> -e "*__pycache__" -f .gitignore -i 5
```
