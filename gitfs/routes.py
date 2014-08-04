from views import IndexView, CurrentView, HistoryView, CommitView


# TODO: replace regex with the strict one for the Historyview
# -> r'^/history/(?<date>(19|20)\d\d[-](0[1-9]|1[012])[-](0[1-9]|[12][0-9]|3[01]))/',
routes = [
        (r'^/history/(?P<date>\d{4}-\d{1,2}-\d{1,2})/(?P<time>\d{2}:\d{2}:\d{2})-(?P<commit_sha1>[0-9a-f]{10})', CommitView),
        (r'^/history/(?P<date>\d{4}-\d{1,2}-\d{1,2})', HistoryView),
        (r'^/history', HistoryView),
        (r'^/current', CurrentView),
        (r'^/', IndexView)]
