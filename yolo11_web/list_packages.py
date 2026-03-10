# -*- coding: utf-8 -*-
import pkg_resources

packages = sorted([d.project_name for d in pkg_resources.working_set])
for p in packages:
    if "lang" in p.lower() or "fast" in p.lower() or "pyd" in p.lower():
        print(p)
