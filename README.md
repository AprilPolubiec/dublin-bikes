# Dublin Bikes
Hello I'm making some changes

# Developer notes

## Git 101
The purpose of this repository is to store all of our work to allow us to collaborate. Anytime you want to make changes, you will need to start a new branch which is where you will make all your changes. When the changes are ready, you will open a Pull Request which will be approved by at least 1 teammate and then merged into main.

## How to start a new branch
1. Check out main, pull down from main to pull any changes
`git pull`
2. Checkout a new branch
`git checkout -b BRANCH_NAME`
3. Make changes in branch
4. Checkout main again, and then merge into your branch
```
git checkout main
git pull
git checkout MY_BRANCH
git merge main
git push
```
5. Resolve conflicts if any (might need to coordinate here)
6. Push to remote (MAKE SURE YOU ARE ON YOUR BRANCH)
`git push`
7. Open PR, from your branch into main - drop link to issue in the PR for reference; leave any comments questions etc
8. Other person must approve - then we can merge into main