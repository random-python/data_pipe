#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "e64fbbdb04f9cd43f7f3e58688c4ac1e2c2bbb45"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
