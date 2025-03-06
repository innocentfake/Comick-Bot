env_vars = {
  # Other environment variables...
  "CACHE_CHANNEL": "your_channel_name",  # Replace with your desired channel name
  # Other environment variables...
}

dbname = env_vars.get('DATABASE_URL_PRIMARY') or env_vars.get('DATABASE_URL') or 'sqlite:///test.db'

if dbname.startswith('postgres://'):
    dbname = dbname.replace('postgres://', 'postgresql://', 1)