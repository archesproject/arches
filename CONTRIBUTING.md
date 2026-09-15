# Contributing to Arches

We'd love for you to contribute your time, experience or knowledge to help make Arches even better than it is
today! Here are the guidelines we'd like you to follow:
- [Logging Issues and Bugs](#issue)
- [Contributing](#contribute)
  - [Contributing Code](#contribute-code)
      - [Commit Message Guidelines](#commit)
  - [Contributing Documentation](#documentation)
  - [Human Accountability](#human-accountability)
  - [Acknowledging AI Assistance and Other Assistance](#acknowledging-assistance)
- [CSS Styleguide](contributing/css-styleguide.md)
- [Seeing What Others Are Working On](#tracking)
- [Becoming an Arches Maintainer](#maintainership)

## <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
[submitting an issue](https://github.com/archesproject/arches/issues). Bugs are much easier to fix if you [include a screenshot or gif](https://github.com/archesproject/arches/wiki/Screen-capture) in the issue. Even better you can submit a Pull Request
with a fix.

### Submitting an Issue
Before you submit your issue search the archive, as your question may already be answered. Please take a minute to search through the [issues] in the repository (both open and closed), and look in the [Arches Community Forum](https://community.archesproject.org/).  If you find an open issue that matches your own, feel free to comment and add further information or thoughts.
If your issue appears to be a bug that hasn't yet been reported, then open a new issue. Be sure to create your issue in the main Arches repository, not in a fork, so that the issue is visible to the community.

Please add the [appropriate labels](https://github.com/archesproject/arches/wiki/Issue-and-Pull-Request-Labels) to the issue (multiple labels are ok) to help us keep track of them.

## <a name="contribute"></a> Contributing

### <a name="contribute-code"></a> Contributing Code
We strongly encourage code contributions. To begin, you should begin by **forking the Arches repo**. Then, follow our guide for [creating a development environment](https://arches.readthedocs.io/en/stable/developing/getting-started/creating-a-development-environment/) and clone your own fork, not the official archesproject repo. Once you have Arches fully installed locally using your own fork of the repo, you are ready to begin.

#### Submitting Code

First, be sure that a ticket exists that addresses the code you are going to commit (see [Submitting an Issue](#submitting-an-issue) above). It is important to start with a ticket so that the community has a chance to become aware of the problem you intend to solve or the feature you'd like to add.

New contributors need to sign the [Contributor License Agreement](https://gist.github.com/archesprojectbot/a3fac614c9fcb9129cd0b5339d9981a4) (CLA) for their contributions to be accepted into Arches. You only need to do this once, at the time of your first contribution. The process is handled by [CLA-Assistant](https://cla-assistant.io). You can sign the CLA [here](https://cla-assistant.io/archesproject/arches), or CLA-Assistant will ask you to sign it once your first Pull Request is submitted.
Typically, work on Arches is done in development branches, and then merged into the appropriate branch (see [Shared Development Branches](#dev-branches)) when all work on that bug/feature is completed. A development branch is usually created to resolve a particular ticket, and such branches are typically named for the ticket number they address followed by a short description of the issue addressed in the ticket, all in snake (lower) case.

For Example:

If I am working on ticket "Cool New Feature (ticket #1231)" my branch may be named "1231_cool_new_feature".  (Note that in all the sample commands below, we use "dev/8.1.x" to represent the current upstream default development branch.  It might be different by the time you read this; see [Shared Development Branches](#dev-branches) for more.)

* In your forked repo, create a branch, using this naming template:
     ```shell
    git checkout -b 1231_cool_new_feature dev/8.1.x
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
   python manage.py test tests --settings="tests.test_settings"
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

* We watch for new pull requests, so someone will respond as soon as they're able to. We may suggest changes to the code before the pull request is approved. If that is the case:
  * Make the required updates.
  * Re-run the test suite to ensure tests are still passing.
  * Commit your changes to your branch.
  * Push the changes to your GitHub repository (this will update your Pull Request).
  * _You do not need to make a new pull request._
* If the PR gets too outdated we may ask you to `rebase` and force push to update the PR:
    ```shell
   git rebase dev/8.1.x -i
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
* Check out the default development branch:
    ```shell
   git checkout dev/8.1.x -f
   ```
* Delete the local branch:
    ```shell
   git branch -D my-fix-branch
   ```
* Update your your local copy of the default development branch with the latest upstream version:
    ```shell
   git pull --ff upstream dev/8.1.x
   ```

#### <a name="dev-branches"></a> Shared Development Branches

Active development takes place on a long-lived branch named for the next upcoming release.  For example, at the time of this writing, that branch is `dev/8.1.x`.  A separate long-lived branch usually also exists for the most recently available release, e.g., `dev/8.0.x`.  That way, important fixes, such as security fixes, can be backported and new interim releases made -- e.g., "8.0.1", "8.0.2", etc -- while work continues in parallel toward the "8.1.0" release.  (Unlike some projects, Arches does not maintain a permanent `main` or `master` branch.  Instead, the name of Arches' default branch changes periodically; just look at the [repository on GitHub](https://github.com/archesproject/arches) to see what it is at any given time.)

Generally, your own individual development branches should be based on the latest `dev/A.B.x` branch.  In some cases a reviewer may ask you to rebase against `dev/A.B-1.x` or something else, depending on the specifics of the change.

#### <a name="commit"></a> Git Commit Guidelines
We have a few guidelines about how our git commit messages should be formatted.  This leads to **more
readable messages** that are easy to follow when looking through the **project history**.

##### Commit Message Format
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Make sure every commit references an issue, for example "improve contributing guidelines docs #1926"
* If you used AI assistance, [consider saying so](#acknowledging-assistance) in the commit message

### <a name="documentation"></a> Contributing Documentation
We greatly appreciate any help in adding to the Arches documentation. This could include creating example videos/workflows, to-do tasks, etc. We have two categories of documentation:
- Official [Arches documentation](http://arches.readthedocs.io) - full and publically accessible documentation
   - Managed in the [archesproject/arches-docs](https://github.com/archesproject/arches-docs) repository. Please see that repo's [wiki](https://github.com/archesproject/arches-docs/wiki) for more information on contributing content.
   - Also, feel free to just create an [issue](https://github.com/archesproject/arches-docs/issues) on the docs repo.
- In-app help panels - accessible only from within the Arches interface, meant for quick user reference
   - This content is stored as HTML templates in `/arches/arches/app/templates/help`.
   - To contribute to this documentation, use the normal contributing procedures described above.

### <a name="human-accountability"></a> Human Accountability

*The human contributor is fully responsible for each code commit and documentation contribution in the Arches Project.*

Regardless of what sources or tools you use in the process of making your contribution, you are responsible for everything you submit.

Your contribution is assumed to be your original work, and must not infringe anyone's copyright.  This will generally be true by default, unless you use an AI model that reproduces others' code verbatim, or unless you copy blocks of code unchanged from somewhere else.  (A contribution may include code from elsewhere as long as the original source is under a compatible open source license, and of course the contribution must keep the upstream provenance and copyright information intact.)

We [encourage citation](#acknowledging-assistance) of AI assistance or of any other significant assistance in assembling a contribution; such citations can help others improve their own contribution processes.

### <a name="acknowledging-assistance"></a> Acknowledging AI Assistance and Other Assistance

While the Arches Project does not require acknowledgement of AI assistance, we strongly encourage it.  Acknowledgement is a good social practice, as other contributors may be interested to know what AI tools their colleagues are using.

This principle is not limited to AI assistance.  For example, if another Arches community member helped with the contribution, thank them in the commit message.  Or if your contribution was aided by something you learned from a programmer help site (e.g., [Stack Overflow](https://stackoverflow.com/) or some place similar), consider citing the relevant page.

The best place for acknowledging human assistance or AI assistance is almost always in the [commit message](#commit).  For other kinds of assistance, use your judgement: the best place might be the commit message, or it might be in a comment in the code at the place where the new technique is used.

Note that some AI tools automatically insert their own byline in the commit message in a fairly generic way, for example:

```
🤖 Generated with https://claude.ai/code 
Co-Authored-By: Claude <noreply@anthropic.com>
```

If your AI tool inserts something like that, *please adjust the language* to accurately reflect the AI's role in this particular contribution.  Commit messages should be accurate, and that includes what they say about how the change was made.

## <a name="tracking"></a> Seeing What Others Are Working On

Some ongoing work in Arches is tracked in [GitHub
Projects](https://github.com/archesproject/arches/projects).  See the
various project boards there to get a sense of activity in different
workstreams.

## <a name="maintainership"></a> Becoming an Arches Maintainer

If you contribute regularly and would like to know how to become one
of the maintainers, with commit access to the project, please see
[Becoming a
Committer](https://github.com/archesproject/arches/wiki/Becoming-a-Committer).
