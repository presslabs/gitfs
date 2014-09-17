from mock import MagicMock, patch

from gitfs.mount import prepare_components


class EmptyObject(object):
    def __init__(self, **kwargs):
        for name, value in kwargs.iteritems():
            setattr(self, name, value)


class TestMount(object):
    def test_prepare_components(self):
        mocked_argparse = MagicMock()
        mocked_parser = MagicMock()
        mocked_args = MagicMock()
        mocked_queue = MagicMock()
        mocked_threading = MagicMock()
        mocked_router = MagicMock()
        mocked_routes = MagicMock()
        mocked_merger = MagicMock()
        mocked_fetcher = MagicMock()
        mocked_fuse = MagicMock()
        mocked_event = MagicMock()
        mocked_merge_worker = MagicMock()
        mocked_fetch_worker = MagicMock()

        args = EmptyObject(**{
            'remote_url': 'remote_url',
            'mount_point': 'mount_point',
            'foreground': True,
            'allow_root': True,
            'allow_others': True,
            'repos_path': 'repos_path',
            'branch': 'branch',
            'user': 'user',
            'group': 'group',
            'max_size': 'max_size',
            'max_offset': 'max_offset',
            'upstream': 'origin',
            'fetch_timeout': 10,
            'merge_timeout': 10,
            'author_name': 'test',
            'author_email': 'tester@test.com',
            'commiter_name': 'commit',
            'commiter_email': 'commiter@commiting.org',
        })

        mocked_argparse.Argumentparser.return_value = mocked_parser
        mocked_args.return_value = args
        mocked_threading.Event.return_value = mocked_event
        mocked_merger.return_value = mocked_merge_worker
        mocked_fetcher.return_value = mocked_fetch_worker
        mocked_router.repo = 'repo'
        mocked_router.repo_path = 'repo_path'

        with patch.multiple('gitfs.mount',
                            MergeQueue=MagicMock(return_value=mocked_queue),
                            threading=mocked_threading,
                            Router=MagicMock(return_value=mocked_router),
                            routes=mocked_routes, MergeWorker=mocked_merger,
                            FetchWorker=mocked_fetcher, FUSE=mocked_fuse):

            assert_result = (mocked_merge_worker, mocked_fetch_worker,
                             mocked_router)

            assert prepare_components(args) == assert_result
            mocked_fetcher.assert_called_once_with(upstream='origin',
                                                   branch='branch',
                                                   repository='repo',
                                                   read_only=mocked_event,
                                                   merge_queue=mocked_queue,
                                                   timeout=10,
                                                   fetching=mocked_event,
                                                   pushing=mocked_event)

            asserted_call = {
                'want_to_merge': mocked_event,
                'somebody_is_writing': mocked_event,
                'read_only': mocked_event,
                'merge_queue': mocked_queue,
                'merging': mocked_event,
                'repository': 'repo',
                'upstream': 'origin',
                'branch': 'branch',
                'timeout': 10,
                'repo_path': 'repo_path',
                'fetching': mocked_event,
                'pushing': mocked_event
            }
            mocked_merger.assert_called_once_with('test', 'tester@test.com',
                                                  'commit',
                                                  'commiter@commiting.org',
                                                  **asserted_call)
