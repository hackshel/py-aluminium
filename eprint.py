
import types
import unicodedata
import xml.sax.saxutils as saxutils
from Al import realnum


"""
foreground
\033[38;5;(256colorcode)[;(my32bitcolorcode)]m
background
\033[48;5;(256colorcode)[;(my32bitcolorcode)]m
\033[0m
"""

class STREND(object):
    pass

class ColorString(object) :
    
    def __init__( self, s='', ascode=None, fg=None, bg=None ):
        
        self.s = unicode(s) if ascode == None else s.decode(ascode)
        self.displaylen = ColorString.displaylength(self.s)
        self.foreground = realnum.Line()
        self.background = realnum.Line()
        
        if fg.__class__ == realnum.Line :
            self.foreground = fg
        elif fg != None :
            self.fgcolor(fg)
        
        if bg.__class__ == realnum.Line :
            self.background = bg
        elif bg != None :
            self.bgcolor(bg)
        
    def fgcolor( self, color, s=0, e=STREND, mode='cover' ):
        
        if s == e :
            return
        
        e = self.displaylen if e == STREND else e
        
        if mode == 'cover' :
            self.foreground[s:e] = color
        elif mode == 'back' :
            self.foreground = realnum.Line([(s,color),(e,None)]).merge( self.foreground )
            #self.foreground.merge(realnum.Line([(s,color),(e,None)]))
        else :
            raise ValueError, 'ColorString:foreground not supported the mode'
        
    def bgcolor( self, color, s=0, e=STREND, mode='cover' ):
        
        if s == e :
            return
        
        e = self.displaylen if e == STREND else e
        
        if mode == 'cover' :
            self.background[s:e] = color
        elif mode == 'back' :
            self.background = realnum.Line([(s,color),(e,None)]).merge( self.background )
            #self.background.merge()
        else :
            raise ValueError, 'ColorString:foreground not supported the mode'

    @staticmethod
    def displaylength( s ):
        return sum( 2 if unicodedata.east_asian_width(c).startswith('W') else 1 
                    for c in s if c not in "\r\n\b" )
    
    @staticmethod
    def colorsign( f, b ):
        if f == None and b == None:
            return '\033[0m'
        if f == None :
            return '\033[0m\033[48;5;%dm' % (b,)
        if b == None :
            return '\033[0m\033[38;5;%dm' % (f,)
        return '\033[38;5;%dm\033[48;5;%dm' % (f,b)
        
    def __str__( self ):
        
        P = self.foreground.zip( self.background, f = lambda x, y : ( x, y ) )
        
        #print self.foreground, self.background, P
        
        return ''.join( self.colorsign(f,b) + self.s[s:e].encode('utf-8') 
                        for s, e, (f, b) in P )
        
        #return self.s.encode('utf-8')
        
    def __repr__( self ):
        
        return str(self)
        
    def join( self, iterstr ):
        
        iterstr = [ ColorString(a) if a.__class__ != ColorString else a 
                    for a in iterstr ]
        
        s = self.s.join( a.s for a in iterstr )
        lentable = reduce( lambda x, y: x+[x[-1]+y,x[-1]+y+self.displaylen], 
                           (a.displaylen for a in iterstr), [0] )[:-1]
        
        xiterstr = [ aa for a in iterstr for aa in [a,self] ][:-1]
        
        fg = [ realnum.Line( [ ( k+lt if k !=None else None, v ) 
                               for k, v in a.foreground.tolist() ] ) 
               for lt, a in zip( lentable, xiterstr ) ]
        fg = reduce( lambda x, y: x.merge(y), fg, realnum.Line() )
        
        bg = [ realnum.Line( [ ( k+lt if k !=None else None, v ) 
                               for k, v in a.background.tolist() ] ) 
               for lt, a in zip( lentable, xiterstr ) ]
        bg = reduce( lambda x, y: x.merge(y), bg, realnum.Line() )
        
        #print fg, bg
        return ColorString( s, fg=fg, bg=bg )
    
    @staticmethod
    def sum( iterstr ):
        
        iterstr = [ ColorString(a) if a.__class__ != ColorString else a 
                    for a in iterstr ]
        
        s = ''.join( a.s for a in iterstr )
        
        lentable = reduce( lambda x, y: x+[x[-1]+y], 
                           (a.displaylen for a in iterstr), [0] )[:-1]
        
        fg = [ realnum.Line( [ ( k+lt if k !=None else None, v ) 
                               for k, v in a.foreground.tolist() ] ) 
               for lt, a in zip( lentable, iterstr ) ]
        fg = reduce( lambda x, y: x.merge(y), fg, realnum.Line() )
        
        bg = [ realnum.Line( [ ( k+lt if k !=None else None, v ) 
                               for k, v in a.background.tolist() ] ) 
               for lt, a in zip( lentable, iterstr ) ]
        bg = reduce( lambda x, y: x.merge(y), bg, realnum.Line() )
        
        return ColorString( s, fg=fg, bg=bg )
    
    def __add__( self, another ):
        
        another = ColorString(another) \
                            if another.__class__ != ColorString else another
        
        s = self.s + another.s
        
        fg = self.foreground.merge( 
                realnum.Line( [ ( k+self.displaylen if k !=None else None, v ) 
                                for k, v in another.foreground.tolist() ] ) 
             )
             
        bg = self.background.merge( 
                realnum.Line( [ ( k+self.displaylen if k !=None else None, v ) 
                                for k, v in another.background.tolist() ] ) 
             )
        
        return ColorString( s, fg=fg, bg=bg )



