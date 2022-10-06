import os

class Config:
    DEBUG = False
    DEVELOPMENT = False
    LIMESURVEY_PASS = os.getenv("LIMESURVEY_PASS", "this-is-the-default-key")
    GMAIL_PASS = os.getenv("GMAIL_PASS", "this-is-the-default-key")

class ProductionConfig(Config):
    pass

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True