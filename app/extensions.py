from flask_cache import Cache

# Initialize the cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})