def AutoNode( d ):
    
    if issubclass( d.__class__, Node ):
        return d
    return Text( str(d) )


class Node( object ):
    
    def __init__( self, nclses=[], styles = {}, nid=None,
                        *contains, **_styles ):
        
        self.contains = [ AutoNode(c) for c in contains ]
        
        self.styles = styles.copy()
        self.styles.update(_styles)
        self.nclses = nclses
        self.nid = nid
        
        return
        
    def use_stylesheet( self, stylesheet ):
        
        styles = {}
        
        for c in self.nclses :
            styles.update( stylesheet.get(c,{}) )
        
        styles.update(self.styles)
        
        self.styles = styles
        
        for ct in self.contains :
            ct.use_stylesheet( stylesheet )
        
        return
        
    def _console_length_( self, d=None ):
        
        if d == None :
            lo = self.styles.get( 'layout', 'horizontal' )
            if lo == 'horizontal' :
                d = sum( self.contains._console_length_() ) if self.contains else 1
            elif lo == 'vertical' :
                d = max( self.contains._console_length_() ) if self.contains else 1
        
        # up ringt down left
        padding = self.styles.get( 'padding', [0]*4 )
        
        return max( self.styles.get( 'width', d ),
                    self.styles.get( 'min-width', 0 )
               ) + padding[1] + padding[3]
        
    def _console_height_( self, d=None ):
        
        if d == None :
            lo = self.styles.get( 'layout', 'horizontal' )
            if lo == 'horizontal' :
                d = max( self.contains._console_height_() ) if self.contains else 1
            elif lo == 'vertical' :
                d = sum( self.contains._console_height_() ) if self.contains else 1
        
        # up ringt down left
        padding = self.styles.get( 'padding', [0]*4 )
        
        return max( self.styles.get( 'height', d ), 
                    self.styles.get( 'min-height', 0 )
               ) + padding[0] + padding[2]
        
    def _console_printchild_( self, w, h ):
        
        lo = self.styles.get( 'layout', 'horizontal' )
        border = self.styles.get( 'borderchars', ' xx-x+++x+++|+++' )
        
        padding = self.styles.get( 'padding', 0 )
        _h = h - padding[0] - padding[2]
        _w = w - padding[1] - padding[3]
        
        if lo == 'horizontal' :
            cts = [ ct._console_print_( ct._console_length_(), _h ) 
                    for ct in self.contains ]
            cts = zip( *cts )
            cts = [ ColorString.sum(row)[:_w] for row in cts ]
            cts = [ row + ColorString(' '*(_w-len(row))) for row in cts ]
        elif lo == 'vertical' :
            cts = [ ct._console_print_( _w, ct._console_height_() ) 
                    for ct in self.contains ]
            cts = sum( cts )[:_h]
            cts = cts + [ ColorString(' '*_w) ]*(_h-len(cts))
            
        cts = [ ColorString(' '*(padding[1])) + row + \
                                                ColorString(' '*(padding[3])) 
                for row in cts ]
            
        cts = [ ColorString(' '*w) ]*padding[0] + cts + \
              [ ColorString(' '*w) ]*padding[2]
              
        return cts
        
    def _console_print_( self, w, h ):
        
        bg = self.styles.get('background', None)
        
        if not self.contains :
            return [ ColorString(' '*w, bg=bg ) for i in range(h) ]
        
        self._console_printchild_( w, h )
        
        if bg :
            for l in cts :
                l.bgcolor( bg, mode = 'back' )
        
        return cts
        
    def _html_print_( self, pname='div' ):
        
        st = '' if st == {} else \
                 ( 'style="' + ';'.join( ('%s: %v' % x) for x in self.styles.items() ) + '"' )
        nid = 'id="%s"' % ( str(nid), ) if self.nid != None else '' 
        return '<%s %s %s />' % (pname,st,nid)
        #e = "</%s>" % (pname,)
        
    def add_node_cls( self, cls ):
        
        self.nclses += [cls]
        
        return

