import asyncio
import os
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={"width": 1920, "height": 1080})
        page = await context.new_page()

        print("Navigating to n8n signin...")
        await page.goto("http://trading-podcast-n8n:5678/signin", wait_until="networkidle")
        await page.wait_for_timeout(2000)

        # Check if already logged in or needs login
        email_input = page.locator('input[type="email"], input[name="email"]')
        if await email_input.count() > 0:
            print("Logging in with credentials from environment...")
            admin_email = os.getenv("N8N_ADMIN_EMAIL", "")
            admin_password = os.getenv("N8N_ADMIN_PASSWORD", "")
            if not admin_email or not admin_password:
                raise ValueError("N8N_ADMIN_EMAIL and N8N_ADMIN_PASSWORD environment variables are required for login.")
            await email_input.fill(admin_email)
            pwd_input = page.locator('input[type="password"], input[name="password"]')
            await pwd_input.fill(admin_password)
            await pwd_input.press("Enter")
            await page.wait_for_timeout(4000)

        # Navigate directly to workflow TDGPodcast0001
        print("Navigating to TDGPodcast0001...")
        await page.goto("http://trading-podcast-n8n:5678/workflow/TDGPodcast0001", wait_until="networkidle")
        await page.wait_for_timeout(4000)

        # Press keyboard shortcut 'd' or 'f' or zoom to fit if available
        await page.keyboard.press("Shift+1")
        await page.wait_for_timeout(1500)

        await page.screenshot(path="/app/output/n8n_staged_workflow_canvas.png")
        print("Captured /app/output/n8n_staged_workflow_canvas.png")

        # Open executions list
        print("Navigating to executions...")
        await page.goto("http://trading-podcast-n8n:5678/workflow/TDGPodcast0001/executions", wait_until="networkidle")
        await page.wait_for_timeout(3000)

        # Click the first execution row if available
        exec_rows = page.locator('tr, [data-test-id="execution-list-item"]')
        if await exec_rows.count() > 1:
            try:
                # Click the most recent execution
                await exec_rows.nth(1).click()
                await page.wait_for_timeout(3000)
            except Exception as e:
                print(f"Could not click execution item: {e}")

        await page.screenshot(path="/app/output/n8n_staged_execution_success.png")
        print("Captured /app/output/n8n_staged_execution_success.png")

        await browser.close()
        print("Done capturing screenshots.")

if __name__ == "__main__":
    asyncio.run(main())
