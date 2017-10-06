
# Description: This housekeeping script cleans up stoped Docker containers, dangling (unused) images and dito networks.
#			   (Uncomment section below to include volumes in cleanup).
#
# Runs on any OS.

docker container prune -f
docker image prune -f
docker network prune -f

# Remove dangling volumes (carefull...)
# docker volume prune