class Text( Node ):
    
    def __init__( self, text, **styles ):
        
        super( Text, self ).__init__( **styles )
        
        self.texts = text.splitlines() or ['']
        
        return
        
    def __repr__( self ):
        
        return 'Text('+repr('\r\n'.join(self.texts))+')'
        
    @staticmethod
    def _onelinelen( a ):
        
        if type(a) == types.StringType :
            return len(a)
        
        if type(a) == types.UnicodeType :
            return sum( [ 2 if unicodedata.east_asian_width(c).startswith('W') \
                            else 1 
                          for c in a ])
        
    def _console_length_( self ):
        
        l = max( [ self._onelinelen(l) for l in self.texts ] )
            
        return super( Text, self )._console_length_( l )
            
    def _console_height_( self ):
        
        h = len( self.texts )
        
        return super( Text, self )._console_height_( l )
        
    def _console_print_( self, w, h ):
        
        # up ringt down left
        padding = self.styles.get( 'padding', 0 )
        _h = h - padding[0] - padding[2]
        _w = w - padding[1] - padding[3]
        
        v_align = self.styles.get('vertical-align','middle')
        r = self.texts[:_h]
        if v_align == 'top' :
            r = ['']*padding[0] + r + ['']*( h - len(r) - padding[0] )
        elif v_align == 'bottom' :
            r = ['']*( h - len(r) - padding[2] ) + r + ['']*padding[2]
        elif v_align == 'middle' :
            bt = ['']*( padding[0] + (_h - len(r))/2 )
            bb = ['']*( h - len(bt) - len(r) )
            r = bt + r + bb
            
        align = self.styles.get('align','center')
        
        if align == 'left' :
            align = lambda s : ' '*padding[1] + s.ljust( w, ' ' ) + ' '*padding[3]
        elif align == 'right' :
            align = lambda s : ' '*padding[1] + s.rjust( w, ' ' ) + ' '*padding[3]
        elif align == 'center' :
            align = lambda s : ' '*padding[1] + s.center( w, ' ' ) + ' '*padding[3]
        
        fg = self.styles.get('color', None)
        bg = self.styles.get('background', None)
        
        r = [ ColorString( align(l[:w]), fg=fg, bg=bg ) for l in r ]
        
        return r
        
    def _html_print_( self, pname='div' ):
        
        r = '<br>'.join([ saxutils.escape(l) for l in self.texts ])
        
        st = '' if st == {} else \
                 ( 'style="' + ';'.join( ('%s: %v' % x) for x in self.styles.items() ) + '"' )
        nid = 'id="%s"' % ( str(nid), ) if self.nid != None else '' 
        
        return '<%s %s %s>%s</%s>' % (pname,st,nid,r,pname)
    

class Number( Text ):
    
    def __init__( self, n, **styles ):
        
        super( Text, self ).__init__( '', **styles )
        
        self.value = n
        self.isfloat = ( type(n) == types.FloatType )
        self.defaultformat = '%d' \
                    if type(n) in ( types.IntType, types.LongType ) else '%0.2f'
        
        return
        
    def _console_length_( self ):
        
        f = self.styles.get('number-format', [ '%d', '%0.2f' ] )
        f = f[1] if self.isfloat else f[0]
        
        l = len( f % (self.value,) )
        
        return super( Number, self )._console_length_( l )
        
    #def _console_height_( self ):
    #    return 1
        
    def _console_print_( self, w, h ):
        
        f = self.styles.get('number-format', [ '%d', '%0.2f' ] )
        f = f[1] if self.isfloat else f[0]
        
        self.texts = [ f % (self.value,), ]
        
        self.styels.setdefault( 'align', 'right' )
        
        return super( Number, self )._console_print_( w, h )
        

