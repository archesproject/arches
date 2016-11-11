# Contributing to Arches

We'd love for you to contribute your time, experience or knowledge to help make Arches even better than it is
today! Here are the guidelines we'd like you to follow:

 - [Question or Problem?](#question)
 - [Issues and Bugs](#issue)
 - [Submission Guidelines](#submit)
 - [Commit Message Guidelines](#commit)
 - [Additional Notes](#notes)

## <a name="question"></a> Got a Question or Problem?

If you have questions about how to use Arches, please direct these to the [Google Group][groups]
discussion list.

## <a name="issue"></a> Found an Issue?
If you find a bug in the source code or a mistake in the documentation, you can help us by
submitting an issue to our [GitHub Repository][github]. Even better you can submit a Pull Request
with a fix.

## <a name="submit"></a> Submission Guidelines

### Submitting an Issue
Before you submit your issue search the archive, maybe your question was already answered.

If your issue appears to be a bug, and hasn't been reported, open a new issue.

### Submitting a Pull Request

* Make your changes in a new git branch:

     ```shell
     git checkout -b my-fix-branch master
     ```

* Commit your changes using a descriptive commit message that follows our
  [commit message conventions](#commit-message-format)

     ```shell
     git commit -a
     ```
  Note: the optional commit `-a` command line option will automatically "add" and "rm" edited files.

* Test your changes locally to ensure all the tests pass:

    ```shell
    INSERT COMMAND HERE
    ```

* Push your branch to GitHub:

    ```shell
    git push origin my-fix-branch
    ```

* In GitHub, send a pull request to `arches:master`.
* If we suggest changes then:
  * Make the required updates.
  * Re-run the test suite to ensure tests are still passing.
  * Commit your changes to your branch (e.g. `my-fix-branch`).
  * Push the changes to your GitHub repository (this will update your Pull Request).

If the PR gets too outdated we may ask you to rebase and force push to update the PR:

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

## <a name="commit"></a> Git Commit Guidelines

We have a few guidelines about how our git commit messages should be formatted.  This leads to **more
readable messages** that are easy to follow when looking through the **project history**. 

### Commit Message Format
* Use the present tense ("Add feature" not "Added feature")
* Use the imperative mood ("Move cursor to..." not "Moves cursor to...")
* Limit the first line to 72 characters or less
* Reference issues and pull requests liberally
* When only changing documentation, include [ci skip] in the commit description

## <a name="notes"></a> Additional Notes

### Issue and Pull Request Labels

This section lists the labels we use to help us track and manage issues and pull requests. Most labels are used across all Arches Project repositories, but some are specific to `archesproject/arches`.

[github]: https://github.com/archesproject/arches/
[groups]: https://groups.google.com/forum/#!forum/archesproject
