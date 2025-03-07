import asyncio
import random

async def simulate_human_mouse_move(page, start: tuple, end: tuple, steps: int = 20):
    """
    Simulate human-like mouse movement from a start point to an end point.

    Args:
        page: The Playwright page object.
        start: Tuple (x, y) representing starting coordinates.
        end: Tuple (x, y) representing ending coordinates.
        steps: Number of intermediate steps.
    """
    delta_x = (end[0] - start[0]) / steps
    delta_y = (end[1] - start[1]) / steps

    for i in range(steps):
        new_x = start[0] + delta_x * (i + 1)
        new_y = start[1] + delta_y * (i + 1)
        await page.mouse.move(new_x, new_y)
        # Sleep for a random short interval to simulate human delay
        await asyncio.sleep(random.uniform(0.01, 0.05))

async def simulate_human_typing(page, selector: str, text: str, delay_range: tuple = (0.1, 0.3)):
    """
    Simulate human-like typing into an input field.

    Args:
        page: The Playwright page object.
        selector: CSS selector for the input field.
        text: The text to type.
        delay_range: Tuple specifying the minimum and maximum delay between keystrokes.
    """
    for char in text:
        await page.type(selector, char)
        await asyncio.sleep(random.uniform(*delay_range))

async def random_delay(min_delay: float = 0.5, max_delay: float = 1.5):
    """
    Introduce a random delay between actions to simulate human behavior.

    Args:
        min_delay: Minimum delay in seconds.
        max_delay: Maximum delay in seconds.
    """
    delay = random.uniform(min_delay, max_delay)
    await asyncio.sleep(delay)
