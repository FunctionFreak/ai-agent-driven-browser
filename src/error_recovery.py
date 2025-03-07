import logging
import asyncio

async def execute_with_retry(action, max_retries=3, initial_delay=1.0, fallback_action=None):
    """
    Execute an asynchronous action with a retry mechanism and exponential backoff.

    Args:
        action (Callable): The async function to execute.
        max_retries (int): Maximum number of retries.
        initial_delay (float): Delay (in seconds) before the first retry.
        fallback_action (Callable, optional): An async function to call if all retries fail.

    Returns:
        Any: The result of the action if successful, or the result of fallback_action if provided.
    
    Raises:
        Exception: The last exception raised if all retries fail and no fallback_action is provided.
    """
    delay = initial_delay
    for attempt in range(max_retries + 1):
        try:
            result = await action()
            return result
        except Exception as e:
            logging.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 1.5  # Exponential backoff
            else:
                logging.error(f"All {max_retries} retries failed.")
                if fallback_action:
                    logging.info("Executing fallback action.")
                    return await fallback_action()
                else:
                    raise e
