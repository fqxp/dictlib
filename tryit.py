from dictlib.mixins import DotNotationMixin, ObjectMappingAdapter,\
    ObjectMappingMixin, DotNotationAdapter

class X(DotNotationMixin, dict):
    pass

class Y(ObjectMappingMixin, dict):
    pass

class Z(DotNotationMixin, ObjectMappingMixin, dict):
    pass

class A(dict):
    pass

if __name__ == u'__main__':
    x = X()
    x[u'b.0'] = 5
    x[u'b.3'] = 666
    print x
    
    y = Y()
    y.a = 5
    y.b = {'c': 777}
    y.b.c = 888
    y.x = {}
    y.x.y = 500
    print y
    
    z = Z()
    z[u'z.0'] = 5
    z[u'z.3'] = 666
    z.a = 5
    z.b = {'c': 777}
    z.b.c = 888
    z[u'b.c'] = 999
    z.b = {'x.y': 777}
    z.x = {}
    z.x.y = 500
    print z
    
    a = {'a': 44, 'b': {'c': 22}}
    aa = DotNotationAdapter(a)
    aa[u'b.c'] = 33
    print u'b.c' in aa
    print aa