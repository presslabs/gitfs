import os
import uuid

from tests.integrations.base import BaseTest, gitfs_log


class TestRepository(BaseTest):

    def test_chmod(self, gitfs_log):
        file_name = "new_file" + str(uuid.uuid4())

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        self.sh.chmod("755", file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        assert os.path.exists("{}/history/{}/{}".format(
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))
        assert oct(
            os.stat(self.current_path + "/" + file_name).st_mode & 0o755
        ) == oct(0o755)

    def test_new_file(self, gitfs_log):
        file_name = "new_file" + str(uuid.uuid4())

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        assert os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_edit_file(self, gitfs_log):
        file_name = "new_file" + str(uuid.uuid4())
        content = "some content"

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        with open(os.path.join(self.remote_repo_path, file_name), "w") as f:
            f.write(content)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        with open(self.repo_path + "/" + file_name) as f:
            assert f.read() == content

        assert os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_delete_content(self):
        file_name = "new_file" + str(uuid.uuid4())

        with open(self.repo_path + "/" + file_name, "w") as f:
            f.write("some content")

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        with open(self.repo_path + "/" + file_name, "w") as f:
            pass

        with open(self.repo_path + "/" + file_name) as f:
            assert f.read() == ""

        assert os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_delete_file(self, gitfs_log):
        file_name = "new_file" + str(uuid.uuid4())

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        self.sh.rm(file_name)

        self.sh.git.rm(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        with gitfs_log(["FetchWorker: Fetch done", "SyncWorker: Set push_successful"]):
            self.sh.git.push("origin", "master")

        assert not os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))
