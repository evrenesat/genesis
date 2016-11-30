# -*-  coding: utf-8 -*-

"""Given an int32 number, print it in English."""
def num2text(num):
    d = { 0 : 'sıfır', 1 : 'bir', 2 : 'iki', 3 : 'üç', 4 : 'dört', 5 : 'beş',
          6 : 'altı', 7 : 'yedi', 8 : 'sekiz', 9 : 'dokuz', 10 : 'on',
          11 : 'on bir', 12 : 'on iki', 13 : 'on üç', 14 : 'on dört',
          15 : 'on beş', 16 : 'on altı', 17 : 'on yedi', 18 : 'on sekiz',
          19 : 'on dokuz', 20 : 'yirmi',
          30 : 'otuz', 40 : 'kırk', 50 : 'elli', 60 : 'altmış',
          70 : 'yetmiş', 80 : 'seksen', 90 : 'doksan' }
    k = 1000
    m = k * 1000
    b = m * 1000
    t = b * 1000

    assert(0 <= num)

    if (num < 20):
        return d[num]

    if (num < 100):
        if num % 10 == 0: return d[num]
        else: return d[num // 10 * 10] + ' ' + d[num % 10]

    if (num < k):
        if num % 100 == 0: return d[num // 100] + ' yüz'
        else: return d[num // 100] + ' yüz ' + num2text(num % 100)

    if (num < m):
        if num % k == 0: return num2text(num // k) + ' bin'
        else: return num2text(num // k) + ' bin ' + num2text(num % k)

    if (num < b):
        if (num % m) == 0: return num2text(num // m) + ' milyon'
        else: return num2text(num // m) + ' milyon ' + num2text(num % m)

    if (num < t):
        if (num % b) == 0: return num2text(num // b) + ' milyar'
        else: return num2text(num // b) + ' milyar ' + num2text(num % b)

    if (num % t == 0): return num2text(num // t) + ' trilyon'
    else: return num2text(num // t) + ' trilyon ' + num2text(num % t)

    raise AssertionError('sayı çok büyük: %s' % str(num))
