# Good Practice Guide for Arches Software Contributions

This document describes good practice guides for making software contributions to Arches. The Arches community welcomes and encourages contributions to the Arches software project (https://github.com/archesproject/arches). There are many pathways to contribute to the Arches project. The easiest way to contribute is to report bugs using the project issue tracker (https://github.com/archesproject/arches/issues). If you want to contribute to feature development and refactoring, you will need to invest time and effort gaining familiarity with Arches, its coding patterns and conventions, and its conceptual abstractions.

## Value for Sponsors, Funders, and Project Leads
If you are leading a project or organization planning to modify or extend Arches software, please read this document carefully. The practices described here will reduce costs, reduce long term maintenance and security risks, and will lead to greater impact, enhanced sustainability, and open doors for future opportunities.

## Value for Software Engineers
If you are a software engineer or developer volunteering or tasked with enhancing Arches, this document provides a roadmap that will make your work easier and more rewarding.

## Why Contribute Code?
- **Community impacts**: Arches is widely deployed. Your code contributions to the Arches open source project will have lots of use across a large community.

- **Sustainability, maintenance**: By contributing to Arches, the burden of maintaining is shared across a wider community. Your code contributions will be more likely to get updates and improvements over time.

- **Positive reputation**: By contributing code to the Arches project, you publicly demonstrate special skills and expertise. That helps build positive community recognition that can lead to valuable future opportunities. 

## Avoid (Permanent) Forking of Arches
Creating new code branches that implement bug fixes or other enhancements is a key aspect of collaborative software development. But what happens if the changes in those development branches never come back to improve the main branch? This unhappy scenario leads to a permanent “fork”. 

Divergent (longterm) forks greatly undermines longer term sustainability and maintenance. Forked code may be incompatible with future fixes and enhancements to Arches. It is best practice to make development branches short-lived and temporary by making frequent “pull requests” so that enhancements get incorporated into the main Arches project. 

# Pathway for Code Contributions
1. **Engage with the Arches community**: Join the Arches Community Forum and Slack channels, and watch code repository activity on GitHub. Engaging in the community, especially Developer Discussions (https://community.archesproject.org/c/arches-dev). This will help you learn about the needs, priorities and interests of Arches users as understood by other developers. It will also help you learn about the history and direction of the project. Remember that the Arches community has clear expectations for good conduct, required by all participants (https://www.archesproject.org/code-of-conduct/).

2. **Familiarize yourself with using and running Arches**: It’s a good idea to run and use instances of Arches to get a deeper understanding of its capabilities and approaches to organizing data.

3. **Give yourself time for onboarding**: While Arches uses the Django Framework (familiar to many Python developers), it organizes data in a very abstract manner (see overview: https://arches.readthedocs.io/en/stable/data-model/). These abstractions give Arches users a great deal of flexibility in organizing their own data. However, it will take programmers time to understand the internals of how Arches software manages these abstractions.

4. **Familiarize yourself with good practices in code style**: Python (the language used for the Arches backend) and Javascript have their own stylistic conventions and expectations that can promote readable and understandable code that is easier to maintain. For Python, please adhere to PEP8 conventions (PEP 8 – Style Guide for Python Code | [peps.python.org](https://peps.python.org/pep-0008/)). You can find additional good advice on Python style here (https://docs.python-guide.org/writing/style/), for Javascript look here for code style advice (https://standardjs.com/).

5. **Start with the right branch**: Arches maintains multiple versions of software in parallel. New versions of Arches (identified by highest version numbers) implement the latest features and architectural evolution of the project. While new versions are always in development, earlier versions may also see maintenance updates that fix bugs and have security enhancements. Make sure your own enhancement project starts with the correct branch corresponding to the version of Arches you’re seeking to improve.

6. **Discuss before you start to code**: Before you sit down and open up your code editor, you should use the various community communication channels available (Slack, the Community Forum, the GitHub issues and ticketing system) to discuss your ideas for improving Arches. That way you’ll learn how your ideas may fit into the larger roadmap and you and the rest of the community can plan accordingly. Consider good practices using each communication venue:
    - *Community Forum*: This venue is a good place to discuss and refine development goals at a general and conceptual level. Consistent participation in this forum will mean less duplicative effort and more exchange of ideas that will make your enhancements more likely to be incorporated into Arches.
    - *Slack*: Slack provides an informal, quick but ephemeral place for conversations that help coordinate work, get advice about where to find people and documentation. Because it is ephemeral, please move longer discussions to the Community forum or Github so exchanged knowledge won’t get lost.
    - *GitHub ticketing system*: This channel provides the best place to discuss technical specifics.

7. **Code for intelligibility and maintainability**: Your code contributions will need to be reviewed and maintained by others. That means you should emphasize clarity and provide plenty of clear and succinct documentation about how your code is organized and functions.
 
8. **Provide meaningful tests**: Automated tests help demonstrate that your code behaves as expected. Include test cases that are clear and provide enough coverage to meaningfully encompass the intended functionality of your code.
 
9. **Start simple and small**: Start with small changes to help familiarize yourself with the code review process. It is easier for your colleagues to review and provide feedback on small changes. Gaining such feedback will help you learn more about Arches coding conventions and stylistic expectations so that future larger contributions can be crafted in a manner that is easier to integrate into the larger project.

10. **Work toward accessibility**: The Arches community strives to be inclusive. Changes that impact the user interface need consider accessibility and localization (multi-lingual) needs. We encourage discussion and collaboration to meet these accessibility goals. 

11. **Incrementally work toward bigger goals**: It’s a good idea to incrementally work towards bigger and more significant changes to Arches. First, share and discuss your larger goals. Then break a large enhancement project into smaller parts that can get incrementally reviewed and merged. This provides more opportunity for discussion and feedback.

12. **Build familiarity and trust**: Taking the time to cultivate trust and a good track record with previous contributions will make it more likely for you to succeed in seeing your larger and more significant enhancements integrated into Arches. 
