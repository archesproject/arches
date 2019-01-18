
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

MAINTAINERS = ["dwuthrich", "apeters", "adamlodge", "chiatt", "robgaston", "jmunowitch"]
START_DATE = datetime.datetime(year=2018, month=1, day=1)

# NOTE - This takes quite a while to run, as it involves a LOT of http traffic

issue_data = {}
# Find the issues for the current call
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
	url = issue.url
	is_pr = issue.pull_request and True

	try:
		user_counts[who.login] += 1
	except:
		user_counts[who.login] = 1

	weight = 0

	comment_ok = False
	for c in comments:
		if c.user.login in MAINTAINERS:
			comment_ok = True
			break
	if comment_ok:
		weight -= 10
	else:
		weight += 25
	if not who.login in MAINTAINERS:
		weight += 10
	if is_pr:
		weight += 15
	if not reactions:
		weight += 5
	if not labels:
		weight += 5
	else:
		for l in labels:
			if "priority" in l.name.lower() or "roadmap" in l.name.lower():
				weight -= 10
				break
	if "bug" in title.lower() or "bug" in body.lower():
		weight += 5

	# Check if body contains image

	for e in events:
		if e.event == "labeled" and e.actor != who:
			weight -= 5
			break
	for e in events:
		if e.event == "referenced":
			weight -= 10
	if milestone:
		weight -= 10
	if assignees:
		weight -= 20

	issue_data[num] = {"title": title, "url": url, "weight": weight, "user": who.login}

issues = list(issue_data.items())
for a in issues:
	w = a[1]['user']
	weight = a[1]['weight']
	if user_counts[w] > 25:
		weight -= 25
	elif user_counts[w] > 10:
		weight -= 10
	elif user_counts[w] > 4:
		weight += 5
	a[1]['weight'] = weight

issues.sort(key=lambda x: x[1]['weight'], reverse=True)


out = open('issue-list.md', 'w')
out.write("## Issue Prioritization List\n")
for i in issues:
	out.write(" * (#%s) %s [%s](%s)\n" % (i[0], i[1]['weight'], i[1]['title'], i[1]['url']))

out.close()
