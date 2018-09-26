# Contributing to Arches

We'd love for you to contribute your time, experience or knowledge to help make Arches even better than it is
today! Here are the guidelines we'd like you to follow:
- [Logging Issues and Bugs](#issue)
- [Contributing Code](#contribute-code)
    - [Commit Message Guidelines](#commit)
- [Contributing Documentation](#documentation)
### <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
submitting an issue to this [GitHub Repository][github]. Even better you can submit a Pull Request
with a fix.
#### Submitting an Issue
Before you submit your issue search the archive, maybe your question was already answered. Please take a minute to search through the open issues in the repo, and if you find one that matches your own, feel free to comment and your thoughts.
If your issue appears to be a bug, and hasn't been reported, open a new issue. Be sure to create your issue in the Arches repo and not a fork of Arches so that it is visible to the community. Please add the appropriate labels to the issue (multiple labels are ok) to help us keep track of them.  Most labels are used across all Arches Project repositories, but some are specific to `archesproject/arches`.
#### Tracking Issues With ZenHub
We use ZenHub in our repo to enhance our issue tracking, and generate statistics for our progress.
### <a name="contribute-code"></a> Contributing Code
We strongly encourage code contributions. To begin, you should begin by **forking the Arches repo**. Then, follow our guide for [creating a development environment](https://arches.readthedocs.io/en/latest/creating-a-development-environment/) and clone your own fork, not the official archesproject repo. Once you have Arches fully installed using your own fork of the repo, you are ready to begin.
#### Submitting Code

First, be sure that a ticket exists that addresses the code you are going to commit (see [Submitting and Issue](https://github.com/archesproject/arches/blob/master/.github/CONTRIBUTING.md#submitting-an-issue) above). It is important to start with a ticket so that the community has a chance to become aware of the problem you intend to solve or the feature you'd like to add.

Before code will be accepted into the Arches, contributors will need to sign the [Contributor License Agreement](https://gist.github.com/archesprojectbot/a3fac614c9fcb9129cd0b5339d9981a4) (CLA). This process is handled by [CLA-Assistant](https://cla-assistant.io). You can sign it [here](https://cla-assistant.io/archesproject/arches), or CLA-Assistant will ask you to sign it once a Pull Request is submitted.
Typically, work on arches is done in branches outside of master, and then merged into master when all work on that bug/feature is completed. Branches are usually created to resolve a particular ticket. As such, branches are typically named for the ticket number they address followed by a short description of the issue addressed in the ticket, all in snake (lower) case.
For Example:
If I am working on ticket "1231 Cool New Feature" my branch may be named "1231_cool_new_feature"
* In your forked repo, create a branch, using the naming template shown above:
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
* When only changing documentation, include [ci skip] in the commit description
### <a name="documentation"></a> Contributing Documentation
If you are so inclined, we greatly appreciate any help in adding to the Arches documentation. This could include creating example videos/workflows, to-do tasks, etc. As you may be aware, our documentation can be found in a few places:
- This Wiki.
   - This is where we document the more technical side of Arches, from command line operations to the actual data model. We also have some step-by-step instructions for development/production strategies. We always love your feedback on what's here, or any contributions you would like to add.
   - To contribute to the wiki, use the same fork method as described above, but note that the wiki is actually a separate repo. [This stack exchange q/a](https://stackoverflow.com/questions/40159478/fork-clone-and-push-a-wiki-in-github) should help you get started.
- The official [Arches v4 Documentation][maindocs] on readthedocs.
   - This documentation is for Arches users (as opposed to developers) and is more focused on the app's UI.
   - To contribute to this documentation, fork the Arches repo as described above.
   - The contents are stored in [`arches/docs/`](https://github.com/archesproject/arches/tree/master/docs). The files are automatically built by readthedocs from the `master` branch. The `.txt` files are reStructured text, and built with Sphinx using the readthedocs theme. You can preview your changes locally by running `make html` in the docs directory, and opening `_build/html/index.html` in a browser.
- The Arches "in-app" help menus.
   - This documentation is accessible from within the Arches interface, and is meant for quick reference.
   - To contribute to this documentation, fork the Arches repo as described above.
   - This content is stored as HTML templates in [`/arches/arches/app/templates/help`](https://github.com/archesproject/arches/tree/master/arches/app/templates/help) and they are loaded on a "per view" basis, as you can see in [this example](https://github.com/archesproject/arches/blob/master/arches/app/views/graph.py#L96) from the graph settings view.
[github]: https://github.com/archesproject/arches/
[groups]: https://groups.google.com/forum/#!forum/archesproject
[website]: http://http://archesproject.org
[getty]: http://www.getty.edu/conservation
[wmf]: http://www.wmf.org/
[maindocs]: https://arches.readthedocs.io/
[Contributing]: https://github.com/archesproject/arches/blob/master/.github/CONTRIBUTING.md

## <a name="notes"></a> Additional Notes

### Issue and Pull Request Labels

This section describes how labels are used to help track and manage issues and pull requests. Most labels are used across all Arches Project repositories, but some are specific to `archesproject/arches`.


[GitHub search](https://help.github.com/articles/searching-issues/) makes it easy to use labels for finding groups of issues or pull requests you're interested in. For example, you might be interested in [open issues across `archesproject/arches` and all Arches Project owned packages which are labeled as bugs](https://github.com/issues?utf8=✓&q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Type%3A+Bug%22) or perhaps [open pull requests in `archesproject/arches` which are dependency upgrades](https://github.com/issues?utf8=✓&q=is%3Aopen+is%3Apr+repo%3Aarchesproject%2Farches+label%3A%22Type%3A+Dependencies%22+). To help you find issues and pull requests, each label is listed with search links for finding open items with that label in `archesproject/arches` only and also across all Atom repositories. We encourage you to read about [other search filters](https://help.github.com/articles/searching-issues/) which will help you write more focused queries.

The labels are grouped by their purpose, but it's not required that every issue have a label from every group or that an issue can't have more than one label from the same group.

#### Type of Issue
Labels in this category are proceeded by the `Type: ` tag.

| Label name   | `arches` :mag_right: | `archesproject`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `Bug` | [search][search-arches-repo-label-bug] | [search][search-arches-org-label-bug] | Issues that are confirmed bugs or reports that are very likely to be bugs. |
| `Dependencies` | [search][search-arches-repo-label-dependencies] | [search][search-arches-org-label-dependencies] | Issues relating to Dependency upgrades. |
| `Enhancement` | [search][search-arches-repo-label-enhancement] | [search][search-arches-org-label-enhancement] | Issues relating to an enhancement to the functionality of the Arches software. |
| `Proposal` | [search][search-arches-repo-label-proposal] | [search][search-arches-org-label-proposal] | Issues that are a proposal that is looking for input from the Arches team or community. |

#### Priority of Issue
Labels in this category are proceeded by the `Priority: ` tag.

| Label name   | `arches` :mag_right: | `archesproject`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `High` | [search][search-arches-repo-label-high] | [search][search-arches-org-label-high] | Issues that are deemed a high priority to be handled quickly. |
| `Low` | [search][search-arches-repo-label-low] | [search][search-arches-org-label-low] | Issues that are deemed a low priority to be handled when time permits. |

#### Status of Issue
Labels in this category are proceeded by the `Status: ` tag.

| Label name   | `arches` :mag_right: | `archesproject`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `Blocked` | [search][search-arches-repo-label-blocked] | [search][search-arches-org-label-blocked] | Issues blocked by other issues. |
| `Duplicate` | [search][search-arches-repo-label-duplicate] | [search][search-arches-org-label-duplicate] | Issues which are duplicates of other issues, i.e. they have been reported before. |
| `On Hold` | [search][search-arches-repo-label-onhold] | [search][search-arches-org-label-onhold] | Issues that have been put on hold for the foreseeable future. |
| `Won't Fix` | [search][search-arches-repo-label-wontfix] | [search][search-arches-org-label-wontfix] | Issues that the Arches core team has decided not to fix for now, either because they're working as intended or for some other reason. |


#### Subject of Issue
Labels in this category are proceeded by the `Subject: ` tag. Since there are many different subjects that change over time, not all are listed here. A few examples are listed below. To view all the Subject Labels, follow this [link](https://github.com/archesproject/arches/labels?utf8=%E2%9C%93&q=Subject). 

| Label name   | `arches` :mag_right: | `archesproject`‑org :mag_right: | Description |
| --- | --- | --- | --- |
| `Documentation` | [search][search-arches-repo-label-documentation] | [search][search-arches-org-label-documentation] | Issues relating to Documentation, either In App or on [Read The Docs][readthedocs]. |
| `Import/Export` | [search][search-arches-repo-label-importexport] | [search][search-arches-org-label-importexport] | Issues relating to Import/Export of data in and out of Arches |
| `RDM` | [search][search-arches-repo-label-rdm] | [search][search-arches-org-label-rdm] | Issues relating to the Reference Data Manager |
| `Search` | [search][search-arches-repo-label-search] | [search][search-arches-org-label-search] | Issues relating to search. |
| `Testing` | [search][search-arches-repo-label-testing] | [search][search-arches-org-label-testing] | Issues relating to testing the Arches codebase. |

#### Roadmap Issues
Labels in this category are proceeded by the `Roadmap: ` tag. Since there are many different subjects that change over time, not all are listed here. These labels pertain to specific work that is planned in the near future. To view all the Roadmap Labels, follow this [link](https://github.com/archesproject/arches/labels?utf8=%E2%9C%93&q=Roadmap). 

[search-arches-repo-label-bug]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Type%3A+Bug%22
[search-arches-org-label-bug]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Type%3A+Bug%22
[search-arches-repo-label-dependencies]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Type%3A+Dependencies%22
[search-arches-org-label-dependencies]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Type%3A+Dependencies%22
[search-arches-repo-label-enhancement]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Type%3A+Enhancement%22
[search-arches-org-label-enhancement]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Type%3A+Enhancement%22
[search-arches-repo-label-proposal]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Type%3A+Proposal%22
[search-arches-org-label-proposal]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Type%3A+Proposal%22

[search-arches-repo-label-high]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Priority%3A+High%22+
[search-arches-org-label-high]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Priority%3A+High%22+
[search-arches-repo-label-low]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Priority%3A+Low%22+
[search-arches-org-label-low]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Priority%3A+Low%22+

[search-arches-repo-label-blocked]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Status%3A+Blocked%22+
[search-arches-org-label-blocked]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Status%3A+Blocked%22+
[search-arches-repo-label-duplicate]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Status%3A+Duplicate%22+
[search-arches-org-label-duplicate]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Status%3A+Duplicate%22+
[search-arches-repo-label-onhold]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Status%3A+On+Hold%22+
[search-arches-org-label-onhold]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Status%3A+On+Hold%22+
[search-arches-repo-label-wontfix]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Status%3A+Won%27t+Fix%22+
[search-arches-org-label-wontfix]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Status%3A+Won%27t+Fix%22+

[search-arches-repo-label-documentation]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Subject%3A+Documentation%22+
[search-arches-org-label-documentation]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Subject%3A+Documentation%22+
[search-arches-repo-label-importexport]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Subject%3A+Import%2FExport%22+
[search-arches-org-label-importexport]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Subject%3A+Import%2FExport%22+
[search-arches-repo-label-rdm]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Subject%3A+RDM%22+
[search-arches-org-label-rdm]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Subject%3A+RDM%22+
[search-arches-repo-label-search]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Subject%3A+Search%22+
[search-arches-org-label-search]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Subject%3A+Search%22+
[search-arches-repo-label-testing]: https://github.com/issues?q=is%3Aopen+is%3Aissue+repo%3Aarchesproject%2Farches+label%3A%22Subject%3A+Testing%22+
[search-arches-org-label-testing]: https://github.com/issues?q=is%3Aopen+is%3Aissue+user%3Aarchesproject+label%3A%22Subject%3A+Testing%22+


[github]: https://github.com/archesproject/arches/
[groups]: https://groups.google.com/forum/#!forum/archesproject
[readthedocs]: http://arches.readthedocs.io/en/stable/
