import time
import os
from tests.integrations.base import BaseTest


class TestRepository(BaseTest):
    def test_new_file(self):
        file_name = "new_file"

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        assert os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_edit_file(self):
        file_name = "new_file"
        content = "some content"

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        with open(self.repo_path + "/" + file_name, "w") as f:
            f.write(content)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        with open(self.repo_path + "/" + file_name) as f:
            assert f.read() == content

        assert os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_delete_content(self):
        file_name = "new_file"

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

    def test_delete_file(self):
        file_name = "new_file"

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        self.sh.rm(file_name)

        self.sh.git.rm(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        assert not os.path.exists(self.current_path + "/" + file_name)
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))

    def test_chmod(self):
        file_name = "new_file"

        self.sh.touch(file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        self.sh.chmod("755", file_name)

        self.sh.git.add(file_name)
        self.sh.git.commit("-m", '"Just a message."')
        self.sh.git.push("origin", "master")

        time.sleep(5)

        assert oct(os.stat(self.current_path + "/" + file_name).st_mode & 0777) ==\
            "0755"
        assert os.path.exists("%s/history/%s/%s" % (
            self.mount_path,
            self.get_commit_dates()[0],
            self.get_commits_by_date()[0]
        ))