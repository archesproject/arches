# Contributing to Arches

We'd love for you to contribute your time, experience or knowledge to help make Arches even better than it is
today! Here are the guidelines we'd like you to follow:
- [Logging Issues and Bugs](#issue)
- [Contributing Code](#contribute-code)
    - [Commit Message Guidelines](#commit)
- [Contributing Documentation](#documentation)

### <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
[submitting an issue](https://github.com/archesproject/arches/issues). Bugs are much easier to fix if you [include a screenshot or gif](https://github.com/archesproject/arches/wiki/Screen-capture) in the issue. Even better you can submit a Pull Request
with a fix.

#### Submitting an Issue
Before you submit your issue search the archive, maybe your question was already answered. Please take a minute to search through the open issues in the repo, and if you find one that matches your own, feel free to comment and your thoughts.
If your issue appears to be a bug, and hasn't been reported, open a new issue. Be sure to create your issue in the Arches repo and not a fork of Arches so that it is visible to the community.

Please add the [appropriate labels](https://github.com/archesproject/arches/wiki/Issue-and-Pull-Request-Labels) to the issue (multiple labels are ok) to help us keep track of them.

#### Tracking Issues With ZenHub
We use ZenHub in our repo to enhance our issue tracking, and generate statistics for our progress.

### <a name="contribute-code"></a> Contributing Code
We strongly encourage code contributions. To begin, you should begin by **forking the Arches repo**. Then, follow our guide for [creating a development environment](https://arches.readthedocs.io/en/latest/creating-a-development-environment/) and clone your own fork, not the official archesproject repo. Once you have Arches fully installed locally using your own fork of the repo, you are ready to begin.

#### Submitting Code

First, be sure that a ticket exists that addresses the code you are going to commit (see [Submitting an Issue](https://github.com/archesproject/arches/blob/master/CONTRIBUTING.md#submitting-an-issue) above). It is important to start with a ticket so that the community has a chance to become aware of the problem you intend to solve or the feature you'd like to add.

Before code will be accepted into the Arches, contributors will need to sign the [Contributor License Agreement](https://gist.github.com/archesprojectbot/a3fac614c9fcb9129cd0b5339d9981a4) (CLA). This process is handled by [CLA-Assistant](https://cla-assistant.io). You can sign it [here](https://cla-assistant.io/archesproject/arches), or CLA-Assistant will ask you to sign it once a Pull Request is submitted.
Typically, work on arches is done in branches outside of master, and then merged into master when all work on that bug/feature is completed. Branches are usually created to resolve a particular ticket. As such, branches are typically named for the ticket number they address followed by a short description of the issue addressed in the ticket, all in snake (lower) case.
For Example:
If I am working on ticket "Cool New Feature (ticket #1231)" my branch may be named "1231_cool_new_feature"
* In your forked repo, create a branch, using this naming template:
     ```shell
    git checkout -b 1231_cool_new_feature master
    ```
* Make changes to the code-base, only those that will address the new feature/bugfix that you named the branch after.
* Commit your changes using a descriptive commit message that follows our
 [commit message conventions](#commit-message-format):
     ```shell
    git commit -a
    ```

    Note 1: The optional `-a` flag will automatically "add" and "rm" all files that you have edited.

    Note 2: If you have created or deleted files in the file system, you'll have to precede this `commit` command with `git add .` which with add these new (or deleted) files to your git index.
* Test your changes locally to ensure all the tests pass (make sure your virtual environment is activate first):
    ```shell
   python manage.py test tests --pattern="*.py" --settings="tests.test_settings"
   ```
* Push your branch to GitHub:
    ```shell
   git push origin my-fix-branch
   ```
* This will create an new branch on your remote forked Arches repo.
* To send a pull request to the official Arches repo:
    1. In the Arches repo, go to "Pull Requests" and choose "Create New Pull Request".
   1. Click the link to "compare across forks".
   1. Set your repo as the "head fork", and select the branch that you want to merge.
   1. Create the pull request, complete with descriptions of changes. If applicable, connect the PR with the issue it addresses.
   
   [GitHub Documentation on creating a pull request from a fork](https://help.github.com/articles/creating-a-pull-request-from-a-fork/)
   
* We may suggest changes to the code before the pull request is approved. If that is the case:
 * Make the required updates.
 * Re-run the test suite to ensure tests are still passing.
 * Commit your changes to your branch.
 * Push the changes to your GitHub repository (this will update your Pull Request).
 * _You do not need to make a new pull request._
* If the PR gets too outdated we may ask you to `rebase` and force push to update the PR:
    ```shell
   git rebase master -i
   git push origin my-fix-branch -f
   ```

    *WARNING. Squashing or reverting commits and forced push thereafter may remove GitHub comments
on code that were previously made by you and others in your commits.*

That's it! Thank you for your contribution!

#### After your pull request is merged
After your pull request is merged, you can safely delete your branch and pull the changes
from the main (upstream) repository:
* Delete the remote branch on GitHub either through the GitHub web UI or your local shell as follows:
    ```shell
   git push origin --delete my-fix-branch
   ```
* Check out the master branch:
    ```shell
   git checkout master -f
   ```
* Delete the local branch:
    ```shell
   git branch -D my-fix-branch
   ```
* Update your master with the latest upstream version:
    ```shell
   git pull --ff upstream master
   ```
   
#### <a name="commit"></a> Git Commit Guidelines
We have a few guidelines about how our git commit messages should be formatted.  This leads to **more
readable messages** that are easy to follow when looking through the **project history**.

##### Commit Message Format
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Make sure every commit references an issue, for example "improve contributing guidelines docs #1926"
* When only changing in-app help panels, include [ci skip] in the commit description

### <a name="documentation"></a> Contributing Documentation
We greatly appreciate any help in adding to the Arches documentation. This could include creating example videos/workflows, to-do tasks, etc. We have two categories of documentation:
- Official [Arches documentation][readthedocs] - full and publically accessible documentation
   - Managed in the [archesproject/arches-docs](https://github.com/archesproject/arches-docs) repository. Please see that repo's [wiki](https://github.com/archesproject/arches-docs/wiki) for more information on contributing content.
   - Also, feel free to just create an [issue](https://github.com/archesproject/arches-docs/issues) on the docs repo.
- In-app help panels - accessible only from within the Arches interface, meant for quick user reference
   - This content is stored as HTML templates in [`/arches/arches/app/templates/help`](https://github.com/archesproject/arches/tree/master/arches/app/templates/help).
   - To contribute to this documentation, use the normal contributing procedures described above.
   
[github]: https://github.com/archesproject/arches/
[groups]: https://groups.google.com/forum/#!forum/archesproject
[website]: http://http://archesproject.org
[getty]: http://www.getty.edu/conservation
[wmf]: http://www.wmf.org/
[Contributing]: https://github.com/archesproject/arches/blob/master/.github/CONTRIBUTING.md
[readthedocs]: http://arches.readthedocs.io
