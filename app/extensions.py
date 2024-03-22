from flask_caching import Cache

# Initialize the cache
cache = Cache(config={'CACHE_TYPE': 'SimpleCache'})