#!/bin/bash
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Build the oauth2client docs.

set -ev


GITHUB_SLUG="dhermes/ci-diff-helper"

############################################################
# Only update test app if we are on Travis in a push build #
# in the master branch.                                    #
############################################################
if [[ "${TRAVIS_BRANCH}" == "master" ]] && \
       [[ "${TRAVIS_EVENT_TYPE}" == "push" ]]; then
  echo "Updating the test-app branch."
else
  echo "Not in a Travis push build on the master branch."
  exit
fi

# See: https://github.com/travis-ci/travis-ci/issues/6328
# Travis uses a 1.x version of `git` so support for `git worktree`
# is missing. The following is to fake the functionality of:
#     $ git worktree add workspace origin/test-app
git fetch origin test-app
# Needed to simulate `git worktree`: When using a filepath as a git
# remote, only the local branches are fetch-able, not the remote
# branches for that checkout.
git branch test-app FETCH_HEAD
# Simulate `git worktree` by adding directory
mkdir workspace
cd workspace
# Simulate `git worktree` by making it a git repo
git init .
git remote add origin ..
# Work-around for fetching a shallow clone in git 1.x:
# http://stackoverflow.com/a/7989006/1068170
mv ../.git/shallow .
# Fetch the test-app branch
git fetch origin test-app
# Undo work-around
mv shallow ../.git
# Checkout the test app and edit the `LATEST-master` file.
git checkout test-app
(cd .. && git log -1 --pretty=%H) > LATEST-master
# Stage file and make a commit.
git add LATEST-master
git config --global user.email "travis@travis-ci.org"
git config --global user.name "travis-ci"
git commit -m 'Automated update LATEST-master.'
# Push the change to GitHub.
git push --quiet \
  "https://${GITHUB_OAUTH_TOKEN}@github.com/${GITHUB_SLUG}" \
  test-app:test-app
