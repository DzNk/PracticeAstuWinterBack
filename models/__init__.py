from sqlalchemy.orm import configure_mappers

from .base import BaseModel
from .basics import *
from .products import *

configure_mappers()
