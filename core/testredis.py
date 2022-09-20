import time
import redis

rconnection = redis.Redis(host='localhost', port=6379, db=0)

# rconnection.set(name='reza', value=22)

# res = rconnection.zrevrange(name='leaderboard:455', start=0, end=2, withscores=True)
# print(res)
# print(type(res))
# print(type(res[0][0]))
# print(type(res[0][1]))

rconnection.set(name=10, value=15)
r1 = rconnection.get(10).decode('utf-8')
print(type(r1))
print(r1)

r2 = rconnection.get('10').decode('utf-8')
print(type(r2))
print(r2)

rconnection.set('food:10', 4.316006108611031)
print(rconnection.get('food:10'))

rconnection.incr('reza', -100)
print(rconnection.get('eivazzadeh'))