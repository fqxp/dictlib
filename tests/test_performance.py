import unittest
import timeit

#class TestPerformance(unittest.TestCase):
    #def test_dot_notation_speed(self):
        #t1 = timeit.Timer(u'''d1['a.b.c'] = 42''',
            #u'''from dictlib.mapping import DotNotationAdapter
#d1 = DotNotationAdapter()''').timeit(100000)

        #print u'DotNotationAdapter set value: %r' % t1

        #t2 = timeit.Timer(u'''
            #d2 = {u'a': {u'b': {u'c': 0}}}
            #d2[u'a'][u'b'][u'c'] = 42''').timeit(100000)
        #print u'dict set value: %r' % t2
