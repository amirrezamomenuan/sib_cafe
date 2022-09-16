import time
import redis

rconnection = redis.Redis(host='localhost', port=6379, db=0)

rconnection.set(name='reza', value=22)

res = rconnection.zrevrange(name='leaderboard:455', start=0, end=2, withscores=True)
print(res)
print(type(res))
print(type(res[0][0]))
print(type(res[0][1]))


