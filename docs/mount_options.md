### Mount options
* `branch`: the branch name to follow. Defaults to `master`.

* `remote_url`: the URL of the remote. The accepted formats are:

    * https://username:password@hostname.com/repo.git - for http
    * username@hostname.com:repo.git - for ssh

* `repos_path`: the location where the repos will be cloned. Defaults to `/var/lib/gitfs/HOSTNAME/repo_path`

* `max_size`: the maximum file size in MB allowed for an individual file. If
set to 0 then allow any file size.  The default value is __10__ MB.
* `user`: mount filesystem as this user. Defaults to `root`.
* `group`: mount filesystem as this group. Defaults to `root`.
* `commiter_name`: the name that will be displayed for all the commits. Defaults
to `user`.
* `commiter_email`: the email that will be displayed for all the commits. Defaults
to `user@FQDN`.
* `merge_timeout`: the interval between idle state and commits/pushes.
Defaults to `5 sec`.
* `fetch_timeout`: the interval between fetches. Defaults to `30 sec`.
* `log`: The path for logging. Special name `syslog` will log to the system logger. Defaults to `syslog`.
* `foreground`: specifies whether fuse will in foreground or in backround. Defaults
to `True`.
* `allow_other`:  This option overrides the security measure restricting file access to the user mounting the filesystem.  So all users (including root) can access the files. This option is by default only allowed to root, but this restriction can be removed with a configuration option described in the previous section. Defaults to `True`
* `allow_root`: This option is similar to allow_other but file access is limited to the user mounting the filesystem and root. This option and allow_other are mutu‐ ally exclusive. Defaults to `False`
