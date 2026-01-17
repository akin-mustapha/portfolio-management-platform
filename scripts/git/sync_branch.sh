#!/bin/bash

echo "Syncing project to git"

git status

read -p "Create a new branch? (y/n): " create_branch
if [ "$create_branch" == "y" ]; then
    read -p "Enter the new branch name: " new_branch_name
    git checkout -b "$new_branch_name"
    echo "Switched to new branch: $new_branch_name"
fi

branch_name=$(git symbolic-ref --short HEAD)

echo "Using branch name: $branch_name"

read -p "Add changed files to git? (y/n): " add_files
if [ "$add_files" == "y" ]; then
  git add .
fi

read -p "Commit message? (y/n): " commit_message_flag
commit_message="$branch_name"
if [ "$commit_message_flag" == "y" ]; then
    read -p "Enter commit message: " commit_message
fi

git commit -m "$commit_message"

# git commit -m "Update apartment model"

git push --set-upstream origin "$branch_name"