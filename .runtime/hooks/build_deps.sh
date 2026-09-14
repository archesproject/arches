#!/bin/bash
# build_deps.sh — required build-time hook.
#
# Runs during `docker build`, as root, in BOTH stages of production/Dockerfile.alpine.
# Unlike the runtime hooks in this directory, this script does NOT have the
# virtualenv activated, APP_ROOT is not set, and there is no database or
# Elasticsearch available — it runs before any of that exists.
#
# Use this to install OS-level packages your project needs that aren't already
# in the base image (e.g. poppler-utils, extra fonts, a GIS library).
#
# BUILD_STAGE tells you which stage is running:
#   build   — compiles C extensions and builds frontend assets. Install any
#             "-dev" / header packages and build toolchains you need here.
#   deploy  — the final, minimal runtime image. Install only the runtime
#             shared libraries/binaries you actually need at runtime.
#
# This file is copied by name (not the whole directory) into the image build,
# so it must always exist — do not delete it. If you have nothing to install,
# leave it as-is; the no-op case below exits successfully.
#
# Example:
# case "${BUILD_STAGE}" in
#     build)
#         apk add --no-cache some-package-dev
#         ;;
#     deploy)
#         apk add --no-cache some-package
#         ;;
# esac
