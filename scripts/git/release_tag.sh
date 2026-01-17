#!/bin/bash

echo "Tagging project"

read -p "Create a new release tag? (y/n): " create_release_tag

if [ "$create_release_tag" == "y" ]; then
  # MAJOR.MINOR.PATCH
  git status

  read -p "-----Add git changes? (y/n)-----: " add_git_changes

  if [ "$add_git_changes" == "n" ]; then
    echo "Existing"
    exit 1
  fi


  echo "Checkout main branch"
  git checkout main

  read -p "Enter the new release tag (vx.1.x): " release_tag
  read -p "Enter release description: " description
  
  echo "$release_tag"
  echo "$description"
  read -p "Continue? (y/n): " continue

  if [ "$continue" == "y" ]; then
    git tag -a "$create_release_tag" -m "$description"
  fi

  # git push origin v0.1.0

fi
# git checkout main
# git tag -a v0.1.0 -m "Initial working release"
# git push origin v0.1.0