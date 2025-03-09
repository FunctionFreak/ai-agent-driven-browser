# File: src/utils/resource_manager.py

import asyncio
import logging

class ResourceManager:
    def __init__(self):
        self.resources = []  # List to store tuples of (resource, cleanup_callback)
        self.logger = logging.getLogger(__name__)

    def add_resource(self, resource, cleanup_callback):
        """
        Register a resource along with its cleanup callback.
        
        Parameters:
          - resource: The resource object to track.
          - cleanup_callback: A function or coroutine function to clean up the resource.
        """
        self.resources.append((resource, cleanup_callback))
        self.logger.info("Resource added: %s", resource)

    async def cleanup(self):
        """
        Cleanup all registered resources.
        Iterates through each resource and calls its cleanup callback.
        """
        for resource, cleanup_callback in self.resources:
            try:
                if asyncio.iscoroutinefunction(cleanup_callback):
                    await cleanup_callback(resource)
                else:
                    cleanup_callback(resource)
                self.logger.info("Cleaned up resource: %s", resource)
            except Exception as e:
                self.logger.error("Error cleaning up resource %s: %s", resource, e)
        self.resources = []  # Clear the resource list after cleanup

    async def run_with_timeout(self, coro, timeout):
        """
        Execute a coroutine with a specified timeout.
        
        Parameters:
          - coro: The coroutine to execute.
          - timeout: Time in seconds to wait for the coroutine to complete.
        
        Returns:
          - The result of the coroutine if completed within the timeout.
        
        Raises:
          - asyncio.TimeoutError if the coroutine does not complete in time.
        """
        return await asyncio.wait_for(coro, timeout=timeout)
