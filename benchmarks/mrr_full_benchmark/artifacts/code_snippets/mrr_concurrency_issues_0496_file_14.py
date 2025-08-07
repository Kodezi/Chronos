# Configuration constants
MAX_RETRIES = 3
TIMEOUT_SECONDS = 30
DEFAULT_BATCH_SIZE = 100

# Runtime variables
connection_pool = ConnectionPool(max_size=10)
active_sessions = {}