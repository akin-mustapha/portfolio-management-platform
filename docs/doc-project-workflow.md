---
name: project-workflow
description: Document highlighting project workflow
---

# Overview

This documentation provided the branch stretegy for this project

## New Feature

When adding a new feature

*-* create a story or epic

## Documentation

When making documentation changes or adding a new documentation create `doc/example-branch`

## Task

*-* Task should be single unit of work, which cover just one intent and problem.

*-* It should also be focused on just one architectural layer alone, don't make database changes and pipeline changes at the same time.

## Bug

* When you encounter a bug
  * Document the bug
    * Where should they be documented
    * How should the docs be named
    * Should you put the error code, how to generate bug
  * Create TODO for bug
  * Research bug
  * Further document the bug
  * Create git issue
  * Set-up project branch
  * Limit branch changes to just intent/problem fix/feature

## Git

**When to create a branch**: Branches should always to lined to an `issue`

**How to name a branch**: Branches should be named after the issue `example-branch-name`
