import hotshot.stats
import sys

stats = hotshot.stats.load(sys.argv[1])
#stats.strip_dirs()
stats.sort_stats('cumtime', 'calls')
stats.print_stats(25)