class Bool( Text ):
    
    def __init__( self, b, **styles ):
        
        super( Text, self ).__init__( '[ ]' if b else '[+]', **styles )
        
        self.value = b
        
    def _console_length_( self ):
        
        f = self.styles.get('number-format', [ '[ ]', '[+]' ] )
        l = len( f[1] if self.value else f[0] )
        
        return super( Bool, self )._console_length_( l )
        
    #def _console_height_( self ):
    #    
    #    return 1
    
    def _console_print_( self, w, h ):
        
        f = self.styles.get('number-format', [ '[ ]', '[+]' ] )
        
        self.texts = f[1] if self.isfloat else f[0]
        
        return super( Bool, self )._console_print_( w, h )
    
    

class Bar( Node ):
    
    def __init__( self, number, contain=None, **styles ):
        
        super( Bar, self ).__init__( **styles )
        
        self.number = number if number < 1 else 1
        self.contains.append( AutoNode(contain if contain else number )  )
        self.add_node_cls('epBar')
        
    def use_stylesheet( self, stylesheet ):
        
        super( Bar, self ).use_stylesheet(stylesheet)
        
        self.styles.setdefault( 'padding', [ 0, 1, 0, 1 ] )
        
        return
        
    def _console_print_( self, w, h ):
        
        bg = self.styles.get( 'background', 235 )
        
        cts = self._console_printchild_( w, h )
        
        
        for l in r :
            
            e = int(l.displaylen*self.number)
            if e <= 0 :
                continue
            
            l.bgcolor( bg, s=0, e=e, mode='back' )
        
        return r
        
    def _html_print_( self, pname='div' ):
        
        r = self.contain._html_print_( 'div' )
        
        st = '' if st == {} else \
                 ( 'style="' + ';'.join( ('%s: %v' % x) for x in self.styles.items() ) + '"' )
        nid = 'id="%s"' % ( str(nid), ) if self.nid != None else '' 
        
        return """\
<%s %s %s>
<div style="width: %s%%">
<div>
%s
</div>
</div>
</%s>""" % (pname,st,nid,int(self.number*100),r,pname)
        

