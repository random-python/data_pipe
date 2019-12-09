#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "02a700108d486f6a13a2eaf2b8f08edb5c20ab1d"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
