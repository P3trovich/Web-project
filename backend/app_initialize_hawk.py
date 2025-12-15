from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(title="News API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Глобальная переменная для hawk
hawk = None

# Функция для получения hawk (не для инициализации!)
def get_hawk():
    global hawk
    return hawk

# Функция инициализации (вызывается один раз)
def init_hawk():
    global hawk
    
    # Если уже инициализирован, возвращаем
    if hawk is not None:
        return hawk
    
    try:
        from hawk_python_sdk.modules.fastapi import HawkFastapi
        
        hawk = HawkFastapi({
            'app_instance': app,
            'token': os.getenv('HAWK_TOKEN')
        })
        print("Hawk initialized successfully")
        
    except Exception as e:
        print(f"Hawk initialization error: {e}")
    
    return hawk

# Инициализируем hawk ДО старта приложения
init_hawk()