class Table( Node ):
    
    def __init__( self, contains=[], headers=[], **styles ):
        
        #self.number = number if number < 1 else 1
        super( Table, self ).__init__( **styles )
        
        self.contains = contains
        self.headers = headers
        self.x_max = max( (x+l) for x, y, l, h, n in contains )
        self.y_max = max( (y+h) for x, y, l, h, n in contains )
        self.add_node_cls('epTable')
        
    def _console_length_( self ):
        
        return
        
    def _console_height_( self ):
        
        return
        
    @staticmethod
    def _adjust_span( wholesize, span, nsize, bordersize ):
        
        truesize = wholesize - ( span - 1 ) * bordersize
        
        divsize = truesize - sum(nsize)
        
        if divsize <= 0 :
            return nsize
        
        snsize = list(enumerate(nsize))
        snsize.sort( key = lambda x : x[1] )
        
        i = 0
        while( divsize > 0 ):
            
            if i == span-1 :
                
                d = divsize / span
                snsize = [ ( n, p+d ) for n, p in snsize ]
                z = divsize % span
                snsize[:z] = [ ( n, p+1 ) for n, p in snsize[:z] ]
                
                divsize = 0
                    
            elif snsize[i][1] < snsize[i+1][1] :
                
                d = snsize[i+1][1] - snsize[i][1]
                s = d*(i+1)
                
                if divsize >= s :
                    
                    snsize[:i+1] = [ ( n, p+d ) for n, p in snsize[:i+1] ]
                    divsize -= s
                    
                else :
                    
                    d = divsize / (i+1)
                    snsize[:i+1] = [ ( n, p+d ) for n, p in snsize[:i+1] ]
                    z = divsize % (i+1)
                    snsize[:z] = [ ( n, p+1 ) for n, p in snsize[:z] ]
                
                    divsize = 0
                
            else :
                i += 1
        
        snsize.sort( key = lambda x : x[0] )
        
        return zip(*snsize)[1]
    
    @staticmethod
    def _adjust( contains, segmax, bordersize ):
        
        directseg = [ [ size for seg, span, size in contains
                             if span == 1 and seg == s
                      ] for s in range(segmax) ]
        
        directseg = [ max( s or [1] ) for s in directseg ]
        
        indirectseg = [ zip( range( seg, seg+span ),
                             Table._adjust_span( size, span, 
                                        directseg[seg:seg+span], bordersize )
                        ) for seg, span, size in contains if span != 1 ]
        
        indirectseg = sum( indirectseg, [] )
        
        return [ max( [ size for seg, size in indirectseg if seg == s ] + \
                      [directseg[s]] 
                 ) for s in range(segmax) ]
    
    @staticmethod
    def _reducebykey( f, sequence, initial ):
        
        d = {}
        
        for k, v in sequence :
            d[k] = f( d.get(k, initial), v )
        
        return d.items()
    
    def _console_print_( self, w=None, h=None ):
        
        #
        #      2
        #      |
        #  0 --+-- 1
        #      |
        #      3
        #
        #  0000 0001 0010 0011  0100  0101  0110  0111
        #   0    1     2    3     4     5     6     7
        #
        #                               |    |      |
        #       [x]   [x]  ---   [x]  --+    +--   -+-
        #
        #  1000 1001 1010 1011  1100  1101  1110  1111
        #   8    9    10   11    12    13    14    15
        #
        #                         |     |    |      |
        #  [x]  --+   +--  -+-    |   --+    +--   -+-
        #         |   |     |     |     |    |      |
        #
        
        border = self.styles.get( 'borderchars', ' xx-x+++x+++|+++' )
        border_fgc, border_bgc = self.styles.get( 'bordercolor', (237,None) )
        #border_fgc, border_bgc = styles.get( 'bordercolor', (22,None) )
        border_width = 1 if border[3] else 0
        border_heigth = 1 if border[12] else 0
        
        widths = self._adjust( [ ( x, l, n._console_length_() )
                                 for x, y, l, h, n in self.contains ],
                               self.x_max, border_width )
        heigths = self._adjust( [ ( y, h, n._console_height_() )
                                  for x, y, l, h, n in self.contains ],
                                self.y_max, border_heigth )
        
        bcstr = lambda x : ColorString(x, bg = border_bgc, fg = border_fgc )
        
        cell_width = lambda x, l : sum( widths[x:x+l] ) + (l-1)*border_width
        cell_heigth = lambda y, h : sum( heigths[y:y+h] ) + (h-1)*border_heigth
        
        cells = [ ( x, y, l, h, n._console_print_( cell_width( x, l ), 
                                                   cell_heigth( y, h ), 
                                                   stylesheet ) )
                  for x, y, l, h, n in self.contains
                ]
        
        #
        # +------------+---------+   <---------- tb[0]
        # |            |         |   <-- tp[0]
        # +------------+---------+   <---------- tb[1]
        # |                      |   <-- tp[1]
        # +----------------------+   <---------- tb[2]
        #
        
        unborder = dict( ( ( x, y+i ), c[cell_heigth(y,i):][:border_heigth] )
                           for x, y, l, h, c in cells for i in range( 1, h ) )
        
        #_unborder = dict( ( ( x, y+i ), (cell_heigth(y,i),border_heigth) )
        #                   for x, y, l, h, c in cells for i in range( 1, h ) )
        #print _unborder
        
        #       (3)
        # (10) ------ (9)
        #   |          |
        #   |          | (12)
        #   |          |
        #  (6) ------ (5)
        
        dots = [ [ ( (x, y), 10 ), ( (x+l, y), 9 ), 
                   ( (x, y+h), 6 ), ( (x+l, y+h), 5 ) ] + \
                 [ ( (_x, y+i), 12 ) for _x in [ x, x+l ] 
                                     for i in range( 1, h ) ] + \
                 [ ( (x+i, _y), 3 ) for _y in [ y, y+h ] 
                                    for i in range( 1, l ) ]
                 for x, y, l, h, c in cells ]
        
        dots = sum( dots, [] )
        
        dots = self._reducebykey( lambda x, y : x | y, dots, 0 )
        
        dots = [ [ ( x, v ) for ( x, y ), v in dots if y == _y ] 
                for _y in range(self.y_max+1) ]
        
        for row in dots :
            row.sort( key = lambda r : r[0] )


        grating = [ ( [ unborder.get( ( x, y ), 
                               [ bcstr( border[3]*widths[x] ) ]*border_heigth )
                        for x, v in row[:-1]
                      ] + [ [''] ],
                      [ [bcstr(border[v])]*border_heigth for x, v in row ],
                    ) for y, row in enumerate(dots)
                  ]
        
        
        
        grating = [ zip( zip(*dts), zip(*g) ) for g, dts in grating ]
        
        grating = [ [ [ ii for i in zip(*r) for ii in i ] for r in row ]
                    for row in grating ]
        
        grating = [ [ ColorString.sum(line) for line in row ] 
                    for row in grating ]
        
        
        
        grids = [ ( ( x, y+i, l ), c[cell_heigth(y,i)+border_heigth:][:heigths[y]] )
                  for x, y, l, h, c in cells for i in range(h) ]
        
        grids = [ dict( ( x+i, c if i==0 else None ) 
                    for (x, y, l), c in grids if y == _y for i in range(l) ) 
                  for _y in range(self.y_max) ]
        
        #print grids[2], cell_heigth(y,1)+border_heigth, heigths[0]
        
        #for row in grids :
        #    row.sort( key = lambda r : r[0] )
        
        #grids = [ zip(*row)[1] for row in grids ]
        
        grids = [ [ row.get( c, [' '*widths[c]]*heigths[i] ) 
                    for c in range(self.x_max) ] 
                  for i, row in enumerate( grids ) ]
        
        grids = [ [ c for c in row if c != None ] for row in grids ]
        
        grids = [ [ bcstr(border[12]) + \
                    bcstr(border[12]).join(l) + \
                    bcstr(border[12])
                  for l in zip(*row) ] 
                for row in grids  ]
        
        grids = grids + [[]]
        
        #lines = sum( sum( ( list(r) for r in zip( tb[:-1], lines ) ), [] ), [] ) + tb[-1]
        
        lines = [ l for a, i in zip( grating, grids ) for l in (a+i) ]
        
        return lines
        
    def _html_print_( self, ):
        
        
        return


