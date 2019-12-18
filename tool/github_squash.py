#!/usr/bin/env python

"""
Squash github commits starting from a point
"""

from devrepo import shell

point = "df57d41c8797052f08d3568f7b0159d285735700"
message = "develop"

shell(f"git reset --soft {point}")
shell(f"git add --all")
shell(f"git commit --message='{message}'")
shell(f"git push --force --follow-tags")
