
### 本地分支回退版本
```shell
 git reset --hard   22f8aae 。22f8aae 为某次提交的提交号。
 git reset --hard HEAD~3 （回退3次提交）
 
 --hard：本地的源码和本地未提交的源码都会回退到某个版本，包括commit内容，和git自己对代码的索引都会回退到某个版本.any local changes will be lost。
 --soft：保留源码，只能回退到commit信息到某个版本，不涉及到index的回退，如果还需要提交，直接commit即可。比如我选择soft方式来进行回退，我的本地代码和本地新添加的尚未commit的代码都没有改变。
 --mixed：会保留源码，只是将git commit和index信息回退到某个版本。
```


### 远程分支回退版本

##### 方法一，先git reset回滚到本地，然后再强制push到远程。
```shell
git push -u origin master -f        origin：远程仓库名  master：分支名称  -f：force，意为强制、强行
```



### 删除提交分支

```shell
# 删除当前提交分支
git remote remove origin 

# 添加新的分支
git remote add origin https://gitee.com/kingCould/HelloWord.git
```


### 分支文件冲突

```shell
# 保存未修改文件，添加备注，方便查找
git stash save "save message"

# 应用并删除第二个存储
git stash pop stash@{1}

# 应用第二个存储,但不会把存储从存储列表中删除
git stash apply stash@{1}

# 从列表中删除第二个存储
git stash drop stash@{1}

# 先切换到主分支（或即将被覆盖的分支）
$ git checkout master

# 将 test 分支覆盖到当前分支
$ git merge test

# 删除之前的分支 (已经没用了)
$ git branch -d <branch-name>
```



### git lfs 突破 大文件

```shell
git init

git lfs install

git lfs track "*.pdf"

git lfs track "*.epub"

cat .gitattributes

git add .gitattributes

git commit -m "track *.pdf *epub files using Git LFS"

git add .

git commit -m "first add books"

git lfs ls-files

```

