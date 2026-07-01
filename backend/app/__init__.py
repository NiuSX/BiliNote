from fastapi import FastAPI

from .routers import note, provider, model, config, chat



def create_app(lifespan) -> FastAPI:
    """创建 FastAPI 应用实例，并集中注册所有业务路由。

    这里不直接处理数据库、事件或静态资源初始化；这些启动期副作用统一放在
    backend/main.py 的 lifespan 和中间件配置中，便于测试时只创建轻量 app。
    """
    app = FastAPI(title="BiliNote",lifespan=lifespan)
    # 所有业务接口统一挂载到 /api 前缀下，前端和扩展可以共用同一套代理规则。
    app.include_router(note.router, prefix="/api")
    app.include_router(provider.router, prefix="/api")
    app.include_router(model.router,prefix="/api")
    app.include_router(config.router,  prefix="/api")
    app.include_router(chat.router, prefix="/api")

    return app
