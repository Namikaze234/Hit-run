import asyncio
import logging
import os
from pathlib import Path

from playwright.async_api import (
    BrowserContext,
    Page,
    Playwright,
    async_playwright,
)

logger = logging.getLogger(__name__)

BROWSER_URL = os.getenv(
    "BROWSER_URL",
    "https://notrack.ai",
)

BROWSER_PROFILE_DIR = os.getenv(
    "BROWSER_PROFILE_DIR",
    "/home/appuser/browser-profile",
)


class BrowserWorker:
    def __init__(self):
        self.playwright: Playwright | None = None
        self.context: BrowserContext | None = None
        self.page: Page | None = None

    async def start(self):
        logger.info("Starting browser worker...")

        Path(BROWSER_PROFILE_DIR).mkdir(
            parents=True,
            exist_ok=True,
        )

        self.playwright = await async_playwright().start()

        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=BROWSER_PROFILE_DIR,
            headless=False,
            executable_path="/usr/bin/chromium",
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
            ],
            viewport={
                "width": 1280,
                "height": 720,
            },
        )

        if self.context.pages:
            self.page = self.context.pages[0]

            # Keep exactly one browser tab.
            for extra_page in self.context.pages[1:]:
                await extra_page.close()
        else:
            self.page = await self.context.new_page()

        logger.info("Browser started with one persistent tab.")

    async def navigate(self, url: str | None = None):
        if not self.page:
            raise RuntimeError("Browser worker is not started.")

        target_url = url or BROWSER_URL

        logger.info("Navigating to %s", target_url)

        await self.page.goto(
            target_url,
            wait_until="domcontentloaded",
        )

    async def get_page_text(self) -> str:
        if not self.page:
            raise RuntimeError("Browser worker is not started.")

        return await self.page.locator("body").inner_text()

    async def close(self):
        logger.info("Stopping browser worker...")

        if self.context:
            await self.context.close()

        if self.playwright:
            await self.playwright.stop()

        self.page = None
        self.context = None
        self.playwright = None


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    worker = BrowserWorker()

    try:
        await worker.start()
        await worker.navigate()

        logger.info(
            "Browser is running. Current page: %s",
            worker.page.url if worker.page else "unknown",
        )

        # Keep the browser worker alive.
        while True:
            await asyncio.sleep(60)

    except KeyboardInterrupt:
        logger.info("Browser worker interrupted.")

    finally:
        await worker.close()


if __name__ == "__main__":
    asyncio.run(main())
