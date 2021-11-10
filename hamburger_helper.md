# Hamburger Helper
## GIT Simple Worklow
### When starting
(NEVER WORK/COMMIT ON DEV)

```bash
git checkout dev
git branch <your_branch>
git checkout <your_branch>
```

### Commit new work
```bash
git add <modified_file>
git commit -m"<commit description message>"
```

### Upload to Github (origin) to share your work
```bash
git pull origin dev
git checkout dev
git merge <your_branch>
git push origin dev
```

## PIP Worklow
### Create a virtual environement
Once after cloning a new repo:
```shell
python -m venv env
pip install -r requirements.txt
``` 
(_To install all the packages required foe development_)

### Update requirements.txt
```shell
pip freeze > requirements.txt
``` 
