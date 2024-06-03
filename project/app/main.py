import os
import uvicorn
from fastapi import Request, Response
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from .config.db_config import get_session
from .models.models import Claim, ClaimCreate, ClaimTopProvider
from sqlalchemy.sql import func
from sqlalchemy import desc
# open telelemetry
from .config.otlp_config import instrument_tracing
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import generate_latest, REGISTRY, CONTENT_TYPE_LATEST
from .models.topNPriorityQueue import TopNPriorityQueue
# redis for rate limiter and caching
import redis.asyncio as redis
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from fastapi_redis_cache import FastApiRedisCache, cache


app = FastAPI()
# adds fastapi default app metrics to prometheus registry
Instrumentator().instrument(app)
# instrument opentelemetry tracing
instrument_tracing(app)

# The `@app.on_event("startup")` decorator in FastAPI is used to register a startup event handler
# function that will be executed when the application starts up. In the provided code snippet, the
# `startup()` function is an event handler that establishes a connection to a Redis server using the
# URL provided in the `REDIS_URL` environment variable. It also initializes FastAPI Limiter with the
# Redis connection and sets up a FastAPI Redis cache for caching responses.
@app.on_event("startup")
async def startup():

    redisUrl = os.environ.get("REDIS_URL")
   # The code snippet `redis_connection = redis.from_url(redisUrl, encoding="utf-8",
   # decode_responses=True)` is establishing a connection to a Redis server using the URL provided in
   # the `redisUrl` environment variable. The `encoding="utf-8"` parameter specifies the encoding to
   # be used for the connection, and `decode_responses=True` indicates that responses from Redis
   # should be decoded as UTF-8 strings.
    redis_connection = redis.from_url(redisUrl, encoding="utf-8", decode_responses=True)
    await FastAPILimiter.init(redis_connection)
    
    # The code snippet is initializing a FastAPI Redis cache
    redis_cache = FastApiRedisCache()
    redis_cache.init(
        host_url=redisUrl,
        prefix="myapi-cache",
        response_header="X-MyAPI-Cache",
        ignore_arg_types=[Request, Response, AsyncSession]
    )


# `pq = TopNPriorityQueue(n=10)` is initializing a priority queue data structure with a maximum size
# of 10. This priority queue, represented by the variable `pq`, will maintain the top N elements based
# on a specific priority criterion. In this case, it is used to keep track of the top providers based
# on their net fees in the given FastAPI application. The priority queue will ensure that only the top
# 10 providers with the highest net fees are retained, discarding any additional elements beyond this
# limit.
pq = TopNPriorityQueue(n=10)

@app.get("/hello")
async def hello():
    """
   The function "hello" returns a JSON response with the key "ping" set to "hello!".
   :return: The function `hello()` is returning a dictionary with the key "ping" and the value
   "hello!".
   """
    return {"ping": "hello!"}

@app.get("/metrics")
async def get_metrics():
    """Returns all metrics registered in the Prometheus registry"""
    return Response(content=generate_latest(REGISTRY), media_type=CONTENT_TYPE_LATEST)


@app.post("/claims")
async def add_multiple_claims(claims: list[ClaimCreate], session: AsyncSession = Depends(get_session)):
    """
    The function `add_multiple_claims` in a Python FastAPI app adds multiple claims to a database and
    calculates the net fee for each claim.
    
    :param claims: The `claims` parameter in the `add_multiple_claims` endpoint is a list of
    `ClaimCreate` objects. Each `ClaimCreate` object represents a claim with the following attributes:
    :type claims: list[ClaimCreate]
    :param session: The `session` parameter in the `add_multiple_claims` function is an instance of an
    AsyncSession. It is used to interact with the database to add new Claim records. The `session`
    object allows you to perform database operations like adding, committing, and refreshing objects
    within an asynchronous context
    :type session: AsyncSession
    :return: The function `add_multiple_claims` is an endpoint that receives a list of `ClaimCreate`
    objects, creates new `Claim` objects based on the data provided in each `ClaimCreate` object, saves
    them to the database using the provided session, and then returns a list of the newly created
    `Claim` objects. The net fee for each claim is calculated as the sum of the provider fees, member
    co-pay, and member co-insurance, minus the allowed fees.
    """
    claimsResp = []
    for claim in claims:
        claim = Claim(service_dttm = claim.service_dttm,
                      submitted_proc=claim.submitted_proc,
                      group_id=claim.group_id,
                      subscriber_id=claim.subscriber_id,
                      provider_npi=claim.provider_npi,
                      provider_fees=claim.provider_fees,
                      allowed_fees=claim.allowed_fees,
                      member_co_ins=claim.member_co_ins,
                      member_co_pay=claim.member_co_pay,
                      quadrant=claim.quadrant,
                      net_fee=claim.provider_fees + claim.member_co_pay + claim.member_co_ins - claim.allowed_fees)
        # The code snippet `session.add(claim)`, `await session.commit()`, `await
        # session.refresh(claim)`, `claimsResp.append(claim)`, and
        # `pq.push(ClaimTopProvider(claim.provider_npi, claim.net_fee))` in the `add_multiple_claims`
        # function is performing the following tasks:
        # 1. Adding the newly created `Claim` object to the session.
        session.add(claim)
         # 2. Committing the transaction to save the `Claim` object to the database.
        await session.commit()
        # 3. Refreshing the `Claim` object to reflect any changes made during the commit.
        await session.refresh(claim)
         # 4. Appending the newly created `Claim` object to the `claimsResp` list.
        claimsResp.append(claim)
         # 5. Pushing a `ClaimTopProvider` object with the provider NPI and net fee to the priority queue
        pq.push(ClaimTopProvider(claim.provider_npi, claim.net_fee))
      
    return claimsResp

