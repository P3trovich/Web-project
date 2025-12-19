# tests/test_users.py
import pytest
@pytest.mark.asyncio
async def test_get_news(client):
    """Тест получения списка пользователей"""
    response = await client.get("/news/")
    
    assert response.status_code == 200
    data = response.json()
    
    assert isinstance(data, list)
    
    if data: 
        news = data[0]
        assert "title" in news
        assert "content" in news
        assert "cover_image" in news
        assert "id" in news

@pytest.mark.asyncio
async def test_post_news(client, get_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token}"
    }
    data = {
        "title": "string",
        "content": "string",
        "cover_image": "string",
        "author_id": 1
    }
    response = await client.post("/news/", headers=headers, json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200, f"Creating news failed with status {response.status_code}: {response.text}"
    response_json = response.json()
    print(f"Parsed JSON: {response_json}")
    assert response_json["title"] == "string"

@pytest.mark.asyncio
async def test_update_news(client, get_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token}"
    }
    data = { 
        "title": "str",
        "content": "str",
        "cover_image": "str",
        "author_id": 2
    }
    response = await client.put("/news/1", headers=headers, json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200, f"Updating news failed with status {response.status_code}: {response.text}"
    response_json = response.json()
    print(f"Parsed JSON: {response_json}")
    assert response_json["content"] == "str"

@pytest.mark.asyncio
async def test_create_comment(client, get_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token}"
    }
    data = {
        "text": "string",
        "author_id": 1
    }
    response = await client.post("/news/1/comments/", headers=headers, json=data)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200, f"Creating a comment failed with status {response.status_code}: {response.text}"
    response_json = response.json()
    print(f"Parsed JSON: {response_json}")
    assert response_json["text"] == "string"

@pytest.mark.asyncio
async def test_get_news_by_id(client, get_token):
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {get_token}"
    }
    response = await client.get("/news/1", headers=headers)
    print(f"Response status: {response.status_code}")
    print(f"Response headers: {dict(response.headers)}")
    print(f"Response text: {response.text}")
    assert response.status_code == 200, f"Getting news 1 failed with status {response.status_code}: {response.text}"
    response_json = response.json()
    print(f"Parsed JSON: {response_json}")
    assert response_json["author_id"] == 1
