from mock import MagicMock, patch, call

from gitfs.mount import prepare_components, parse_args, start_fuse


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
        mocked_router = MagicMock()
        mocked_routes = MagicMock()
        mocked_merger = MagicMock()
        mocked_fetcher = MagicMock()
        mocked_fuse = MagicMock()
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
            'commiter_name': 'commit',
            'commiter_email': 'commiter@commiting.org',
            'log': 'syslog'
        })

        mocked_argparse.Argumentparser.return_value = mocked_parser
        mocked_args.return_value = args
        mocked_merger.return_value = mocked_merge_worker
        mocked_fetcher.return_value = mocked_fetch_worker
        mocked_router.repo = 'repo'
        mocked_router.repo_path = 'repo_path'

        with patch.multiple('gitfs.mount',
                            MergeQueue=MagicMock(return_value=mocked_queue),
                            Router=MagicMock(return_value=mocked_router),
                            routes=mocked_routes, MergeWorker=mocked_merger,
                            FetchWorker=mocked_fetcher, FUSE=mocked_fuse):

            assert_result = (mocked_merge_worker, mocked_fetch_worker,
                             mocked_router)

            assert prepare_components(args) == assert_result
            mocked_fetcher.assert_called_once_with(upstream='origin',
                                                   branch='branch',
                                                   repository='repo',
                                                   timeout=10)

            asserted_call = {
                'repository': 'repo',
                'upstream': 'origin',
                'branch': 'branch',
                'timeout': 10,
                'repo_path': 'repo_path',
                'merge_queue': mocked_queue
            }
            mocked_merger.assert_called_once_with('commit',
                                                  'commiter@commiting.org',
                                                  'commit',
                                                  'commiter@commiting.org',
                                                  **asserted_call)

    def test_args(self):
        mocked_parser = MagicMock()
        mocked_args = MagicMock()

        mocked_args.return_value = "args"

        with patch.multiple('gitfs.mount', Args=mocked_args):
            assert parse_args(mocked_parser) == "args"
            asserted_calls = [call('remote_url', help='repo to be cloned'),
                              call('mount_point',
                                   help='where the repo should be mount'),
                              call('-o', help='other options: repos_path, ' +
                                   'user, group, branch, max_size, ' +
                                   'max_offset, fetch_timeout, merge_timeout')]
            mocked_parser.add_argument.has_calls(asserted_calls)

    def test_start_fuse(self):
        mocked_parse_args = MagicMock()
        mocked_prepare = MagicMock()
        mocked_argp = MagicMock()
        mocked_fuse = MagicMock()
        mocked_args = MagicMock()

        mocked_merge = MagicMock()
        mocked_fetch = MagicMock()
        mocked_router = MagicMock()

        mocked_prepare.return_value = (mocked_merge, mocked_fetch,
                                       mocked_router)
        mocked_argp.ArgumentParser.return_value = "args"
        mocked_parse_args.return_value = mocked_args

        with patch.multiple('gitfs.mount', argparse=mocked_argp,
                            parse_args=mocked_parse_args,
                            prepare_components=mocked_prepare,
                            FUSE=mocked_fuse):
            start_fuse()

            mocked_argp.ArgumentParser.assert_called_once_with(prog='GitFS')
            mocked_parse_args.assert_called_once_with("args")
            mocked_prepare.assert_called_once_with(mocked_args)
            assert mocked_merge.start.call_count == 1
            assert mocked_fetch.start.call_count == 1

            excepted_call = {
                'foreground': mocked_args.foreground,
                'nonempty': True,
                'allow_root': mocked_args.allow_root,
                'allow_other': mocked_args.allow_other,
                'fsname': 'GitFS'
            }
            mocked_fuse.assert_called_once_with(mocked_router,
                                                mocked_args.mount_point,
                                                **excepted_call)
