import pytest
from playwright.async_api import async_playwright
BASE_URL = 'http://frontend:3000'

@pytest.mark.asyncio
async def test_ui():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()
        await page.goto(BASE_URL)

        # Вход в систему
        await page.click(".nav-link")
        await page.wait_for_url("**/login", timeout=5000)
        email_input = page.locator('#email')
        await email_input.fill("admin@example.com")
        password_input = page.locator('#password')
        await password_input.fill("admin123")
        await page.click(".login-submit-button")
        await page.wait_for_url("**/", timeout=10000)
        welcome_element = page.locator(".user-info")
        await welcome_element.wait_for(state="visible", timeout=10000)
        welcome_text = await welcome_element.text_content()
        assert "Welcome, admin@example.com" in welcome_text

        # Создание новости
        create_news_link = page.locator(".nav-link", has_text='Create News')
        await create_news_link.click()
        await page.wait_for_url("**/news/create", timeout=5000)
        title_input = page.locator('#title')
        await title_input.fill("E2E test")
        content_input = page.locator('#content')
        await content_input.fill("Testing creating news with E2E test...")
        await page.click(".create-news-submit-button")
        await page.wait_for_url("**/", timeout=10000)

        # Просмотр новости
        await page.goto(f"{BASE_URL}/news/3")
        title_element = page.locator('.news-detail-title')
        title = await title_element.text_content()
        assert title == 'E2E test'

        await browser.close()