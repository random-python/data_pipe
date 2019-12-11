#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "4d21ad080fdfaf1f1d90c59251e3063ce48b3671"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