@app.get("/top-provider", dependencies=[Depends(RateLimiter(times=10, seconds=60))])
# The `@cache(expire=60)` decorator in the FastAPI endpoint function `get_top_provider` is
# implementing caching functionality for the corresponding endpoint. Here's what it does:
# - The `cache(expire=60)` decorator is used to cache the response of the `get_top_provider` endpoint
# for 60 seconds. This means that the response will be stored in the cache for 60 seconds, and if the
# same request is made within that time frame, the cached response will be returned instead of
# re-executing the endpoint logic.
@cache(expire=60)
async def get_top_provider(request: Request, response: Response, session: AsyncSession = Depends(get_session)):
    """
    This function retrieves the top 10 providers based on net fee either from cache or by querying the
    database if the cache is empty.

     The `dependencies=[Depends(RateLimiter(times=10, seconds=60))` part in the
     FastAPI endpoint decorator is implementing rate limiting functionality for
     the corresponding endpoint. Here's what it does:
     - The `RateLimiter(times=10, seconds=60)` dependency is used to limit the rate of requests to the
     endpoint. It allows a maximum of 10 requests per 60 seconds. If the rate limit is exceeded, the
     endpoint will return a 429 Too Many Requests response.
    
    :param request: The `request` parameter in the `get_top_provider` function represents the incoming
    HTTP request made to the endpoint. It contains information about the request such as headers, query
    parameters, and more. You can use this parameter to access and process data sent in the request,
    such as extracting query parameters or
    :type request: Request
    :param response: The `response` parameter in your FastAPI endpoint function represents the HTTP
    response that will be sent back to the client making the request. You can use it to modify the
    response before sending it back. In your code snippet, you are not currently using the `response`
    parameter, but you can utilize
    :type response: Response
    :param session: The `session` parameter in your FastAPI endpoint function `get_top_provider` is an
    instance of an asynchronous session that is used to interact with the database. In this case, it is
    obtained using the `get_session` dependency
    :type session: AsyncSession
    :return: The code snippet provided is a FastAPI endpoint that retrieves the top 10 providers based
    on their net fee from a database. If the priority queue (pq) is empty, it queries the database for
    the top providers, stores the result in a priority queue, and returns the top providers. If the
    priority queue is not empty, it directly returns the top providers from the cached priority queue.
    """
    if pq.is_empty():
        print("Non-cache top n")
        result = await session.execute(select(Claim.provider_npi, func.sum(Claim.net_fee).label('net_fee')).group_by(Claim.provider_npi).order_by(desc('net_fee')).limit(10))
        claimsRes = []
        for row in result:
            claimsRes.append({"provider_npi": row["provider_npi"],"net_fee": row["net_fee"]})
        await setTopPQ(claimsRes)
        return claimsRes
    else:
        print("Cached top n")
        return pq.get_top_n()
    


async def setTopPQ(claimsRes: []):
    """
    The function `setTopPQ` takes a list of claims results and pushes them into a priority queue based
    on provider NPI and net fee.
    
    :param claimsRes: A list of dictionaries containing information about claims. Each dictionary in the
    list should have keys "provider_npi" and "net_fee" to represent the NPI (National Provider
    Identifier) of a healthcare provider and the net fee associated with a claim, respectively
    :type claimsRes: []
    """
    for claim in claimsRes:
        pq.push(ClaimTopProvider(claim["provider_npi"], claim["net_fee"]))



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)  # pragma: no cover