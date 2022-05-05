import random


def get_userTeamName() -> str:
    usableName_char = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"  # 可作为用户名的字符
    e_userName = ''  # 定义一个临时List变量,使用list.append添加字符
    for i in range(8):
        e_userName = e_userName + (random.choice(usableName_char))
    return e_userName

