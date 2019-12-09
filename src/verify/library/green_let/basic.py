from greenlet import greenlet


def test1():
    print(12)
    print(greenlet.getcurrent())
    gr2.switch()
    print(34)


def test2():
    print(56)
    print(greenlet.getcurrent())
    gr1.switch()
    print(78)


gr1 = greenlet(test1)
gr2 = greenlet(test2)

print(greenlet.getcurrent())

gr1.switch()
