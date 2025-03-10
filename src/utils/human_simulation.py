# File: src/utils/human_simulation.py

import random
import asyncio

async def simulate_human_mouse_movement(page, start_x, start_y, end_x, end_y, steps=20):
    """
    Simulate human-like mouse movement using a quadratic Bezier curve.
    Parameters:
      - page: the browser page object.
      - start_x, start_y: starting coordinates.
      - end_x, end_y: destination coordinates.
      - steps: number of intermediate steps to simulate smooth movement.
    """
    # Calculate a control point with random offset for a natural curve
    control_x = (start_x + end_x) / 2 + random.randint(-100, 100)
    control_y = (start_y + end_y) / 2 + random.randint(-100, 100)

    for i in range(steps + 1):
        t = i / steps
        # Quadratic Bezier formula for x and y
        x = (1-t)**2 * start_x + 2*(1-t)*t * control_x + t**2 * end_x
        y = (1-t)**2 * start_y + 2*(1-t)*t * control_y + t**2 * end_y
        await page.mouse.move(x, y)
        await asyncio.sleep(random.uniform(0.005, 0.02))

async def simulate_human_typing(page, selector, text):
    """
    Simulate human-like typing with variable speed.
    Parameters:
      - page: the browser page object.
      - selector: the target input field selector.
      - text: text to be typed.
    """
    await page.click(selector)
    # Clear any pre-existing text
    await page.fill(selector, "")
    for char in text:
        await page.type(selector, char, delay=random.randint(50, 200))
        # Occasionally add a longer pause to mimic human variability
        if random.random() < 0.01:
            await asyncio.sleep(random.uniform(0.5, 1.0))
    await asyncio.sleep(random.uniform(0.1, 0.3))
