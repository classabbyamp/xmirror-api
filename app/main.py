from uuid import UUID, uuid4

import aioredis

from fastapi import FastAPI

from fastapi_cache import FastAPICache  # type: ignore[import]
from fastapi_cache.backends.redis import RedisBackend  # type: ignore[import]
from fastapi_cache.decorator import cache  # type: ignore[import]

from .models import Mirror, MirrorWithPrivInfo, Message


app = FastAPI()
app.state.redis = aioredis.from_url("redis://172.17.0.2", encoding="utf8", decode_responses=True)


@app.on_event("startup")
async def startup():
    FastAPICache.init(RedisBackend(app.state.redis), prefix="xmirror-api:cache")


@app.get("/manage")
async def management_interface():
    ...


@app.get("/mirrors")
@cache(expire=60)
async def list_all_mirrors():
    return [
        MirrorWithPrivInfo(**(await app.state.redis.hgetall(k)))
        for k in await app.state.redis.keys(pattern="mirror:*")
    ]


@app.get("/mirrors/{mirror_id}", response_model=MirrorWithPrivInfo)
@cache(expire=60)
async def list_mirror(mirror_id: UUID):
    return MirrorWithPrivInfo(**(await app.state.redis.hgetall(f"mirror:{mirror_id}")))


@app.post("/mirrors/add")
async def add_mirror(new_info: MirrorWithPrivInfo):
    mirror_id = uuid4()
    return await app.state.redis.hset(f"mirror:{mirror_id}", mapping=new_info.dict(exclude_unset=True))


@app.post("/mirrors/{mirror_id}/update")
async def update_mirror(mirror_id: UUID, new_info: MirrorWithPrivInfo):
    mapping = new_info.dict(exclude_unset=True)
    if len(mapping):
        return Message(success=True, message=await app.state.redis.hmset(f"mirror:{mirror_id}", mapping=mapping))
    return Message(success=False, message="Nothing Changed")


@app.post("/mirrors/{mirror_id}/delete")
async def delete_mirror(mirror_id: UUID):
    res = await app.state.redis.delete(f"mirror:{mirror_id}")
    return Message(success=True, message=res)


# @app.get("/geo")
# async def get_closest_mirrors(request: Request, n: int = Query(5, gt=0)):
#     client_ip = request.client.host
#     ...
