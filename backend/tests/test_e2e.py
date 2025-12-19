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
        await page.wait_for_url("**/login", timeout=1000)
        email_input = page.locator('#email')
        await email_input.fill("admin@example.com")
        password_input = page.locator('#password')
        await password_input.fill("admin123")
        await page.click(".login-submit-button")
        await page.wait_for_url("**/", timeout=1000)
        welcome_element = page.locator(".user-info")
        await welcome_element.wait_for(state="visible", timeout=1000)
        welcome_text = await welcome_element.text_content()
        assert "Welcome, admin@example.com" in welcome_text

        # Создание новости
        create_news_link = page.locator(".nav-link", has_text='Create News')
        await create_news_link.click()
        await page.wait_for_url("**/news/create", timeout=1000)
        title_input = page.locator('#title')
        await title_input.fill("E2E test")
        content_input = page.locator('#content')
        await content_input.fill("Testing creating news with E2E test...")
        await page.click(".create-news-submit-button")
        await page.wait_for_url("**/", timeout=1000)

        from database import async_session_maker
        from sqlalchemy import select, func
        from tables.news import News
        async with async_session_maker() as session:
            result = await session.execute(select(func.max(News.id)))
            last_news = result.scalar_one_or_none()

        # Просмотр новости
        await page.goto(f"{BASE_URL}/news/{last_news}")
        title_element = page.locator('.news-detail-title')
        title = await title_element.text_content()
        assert title == 'E2E test'

        # Редактирование новости
        update_news_button = page.locator(".edit-button")
        await update_news_button.click()
        await page.wait_for_url(f"**/news/{last_news}/edit", timeout=1000)
        content_input = page.locator('#content')
        await content_input.fill("Updating news with E2E test...")
        await page.click(".create-news-submit-button")
        await page.wait_for_url(f"**/news/{last_news}", timeout=1000)
        content_element = page.locator('.news-content')
        content = await content_element.text_content()
        assert content == 'Updating news with E2E test...'

        # Удаление новости
        delete_news_button = page.locator(".delete-button")
        page.on('dialog', lambda dialog: dialog.accept())
        await delete_news_button.click()
        await page.wait_for_url("**/", timeout=1000)
        
        await browser.close()