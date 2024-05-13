# 41091 Data Systems
### Project Title: OptiMate Tech

## Group Members

| Student Name | Student ID |
|-----|-----|
| Nicole Hutomo | 24613388 |
| Olivia Ju | 13923673 |
| Alana Kumar | 24451623 |
| Elizabeth Nguyen | 24846519 |
| Sandhya Prabakaran | 24955205 |
| Jaemiely Umali | 13894656 |

## VSCode Setup

In VSCode, install "GitHub Pull Requests and Issues Extension" and sign into GitHub using extension.

Clone project repo -> `Shift + Cmd + P` -> "Git: Clone".

Search for the project repo -> "alanak24/Datasystems".

Select local destination for repo.

## Setting up a Virtual Environment

In bash terminal:

``` bash
python3 -m venv {environment_name}
```

Click 'Yes' in the pop up. 

To activate:

``` bash
source {environment_name}/bin/activate
```

Select interpreter in `Shift + Cmd + P`, search 'Python: Select Interpreter' -> Python v 3.12.3 (Recommended)
To unselect interpreter, select the Global option.

Deactivate using `deactivate` in terminal or to remove environment:
``` bash
rm -r {environment_name}/
```


## Installations

**Homebrew**

[HomeBrew](https://docs.brew.sh/Installation.html) version 4.2.17 (or latest)

**Bash**

``` bash
brew install bash
```

**Azure CLI**

``` bash
brew update && brew install azure-cli
``` 

See troubleshooting details [here](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)

Login to Azure:
``` bash
az login
```

**API for our database**

SQL Alchemy or tutor suggested MS ODBC

**Node.js and npm**
``` bash
brew install node
```

Test versions:
``` bash
node -v
npm -v
```

**dotenv**
``` bash
npm install dotenv --save
```

## Create a PR

create branch (if required):

``` bash
git branch {branch_name}
git checkout {branch_name}
git checkout -b {branch_name}
```

commit files to pr:
``` bash
git add .
git commit -m "{a message about the pull request/changes added}"
git push
```

run `git checkout` in terminal if you want to check what files have been added/changed
