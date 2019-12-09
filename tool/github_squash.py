#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "2f0a0619ffb336b643361d99c8798074cd0f60e3"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
