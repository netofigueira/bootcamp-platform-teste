from enum import Enum

#nomes dos ambientes 

class Environment(Enum):
    PRODUCTION = 'production'
    STAGING = 'staging'
    DEV = 'dev'