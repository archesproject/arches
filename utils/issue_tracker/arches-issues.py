
from github import Github
import datetime

# Now configure github and repo
orgName = "archesproject"
repoName = "arches"
userName = "azaroth42"
pwh = open("token.txt")
pw = pwh.read().strip()
pwh.close()
gh = Github(userName, pw)
repo = gh.get_repo("%s/%s" % (orgName, repoName))

# NOTE - This takes quite a while to run, as it involves a LOT of http traffic

collabs = list(repo.get_collaborators())
MAINTAINERS = [x.login for x in collabs if x.permissions.push]
ADMINS = [x.login for x in collabs if x.permissions.admin]
START_DATE = datetime.datetime(year=2018, month=1, day=1)
DO_REVIEW_NUDGE = False

issue_data = {}
issuelist = repo.get_issues(state="open", since=START_DATE)
user_counts = {}

for issue in list(issuelist):
	reactions = list(issue.get_reactions())
	comments = list(issue.get_comments())
	labels = list(issue.get_labels())
	events = list(issue.get_events())
	assignees = issue.assignees
	body = issue.body
	milestone = issue.milestone
	created = issue.created_at
	who = issue.user
	title = issue.title
	num = issue.number
	url = issue.html_url
	is_pr = issue.pull_request and True

	# Count the number of days on which the submitter submitted issues
	try:
		user_counts[who.login]["%s-%s-%s" % (created.year, created.month, created.day)] = 1
	except:
		user_counts[who.login] = {"%s-%s-%s" % (created.year, created.month, created.day): 1}

	weight = 0

	# Completely ignore issues that come from bots
	if who.type == "Bot":
		continue

	# Reduce weight of issues commented on by maintainers
	comment_ok = False
	for c in comments:
		if c.user.login in MAINTAINERS:
			comment_ok = True
			break
	if comment_ok:
		weight -= 10
	else:
		weight += 30

	# Increase weight of issues from non-maintainers
	if not who.login in MAINTAINERS:
		weight += 10
	# Increase weight of pull requests
	if is_pr:
		weight += 20
		# But less if review has been requested
		pr = issue.as_pull_request()
		reviewers = list(pr.get_review_requests()[0])
		if reviewers:
			weight -= 10
			if DO_REVIEW_NUDGE:
				nudge = ["@%s" % x.login for x in reviewers]
				nudge.append(" Can you please review?")
				issue.create_comment(" ".join(nudge))

	# Increase weight if no reactions  (+1, -1, etc)
	if not reactions:
		weight += 5

	# ENHANCEMENT: Increase weight if the issue references other issues
	# It's not evident from the GH API how to extract references to issues
	# It could be hackily done with regexps over the body...
	# ... but that's a terrible idea.

	# Increase weight if no labels
	if not labels:
		weight += 10
	else:
		# Decrease weight if already assigned a priority
		for l in labels:
			if "priority" in l.name.lower() or "roadmap" in l.name.lower():
				weight -= 15
				break

	# ENHANCEMENT: Check if body contains image?
	# ENHANCEMENT: Check if body conforms to existing template?

	# Decrease weight if labeled by someone other than the submitter
	for e in events:
		if e.event == "labeled" and e.actor != who:
			weight -= 5
			break
	# Decrease weight if referenced from somewhere, by a Maintainer
	ref_weight = 0
	for e in events:
		if e.event == "referenced" and e.actor in MAINTAINERS:			
			weight -= 10
			break
			# ENHANCEMENT: Determine if reference is from a merged PR somehow?

	# Decrease weight if it's in a milestone
	if milestone:
		weight -= 10
	# Decrease weight if someone is assigned to working on it.
	if assignees:
		weight -= 20

	# ENHANCEMENT: Decrease weight of issues based on pipelines in zenhub
	# This means interacting with zenhub API, or configuring Zenhub to
	# magically add a milestone or label to track off of

	issue_data[num] = {"title": title, "url": url, "weight": weight, "user": who.login}


issues = list(issue_data.items())

# Decrease weight if the submitter comes back repeatedly
for a in issues:
	w = a[1]['user']
	weight = a[1]['weight']
	n = len(user_counts[w])
	if n > 25:
		weight -= 20
	elif n > 10:
		weight -= 10
	elif n < 3:
		weight += 10
	a[1]['weight'] = weight

issues.sort(key=lambda x: x[1]['weight'], reverse=True)

out = open('issue-list.md', 'w')
out.write("## Issue Prioritization List\n")
for i in issues:
	out.write(" * %s: [%s](%s) (%s)\n" % (i[1]['weight'], i[1]['title'], i[1]['url'], i[0]))

out.close()