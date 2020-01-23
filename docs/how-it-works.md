---
title: How Gitfs works
linktitle: Gitfs explained
description: Gitfs uses fuse to create current and history directories
keywords: [gitfs, readonlyview, passthroughview, currentview, historyview, commitview, indexview, fetchworker, mergeworker]
menu:
  global:
    weight: 1
---

## FUSE

gitfs uses [FUSE](http://fuse.sourceforge.net/) to create its filesystem. It’s used to create the `current` and `history` directories that you can find where you mounted the repository. More on that [here](usage.md#user-content-directory-structure).

## pygit2

[pygit2](https://github.com/libgit2/pygit2) gives us direct access to git and makes room for a lot of optimization. The alternative, using shell commands, would have been a pain to implement and so would have been tying it to a state too.

## Structure

This is a simplified overview of the `gitfs` structure.

## Class diagram

### Router

The `Router` class is used in order to dispatch paths to different `Views`.

### View

Views are used to offer different functionality depending on your current path.

They are divided into two super classes:
- `PassthroughView`
- `ReadOnlyView`

The `PassthroughView` will work just like you would expect a normal directory to. It’s purpose is to map all of `FUSE`'s operations to the similar ones in `Python`.

The `ReadOnlyView` is used when user writes are not desired.

The subclasses of these are:

- `PassthroughView`
  - `CurrentView` – this is the view which handles the current directory and does the automated commits and pushes
- `ReadOnlyView`
  - `HistoryView` – this is the view which handles the history directory and categorizes commits by date
  - `CommitView` – this is the view which handles the `history/*day*` directory
  - `IndexView` – this is the view which handles the `history/*day*/*commit*` directory and shows you a read-only snapshot pointing to that commit

### Worker

All workers inherit the `Peasant` class which is nothing more than a specialized `Thread`.

Here are the workers with their more than explicit names:
- `FetchWorker`
- `MergeWorker`

### Idle mode

gitfs uses the FetchWorker in order to bring your changes from upstream.
The FetchWorker will fetch, by default, at a period of 30 seconds (you can change the timeout at mount, using `-o fetch_timeout=5`, for 5 seconds).

If nothing was changed, for more than 5min on the filesystem, gitfs will enter in idle mode. In this mode, will fetch each 30min. You can modify those parameters using `min_idle_times` in order to change the amount of idle cycles required until gitfs will go in idle mode (by default 10 times, which means 5min) and `idle_fetch_timeout` to control the period of time between fetches, for idle mode.
