class Config:
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:@127.0.0.1/real_estate_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = "af71dccd5debaaea4728896e94dbdd18aeb6f57bfd50b7567caf9bcd5845e1e3"