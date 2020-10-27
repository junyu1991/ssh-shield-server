import hashlib
import time


'''
根据userid以及当前时间戳生成roomid
@param: userid 用户id
@return: 生成的roomid
'''
def getRoomID(userid):
    m = hashlib.sha256()
    m.update(userid.encode())
    m.update(str(time.time()).encode())
    return m.hexdigest()
