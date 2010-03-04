#!/usr/bin/env python2.6
# coding: utf-8

import types
import unicodedata

from pprint import pprint

def safestr( a ):
    
    if type(a) == types.UnicodeType :
        return a
    
    return unicode( str(a), 'utf-8', 'replace' ).replace('\ufffd','\u00b7')
    
def safelen( a ):
    
    if type(a) == types.StringType :
        return len(a)
    
    if type(a) == types.UnicodeType :
        return sum( [ 2 if unicodedata.east_asian_width(c).startswith('W') else 1 
                      for c in a ])
    
    raise Exception, a
    


def _namescore( name ):
    
    score = 0
    
    name = name.lower()
    
    if name in ( '!','#' ) :
        score += 150
    
    if name.endswith('id') :
        score += 100
        score -= len(name)-2
    
    if name.endswith('name') :
        score += 80
        score -= len(name)-4
    
    if name.startswith('last-') :
        score -= 50
        score -= len(name)-5
        
    if name.find('data') != -1 or name.find('time') != -1 :
        score -= 50
        score -= len(name)-5
    
    if name.find('url') != -1 or name.find('address') != -1 :
        score -= 30
        score -= len(name)-5
    
    return -score

def smartsort( kvpair ):
    
    l = kvpair[:]
    
    l.sort( key = lambda x : [_namescore(x[0]),x[0]] )
    
    return l



def _coltree( Name, d ):
    return ( Name, {}, tuple( _coltree(k, v)
                              for k, v in smartsort( d.items() )
                            )
           )

def _coldata( t ):
    
    if t[2] == ():
        return t[0]
    
    return [ t[0], dict([ (v[0], _coldata(v)) for v in t[2] ]) ]

def getcols( data, level = 2 ):
    
    cols = {}
    
    # breadth-first traversal
    
    s = [ ( data, 0, cols ), ]
    
    while( len(s)!=0 ):
        
        v, lv, r = s.pop(0)
        
        if lv > level :
            continue
        
        if type(v) not in ( types.ListType, types.TupleType ) :
            v = [v,]
            
        for vi in v :
            
            if type(vi) != types.DictType :
                continue
            
            for k in vi.keys():
                r.setdefault( k, {} )
                s.append( ( vi[k], lv+1, r[k] ) )
    
    return _coltree( '', cols )


def _xzip( matrix ):
    
    maxlen = max( [ len(r) for r in matrix ] )
    m2 = [ list(r) + ['',]*(maxlen-len(r)) for r in matrix ]
    
    return zip(*m2)


def _format( v, cols ):
    
    if cols == None or cols[2] == () :
        return safestr(v).splitlines()
        
    if type(v) not in ( types.ListType, types.TupleType ) :
        v = [v,]
        
    r = []
    
    for vi in v :
        
        if type(vi) == types.DictType :
            ri = [ _format( vi[subc[0]], subc ) if subc[0] in vi else ''
                   for subc in cols[2] ]
            r.append( _xzip(ri) )
        else :
            r.append( _format( vi, None ) )
    
    return sum(r,[])



def _width( v, cols ):
    
    if type(v) == types.TupleType :
        r = sum( [ _width( vi, cols[2][i] ) for i, vi in enumerate(v) ] )
        r += len(v)-1
    else :
        r = safelen(v)
    
    cols[1]['__width__'] = max( cols[1].get('__width__',safelen(cols[0])), r )
    
    return cols[1]['__width__']
    
def _colwidth( cols ):
    
    
    cols[1]['__width__'] = max( cols[1].get('__width__'),
                                sum( [ _colwidth(c)+1  for c in cols[2] ] ) -1,
                                *[ safelen(l) for l in cols[0].splitlines()]
                           )
    
    return cols[1]['__width__']

def width( v, cols ):
    
    _colwidth(cols)
    
    for vi in v :
        _width( vi, cols )
    
    
    return

def _print( v, cols ):
    
    if type(v) == types.TupleType :
        return ' '.join([ _print(vi, cols[2][i]) for i, vi in enumerate(v) ])
    else :
        j = cols[1].get( '__just__', 'left' )
        if callable(j):
            j = j(v)
        
        #if j == 'right' :
        #    return v.rjust(cols[1]['__width__'])
        #elif j == 'center' :
        #    return v.center(cols[1]['__width__'])
        #    
        #return v.ljust(cols[1]['__width__'])
        if j == 'right' :
            return ' '*(cols[1]['__width__'] - safelen(v))+v
        elif j == 'center' :
            n = (cols[1]['__width__'] - safelen(v))/2
            m = cols[1]['__width__'] - n
            return ' '*m+v+' '*n
        return v + ( ' '*(cols[1]['__width__'] - safelen(v)) )

def eprint( v, cols ):
    
    for vi in v :
        print _print( vi, cols )
        
def eformat( v, cols ):
    
    return '\r\n'.join( [ _print( vi, cols ) for vi in v ] )
    

def ifdict( di ):
    
    return [ { 'Key':k, 'Value':v } for k, v in di.items() ]

def easyprint( data, cols = None ):
    
    if type(data) == types.DictType :
        data = ifdict(data)
    
    # get the cols if not fixed
    if cols == None :
        cols = getcols( data )
    elif type(cols) == types.IntType :
        cols = getcols( data, cols )
    
    #print cols
    
    fdata = _format( data, cols )
    width( fdata, cols )
    
    cdata = _coldata( cols )
    cdata = _format( cdata, cols )
    
    eprint( cdata, cols )
    print '-'*cols[1]['__width__']
    eprint( fdata, cols )
    
    return


def easyformat( data, cols = None ):
    
    if type(data) == types.DictType :
        data = ifdict(data)
    
    # get the cols if not fixed
    if cols == None :
        cols = getcols( data )
    elif type(cols) == types.IntType :
        cols = getcols( data, cols )
    
    #print cols
    
    fdata = _format( data, cols )
    width( fdata, cols )
    
    cdata = _coldata( cols )
    cdata = _format( cdata, cols )
    
    r = [ eformat( cdata, cols ),
          '-'*cols[1]['__width__'],
          eformat( fdata, cols ) ]
    
    return '\r\n'.join(r)




if __name__ == '__main__' :
    
    a = [ { 'colA' : ['A','B','C','D'], 'colB' : ['A','B','C'] },
          { 'colA' : ['A','B'] , 'colB' : 'A\r\nB\r\nC\r\nD' },
          { 'colA' : ['A\r\nB','C\r\nD'] , 'colB' : 'A\r\nB\r\nC\r\nD' },
        ]
    
    b = [ { 'col A' : 'A.1', 'col B': 'B.1' },
          { 'col A' : 'A.2', 'col B': {'subcol A': 'B.A.2', 'subcol B': 'B.B.2'} },
        ]
    
    c = [ { 'col A' : 'A.1', 'col B': 'B.1' },
          { 'col A' : 'A.2', 'col B': 'B.2' },
        ]
    
    d = [ { 'colA' : 'A.1.alpha\r\nA.1.beta' ,
            'colB' : 'B.1.alpha\r\nB.1.beta\r\nB.1.gamma\r\nB.1.delta' },
          { 'colA' : 'A.2.alpha\r\nA.2.beta' ,
            'colB' : 'B.2.alpha' }
        ]
    
    #easyprint(a)
    easyprint(b)
    print
    easyprint(c)
    print
    easyprint(d)
    
    print
    print easyformat(d)