class EasyPrinter( object ):
    
    covert = {}
    
    def __init__( self, ):
        
        return
        
    def htmltable( self, ):
        
        return
        
    def eprint( self, ):
        
        return
        
    def _colssort( self, cols ):
        
        return
        
    def _parse_inner( self, data, rk=(), pth=(), strick=False, covert={} ):
        
        cvrt = covert.get( rk, lambda x : x )
        
        print rk, covert
        
        data = cvrt(data)
        
        cvrt = covert.get( type(data), None ) or \
                    self.covert.get( type(data), lambda x : x )
        
        data = cvrt(data)
        
        if type(data) not in ( types.ListType, types.TupleType ):
            return [( rk, pth, AutoNode(data) ),]
        
        a = [ self._parse_inner( v, tuple(list(rk)+[k]), tuple(list(pth)+[i]), covert = covert )
              for i, _a in enumerate(data) if type(_a) == types.DictType for k, v in _a.items() ]
        
        b = [ ( rk, tuple(list(pth)+[i]), AutoNode(_a) )
              for i, _a in enumerate(data) if type(_a) != types.DictType ]
        
        return sum( a, [] ) + b
        
    @staticmethod
    def _fast_get_childrows( i, p, x ):
        
        s = 0
        
        #print x, p[i:], i
        
        for c, e in p[i:]:
            if c[:len(x)] == x :
                s += e
            else :
                return s
        
        return s
        
    def _parse( self, data, covert={}, format={} ):
        '''
        convert :
        
        format :
        ( A, (A2,A1) ) : None
        ( C, ) : under(A, )
        ( D, ) : inner(B, )
        
        +---------+---------+
        |    A    |    B    |
        +----+----+---------+
        | A2 | A1 |    D    |
        +----+----+---------+
        |    C    |         |
        +---------+---------+
        
        '''
        
        tbv = self._parse_inner( data, covert=covert )
        
        print tbv
        
        ks = [ tuple(k[:i]) for k, pth, v in tbv for i in range(1,len(k)+1) ]
        ks = list( set( ks ) )
        ks.sort()
        
        kcs = [ ( k, sum( 1 for _k in ks 
                            if len(_k) > len(k) and _k[:len(k)] == k ) ) 
                for k in ks ]
        
        #        key end  cols
        kcs = [ ( k, c==0, max(c,1) ) for k, c in kcs ]
        
        colnum = [ ( 1 if e else 0 ) for k, e, c in kcs ]
        colnum = reduce( lambda x, y : x+[x[-1]+y], colnum, [0] )
        
        colnum, colsum = colnum[:-1], colnum[-1]
        #colsum = sum( 1 for k, e, c in kcs if e )
        
        rowmax = max( len(k) for k in ks )
        
        #tbs_k = [ [ ( rowmax-len(k)+1 if e else 1 , c, k[-1] ) 
        #            for k, e, c in kcs if len(k) == r+1 ] 
        #          for r in range(rowmax) ]
        
        # x, y, cols, rows, node
        t = [ ( x, len(k)-1, c, rowmax-len(k)+1 if e else 1, Text(k[-1]) ) 
              for ( k, e, c ), x in zip( kcs, colnum )  ]
        
        colnum = dict( ( ( k, x ) for (k, e, c), x in zip(kcs, colnum) ) )
        
        prs = set( p for k, p, a in tbv )
        prs = set( p[:i+1] for p in prs for i in range(len(p)) )
        
        rows = list(prs)
        rows.sort()
        
        rowcheck = [ ( c, 0 if ( n[:len(c)] == c and sum( n[len(c):] ) == 0 ) else 1 )
                     for c, n in zip( rows, rows[1:]+[[]] ) ]
        
        rownum = reduce( lambda x, y : x + [x[-1]+y[1]], rowcheck, [rowmax] )
        rowmax = rownum[-1]
        rownum = dict( zip( rows , rownum ) )
        
        #print rownum
        #print colnum
        #print
        
        rowspans = dict( ( r,  self._fast_get_childrows( i, rowcheck, r ) )
                         for i, r in enumerate( rows ) )
        
        colspans = dict( ( k, c ) for k, e, c in kcs )
        
        #print t
        
        t += [ ( colnum[k], rownum[pth], colspans[k], rowspans[pth], v ) 
               for k, pth, v in tbv ]
        
        print rowmax, colsum
        
        blanks = [ set( x+i for x, y, l, h, v in t if _y >= y and _y < y+h
                            for i in range(l) ) 
                   for _y in range(rowmax) ]
                       
        blanks = [ ( x, y, 1, 1, Node() ) 
                   for y, row in enumerate(blanks) 
                   for x in range(colsum) if x not in row ]
        
        print blanks
        
        t += blanks
        
        tbl = Table( contains = t )
        r = tbl._console_print_()
        
        for l in r :
            print l
        
        return
        
        
