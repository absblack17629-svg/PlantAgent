# -*- coding: utf-8 -*-
"""
CRUD模块
"""

from crud.base import CRUDBase
from crud.detection import crud_detection
from crud.users import crud_user
from crud.news import crud_news
from crud.favorite import crud_favorite
from crud.history import crud_history

__all__ = [
    "CRUDBase",
    "crud_detection",
    "crud_user",
    "crud_news",
    "crud_favorite",
    "crud_history"
]
