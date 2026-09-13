# Lab 1：Git 版本控制与协作

## 实验目标

通过本实验熟悉 Git 的基本版本控制操作，并体验基于 GitHub 的分支开发、Pull Request（PR）、代码合并和冲突解决流程。

## 任务 1：个人版本管理

1. Fork 本课程仓库 [`pku-software/isse-labs`](https://github.com/pku-software/isse-labs)，然后将自己的 fork 克隆到本地。
2. 在 `lab1/` 下创建自己的提交目录，命名为 `<姓名>-<学号>`。
3. 在个人提交目录中创建 `diary.txt`，写下今天上课的感受，然后完成第一次提交，并设置一句提交信息。
4. 修改 `diary.txt`，追加一句话，然后完成第二次提交。
5. 使用 `git log --oneline` 检查提交历史。

## 任务 2：远程仓库操作

1. 将本地 `main` 分支推送到自己的课程仓库 fork。
2. 在 GitHub 网页中确认个人目录、文件和两次提交记录已经成功同步。

## 任务 3：分支操作

1. 在自己fork的仓库中从 `main` 创建一个以自己学号命名的分支。
2. 打开文件 [`lab1/shared-note.md`](shared-note.md)，找到包含自己学院和姓名的一行，例如：

   ```text
   xx学院 张三 学号：待填写
   ```

   只将该行的 `待填写` 替换为自己的学号，不要修改其他同学的内容：

   ```text
   xx学院 张三 学号：20260101
   ```
3. 提交这次修改，将自己的学号分支推送到个人 fork。
4. 等待助教更新仓库 `main` 分支后，继续任务 4。助教会修改每位同学所在行的内容，因此个人分支和课程仓库 `main` 会对同一行产生不同修改。

## 任务 4：提交 Pull Request 与冲突解决

1. 在 GitHub 上从个人 fork 的 `<学号>` 分支，向课程仓库 `pku-software/isse-labs` 的 `main` 分支发起 PR，PR 标题使用以下格式：

   ```text
   [Lab1] 姓名-学号
   ```
2. 如果 PR 页面提示存在冲突，点击 **Resolve conflicts**。删除 GitHub 显示的冲突标记，将本人所在行整理为“学院 姓名 学号”，不要修改其他同学的内容。
3. 点击 **Mark as resolved**，确认所有冲突均已处理后，点击 **Commit merge**。GitHub 会自动更新原 PR，无需重新创建或再次推送。
