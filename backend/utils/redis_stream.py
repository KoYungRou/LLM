import redis
import json
import os
import asyncio
import uuid
from typing import Dict, Any
import logging

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisStreamClient:
    """Client for interacting with Redis Streams."""
    
    def __init__(self):
        """Initialize Redis client connection."""
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_port = int(os.getenv("REDIS_PORT", 6379))
        self.redis_db = int(os.getenv("REDIS_DB", 0))
        self.redis_password = os.getenv("REDIS_PASSWORD", None)
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Connect to Redis."""
        try:
            self.redis = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                db=self.redis_db,
                password=self.redis_password,
                decode_responses=True
            )
            self.redis.ping()  # Test connection
            logger.info("Connected to Redis server")
        except redis.exceptions.ConnectionError as e:
            logger.warning(f"Could not connect to Redis: {str(e)}. Using fallback mode.")
            self.redis = None
    
    async def publish(self, stream: str, data: Dict[str, Any]) -> None:
        """
        Publish data to a Redis stream.
        
        Args:
            stream: The name of the stream
            data: The data to publish
        """
        if not self.redis:
            logger.info(f"Fallback mode: Would have published to '{stream}': {data}")
            return
        
        try:
            # Generate a unique ID for the message
            message_id = str(uuid.uuid4())
            
            # Convert data to string dictionary
            string_data = {k: json.dumps(v) if isinstance(v, (dict, list)) else str(v) 
                         for k, v in data.items()}
            
            # Add message to the stream
            self.redis.xadd(stream, string_data, id=f'*')
            
            logger.info(f"Published to stream '{stream}': {data}")
        except Exception as e:
            logger.error(f"Error publishing to Redis stream: {str(e)}")
    
    async def consume(self, stream: str, group: str, consumer: str, count: int = 1):
        """
        Consume messages from a Redis stream.
        
        Args:
            stream: The name of the stream
            group: The consumer group name
            consumer: The consumer name
            count: Max number of messages to read
            
        Returns:
            List of consumed messages
        """
        if not self.redis:
            logger.info(f"Fallback mode: Would have consumed from '{stream}'")
            return []
        
        try:
            # Ensure the stream and consumer group exist
            try:
                self.redis.xgroup_create(stream, group, id='0', mkstream=True)
                logger.info(f"Created consumer group '{group}' for stream '{stream}'")
            except redis.exceptions.ResponseError as e:
                if "already exists" not in str(e):
                    raise
            
            # Read messages from the stream
            messages = self.redis.xreadgroup(
                group, consumer,
                {stream: '>'},
                count=count, block=1000
            )
            
            if not messages:
                return []
            
            result = []
            for stream_name, stream_messages in messages:
                for message_id, message_data in stream_messages:
                    # Deserialize JSON values
                    deserialized_data = {}
                    for k, v in message_data.items():
                        try:
                            deserialized_data[k] = json.loads(v)
                        except (json.JSONDecodeError, TypeError):
                            deserialized_data[k] = v
                    
                    # Acknowledge the message
                    self.redis.xack(stream, group, message_id)
                    
                    # Add to result
                    result.append({
                        'id': message_id,
                        'data': deserialized_data
                    })
            
            return result
            
        except Exception as e:
            logger.error(f"Error consuming from Redis stream: {str(e)}")
            return []