if __name__ == '__main__' :
    
    #a = ColorString('ABCDEFGHIJKLMNOPQRSTUVWSYZ')
    #a.fgcolor( 200, e=10 )
    #a.bgcolor( 150, s=5, e=15 )
    #print a
    
    print ColorString.sum([ ColorString( str(b).ljust(4), bg = b ) for b in range(16) ])
    
    for x in range(6):
        print ColorString.sum([ ColorString( str(x*36+b+16).ljust(4), bg = x*36+b+16, fg = ~(x*36+b)%216 + 16 ) for b in range(36) ])

    print ColorString.sum([ ColorString( str(b).ljust(4), bg = b ) for b in range(232,256) ])
    
    #print ColorString('|',bg=237).join(['A','B','C'])
    #print ColorString('hello',bg=90)+' world '+ColorString('!',fg=90)


    #print u'\u2714'
    #print u'\u28ff'
    #print u'\u2423\u2420\u2422'
    #print u'\u204B'
    
    #print 
    #print
    print
    print
    
    d = [ { 'colA' : 'A.1.alpha\r\nA.1.beta' ,
            'colB' : [1,2],
            'colC' : 'B.1.alpha\r\nB.1.beta\r\nB.1.gamma\r\nB.1.delta',
          },
          { 'colA' : 'A.2.alpha\r\nA.2.beta' ,
            'colB' : [0.1,0.9,0.3,0,-1],
            'colC' : ['3',{'B.2.alpha':'z','B.1':'qew' }],
          },
        ]
    
    ep = EasyPrinter()
    ep._parse( d, covert = { ('colB',) : (lambda x : [ Bar(_x,str(_x)) for _x in x ]) } )
