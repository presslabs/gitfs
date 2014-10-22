# Copyright 2014 PressLabs SRL
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


import os
import time
import pytest
import string

from tests.integrations.base import BaseTest, pull
from fuse import FuseOSError


class TestWriteCurrentView(BaseTest):
    def test_write_a_file(self):
        content = "Just a small file"
        filename = "%s/new_file" % self.current_path

        with open(filename, "w") as f:
            f.write(content)

        time.sleep(5)

        # check if the write was done correctly
        with open(filename) as f:
            assert f.read() == content

        # check if a commit was made
        with pull(self.sh):
            self.assert_new_commit()

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Update /new_file")

    def test_create_a_directory(self):
        directory = "%s/new_directory" % self.current_path

        os.makedirs(directory)

        time.sleep(5)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/new_directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check for .keep file
            keep_path = "%s/new_directory/.keep" % self.repo_path
            assert os.path.exists(keep_path)

            self.assert_new_commit()
            self.assert_commit_message("Create the /new_directory directory")

    def test_create_embedded_directory(self):
        directory = "%s/directory/embedded-directory" % self.current_path

        os.makedirs(directory)

        time.sleep(5)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/directory/embedded-directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/directory/.keep" % self.repo_path,
                "%s/directory/embedded-directory/.keep" % self.repo_path
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Update 2 items"
            self.assert_commit_message(commit_msg)

    def test_create_directory_inside_an_already_existing_directory(self):
        directory = "%s/directory/new-embedded-directory" % self.current_path

        os.makedirs(directory)

        time.sleep(5)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/directory/new-embedded-directory" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/directory/.keep" % self.repo_path,
                "%s/directory/new-embedded-directory/.keep" % self.repo_path
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Create the /directory/new-embedded-directory directory"
            self.assert_commit_message(commit_msg)

    def test_create_embedded_directory_on_multiple_levels(self):
        directory = "%s/a/b/c" % self.current_path

        os.makedirs(directory)

        time.sleep(5)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = "%s/a/b/c" % self.repo_path
            assert os.path.exists(directory_path)

            # check the existence of the .keep files
            keep_files = [
                "%s/a/.keep" % self.repo_path,
                "%s/a/b/.keep" % self.repo_path,
                "%s/a/b/c/.keep" % self.repo_path,
            ]
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

            self.assert_new_commit()
            commit_msg = "Update %s items" % len(keep_files)
            self.assert_commit_message(commit_msg)

    def test_create_embedded_directory_big_depth(self):
        path = ""
        for letter in string.letters:
            path = os.path.join(path, letter)

        os.makedirs(os.path.join(self.current_path, path))

        time.sleep(5)

        with pull(self.sh):
            # check if directory exists or not
            directory_path = os.path.join(self.repo_path, path)
            assert os.path.exists(directory_path)

            # build the paths for the keep files
            keep_files = []
            path = self.repo_path
            for letter in string.letters:
                path = os.path.join(path, letter)
                path_with_keep = os.path.join(path, '.keep')
                keep_files.append(path_with_keep)

            # check the existence of the .keep files
            for keep_file in keep_files:
                assert os.path.exists(keep_file)

    def test_chmod_valid_mode(self):
        filename = "%s/testing" % self.current_path
        os.chmod(filename, 0755)

        time.sleep(5)

        with pull(self.sh):
            # check if the right mode was set
            stats = os.stat(filename)
            assert stats.st_mode == 0100755

            self.assert_new_commit()
            self.assert_commit_message("Chmod to 0755 on /testing")

    def test_chmod_invalid_mode(self):
        filename = "%s/testing" % self.current_path

        with pytest.raises(OSError):
            os.chmod(filename, 0777)


    def test_rename(self):
        old_filename = "%s/testing" % self.current_path
        new_filename = "%s/new_testing" % self.current_path

        os.rename(old_filename, new_filename)

        time.sleep(5)

        with pull(self.sh):
            # check for new file
            assert os.path.exists(new_filename)

            self.assert_new_commit()
            self.assert_commit_message("Rename /testing to /new_testing")

    def test_fsync(self):
        filename = "%s/me" % self.current_path
        content = "test fsync"

        with open(filename, "w") as f:
            f.write(content)
            os.fsync(f.fileno())

        time.sleep(5)

        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Update 1 items")

    def test_create(self):
        filename = "%s/new_empty_file" % self.current_path
        open(filename, "a").close()

        time.sleep(5)

        with pull(self.sh):
            self.assert_new_commit()
            self.assert_commit_message("Created /new_empty_file")

    def test_symbolic_link(self):
        target = "me"
        name = "%s/links" % self.current_path
        os.symlink(target, name)

        time.sleep(5)

        with pull(self.sh):
            # check if link exists
            assert os.path.exists(name)

            self.assert_new_commit()
            self.assert_commit_message("Create symlink to %s for "
                                       "/links" % (target))

    def test_edit_file(self):
        content = "first part"
        continuation = "second part"
        filename = "%s/some_file" % self.current_path

        with open(filename, "w") as f:
            f.write(content)

        time.sleep(5)

        with pull(self.sh):
            with open(filename) as f:
                assert f.read() == content

            self.assert_new_commit()

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Update /some_file")

            with open(filename, "w") as f:
                f.write(continuation)

        time.sleep(5)

        with pull(self.sh):
            with open(filename) as f:
                assert f.read() == continuation

            self.assert_new_commit()

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Update /some_file")

    def test_create_multiple_files(self):
        content = "Just a small file"
        no_of_files = 10
        filename = "%s/new_file" % self.current_path

        for i in range(no_of_files):
            with open(filename + str(i), "w") as f:
                f.write(content)

        time.sleep(5)

        with pull(self.sh):
            for i in range(no_of_files):
                with open(filename + str(i)) as f:
                    assert f.read() == content

            self.assert_new_commit()

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Update %d items" % no_of_files)

    def test_delete_file(self):
        filename = "%s/deletable_file" % self.current_path

        with open(filename, "w") as f:
            f.write("some content")

        time.sleep(5)

        with pull(self.sh):
            self.assert_new_commit()

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Update /deletable_file")

        os.remove(filename)

        time.sleep(10)

        with pull(self.sh):
            assert not os.path.exists(filename)

        time.sleep(1)

        with pull(self.sh):
            self.assert_commit_message("Deleted /deletable_file")
