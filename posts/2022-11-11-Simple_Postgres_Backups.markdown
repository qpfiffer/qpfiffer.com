---
title: Simple Postgres Backups
author: Quinlan Pfiffer
tags: software, postgres
---

You'll need Postgres installed somewhere, and my favorite program ever,
[logpurge.](https://github.com/nijotz/logpurge)

1. Create a `backup.sh` script that looks like this:

```
#!/bin/bash

pg_dump -Fc mzbh > /var/backups/db_backups/db-$(date '+%Y-%m-%d_%H:%M:%S').gz
logpurge -y -d /var/backups/db_backups/
```

This will tell Postgres to dump to gzip'd files that look something like
`db-2022-11-11_19:41:57.gz`. It will also run `logpurge` in that directory,
which will keep more recent backups but delete older ones, keeping some around
for access, logarithmically.

2. Setup a cron job like so:

```
$ crontab -e
17 2 * * * /var/backups/db_backups/backup.sh
```

This will run your backup nightly at 2:17 AM. And you're done! You could add a
neat little monitoring hook like [Deadman's Snitch](https://deadmanssnitch.com/)
if you wanted to get really fancy.
