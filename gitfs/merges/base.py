from collections import namedtuple

from pygit2 import GIT_SORT_TOPOLOGICAL

from gitfs.utils.commits import CommitsList


DivergeCommits = namedtuple("DivergeCommits", ["common_parent",
                            "first_commits", "second_commits"])


class Merger(object):
    def __init__(self, repository, **kwargs):
        self.repository = repository
        for arg in kwargs:
            setattr(self, arg, kwargs[arg])

    def find_diverge_commits(self, first_branch, second_branch):
        """
        Take two branches and find diverge commits.

             2--3--4--5
            /
        1--+              Return:
            \               - common parent: 1
             6              - first list of commits: (2, 3, 4, 5)
                            - second list of commits: (6)

        :param first_branch: first branch to look for common parent
        :type first_branch: `pygit2.Branch`
        :param second_branch: second branch to look for common parent
        :type second_branch: `pygit2.Branch`
        :returns: a namedtuple with common parent, a list of first's branch
        commits and another list with second's branch commits
        :rtype: DivergeCommits (namedtuple)
        """

        common_parent = None
        first_commits = CommitsList()
        second_commits = CommitsList()

        walker = self.repository.walk_branches(GIT_SORT_TOPOLOGICAL,
                                               first_branch, second_branch)

        for first_commit, second_commit in walker:
            if (first_commit in second_commits or
               second_commit in first_commits):
                break

            if first_commit not in first_commits:
                first_commits.append(first_commit)
            if second_commit not in second_commits:
                second_commits.append(second_commit)

            if second_commit.hex == first_commit.hex:
                break

        if first_commit in second_commits:
            index = second_commits.index(first_commit)
            second_commits = second_commits[index:]
            common_parent = first_commit
        else:
            index = first_commits.index(second_commit)
            first_commits = first_commits[index:]
            common_parent = second_commit

        return DivergeCommits(common_parent, first_commits, second_commits)
