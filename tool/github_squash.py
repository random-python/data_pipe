#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "d775bdbf42c369117d30ee98973d06e2e43c0335"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
