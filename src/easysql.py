
import types
import threading
import random

import MySQLdb


class EasySqlException( Exception ):
    """
    Default WorkFlow Exception
    """
    pass

class DuplicateError(EasySqlException):
    pass

class PrimaryKeyError(EasySqlException):
    pass

class NotFoundError(EasySqlException):
    pass

class TypeError(EasySqlException, TypeError ):
    pass


def sqlstr( v ):
    
    if hasattr(v, '_tosql'):
        return v._tosql()
    
    if v in types.StringTypes :
        return '"'+MySQLdb.escape_string(v)+'"'
    else :
        return "'"+MySQLdb.escape_string(str(v))+"'"






class Raw( object ):
    
    def __init__( self, _raw ):
        self._raw = _raw
    
    def _tosql(self):
        return self._raw

raw = Raw


class Default( Raw ):
    
    def __init__( self ):
        pass
        
    @staticmethod
    def _tosql():
        return 'DEFAULT'
    
default = Default
    
    
    
class Null( Raw ):
    
    def __init__( self ):
        pass
        
    @staticmethod
    def _tosql():
        return 'NULL'
    
null = Null



class Condition( Raw ):
    pass

class Expression( Raw ):
        
    def __add__ ( self, another ):
        
        self._raw = '(' + self._raw + '+' + sqlstr(another)+ ')'
        return self
    
    def __sub__( self, another ):
        
        self._raw = '(' + self._raw + '-' + sqlstr(another)+ ')'
        return self
    
    def __mul__( self, another ) :
        
        self._raw = '(' + self._raw + '*' + sqlstr(another)+ ')'
        return self
    
    def __div__( self, another ) :
        
        self._raw = '(' + self._raw + '/' + sqlstr(another)+ ')'
        return self
    
    
class This( Raw ):
    
    def __init__( self, colname ):
        super( This, self ).__init__('`'+colname+'`')
        
    def __add__ ( self, another ):
        
        return Expression( '(' + self._raw + '+' + sqlstr(another)+ ')' )
    
    def __sub__( self, another ):
        
        return Expression( '(' + self._raw + '-' + sqlstr(another)+ ')' )
    
    def __mul__( self, another ) :
        
        return Expression( '(' + self._raw + '*' + sqlstr(another)+ ')' )
    
    def __div__( self, another ) :
        
        return Expression( '(' + self._raw + '/' + sqlstr(another)+ ')' )
    
    def __eq__( self, another ):
        
        if another in ( Null, Default ) or type(another) in ( Null, Default ):
            return Condition( self._raw + ' IS ' + sqlstr(another) )
        
        return Condition( self._raw + '=' + sqlstr(another) )
        
    def __ne__( self, another ):
        
        if another in ( Null, Default ) or type(another) in ( Null, Default ):
            return Condition( self._raw + ' IS NOT ' + sqlstr(another) )
        
        return Condition( self._raw + '!=' + sqlstr(another) )
    
    def __gt__( self, another ):
        
        return Condition( self._raw + '>' + sqlstr(another) )
    
    def __ge__( self, another ):
        
        return Condition( self._raw + '>=' + sqlstr(another) )
    
    def __lt__( self, another ):
        
        return Condition( self._raw + '<' + sqlstr(another) )
    
    def __le__( self, another ):
        
        return Condition( self._raw + '<=' + sqlstr(another) )
        
    def startswith( self, another ):
        
        if type(another) == types.StringType :
            raise TypeError, 'this.startswith argment must be string'
        
        _raw =   self._raw + '>=' + sqlstr(another) \
               + ' AND ' \
               + self._raw + '<=' + sqlstr(another[:-1]+chr(ord(another[-1])+1))
        
        return Condition(_raw)
        
    def endswith( self, another ):
        
        if type(another) == types.StringType :
            raise TypeError, 'this.startswith argment must be string'
        
        _raw = self._raw + " LIKE '%" + another + "'"
        
        return Condition(_raw)
    
    def hassub( self, another ):
        
        if type(another) == types.StringType :
            raise TypeError, 'this.startswith argment must be string'
        
        _raw = self._raw + " LIKE '%" + another + "%'"
        
        return Condition(_raw)
    
this = This

SQLThisType = This
SQLCondType = Condition
SQLExprType = Expression




class SQLFunction( object ):
    
    def __init__ ( self, fname ):
        
        self.fname = fname
        
    def __call__ ( self, *args ):
        
        args = ','.join( [ sqlstr(a) for a in args ] )
        
        raw = self.fname+'('+args+')'
        
        return Expression(r)

func = SQLFunction









class NoArg( object ):
    pass
    


ArrayTypes = ( types.ListType, types.TupleType )
StrTypes = ( types.StringType, types.UnicodeType )


'''
CR = MySQLdb.constants.CR
CR = dict( [ ( getattr(CR, e), e )
             for e in vars(CR)
             if not e.startswith('__')
           ]
         )
'''

class MultiDimDict():
    
    def __init__( self ):
        
        self.d = {}
    
    def __setitem__( self, keys, value ):
        
        x = self.d
        
        for k in keys[:-1] :
            
            if k not in x :
                x[k] = {}
            
            x = x[k]
            
        x[keys[-1]] = value
        
        return self
    
    def __getitem__( self, keys ):
        
        x = self.d
        
        for k in keys :
            if k not in x :
                raise KeyError, ( 'not found key', key )
            
            x = x[k]
        
        return x
    
    def __contains__ ( self, keys ):
        
        x = self.d
        
        for k in keys :
            if k not in x :
                return False
            x = x[k]
            
        return True
    
    def getdefault( self, keys, default=None ):
        
        x = self.d
        
        for k in keys :
            if k not in x :
                return default
            
            x = x[k]
        
        return x
    
    get = getdefault


class SQLConnectionPool( object ):
    '''
    Connection Pool
    '''
    
    def __init__( self, ):
        
        self.conns = MultiDimDict()
        
        self._longlink = False
        
        return
    
    def _read( self, conn, sql ):
        
        conn.query(sql)
        
        rst = conn.store_result()
        
        rst = rst.fetch_row(rst.num_rows())
        
        return rst
    
    def _write( self, conn, sql ):
        '''
        using Mysql_info() to get the match number affact number
        using Mysql_insert_id() to get lastid
        
        
        info (eg) :
        { 'Records': 2, 'Duplicates': 1, 'Warnings': 0 }
        { 'Rows matched': 1, 'Changed': 0, 'Warnings': 0 }
        '''
        conn.query(sql)
        
        affect = conn.affected_rows()
        
        lastid = conn.insert_id()
        lastid = lastid if lastid != False else None
        
        info = conn.info()
        if info != None :
            info = [ w.split(':') for w in info.split('  ') if w != '' ]
            info = [ ( k.strip(' '), int(v.strip(' ')) ) for k, v in info ]
            info = dict(info)
        
        conn.commit()
        
        print 'ali>', affect, lastid, info
        
        return affect, lastid, info
    
    def read( self, conn_args, sql ):
        
        print 'sql>', sql
        
        conn = self._get( conn_args )
        rconn = None
        
        try :
            r = self._read( conn, sql )
            rconn = conn
        finally :
            self._put( conn_args, rconn )
        
        return r
    
    def write( self, conn_args, sql ):
        
        print 'sql>', sql
        
        conn = self._get( conn_args )
        rconn = None
        
        try :
            r = self._write( conn, sql )
            rconn = conn
        finally :
            self._put( conn_args, rconn )
            
        return r
    
    def _get( self, conn_args ):
        
        x = self.conns.get( conn_args, None )
        
        if x == None :
            
            conn = \
            MySQLdb.Connection(
                host=conn_args[0], port=conn_args[1], db=conn_args[4],
                user=conn_args[2], passwd=conn_args[3]
            )
        
        return conn
    
    def _put( self, conn_args, conn ):
        
        if self._longlink == True :
            self.conns[conn_args] = conn
        else :
            self.conns[conn_args] = None
            
        return
    

class Tablet( object ) :
    '''
    tablet of table
    '''
    
    def __init__ ( self, name, conn_args, cols=[] ):
        
        self.conn_args = conn_args
        
        self.name = name
        
        self.cols = cols
        self.defaultcols = [ c for c in cols if not c.startswith('_') ]
        
        
    def _buildrow( self, row ):
        
        return dict( [ ( k, sqlstr(v) ) for k, v in row.items() 
                                        if k in self.cols ] )
        
    def _insert( self, connpool, rows, dup=None ):
        '''
        return ( affect rows number , lastid )
        '''
        
        rows = [ self._buildrow(row) for row in rows ]
        dup = self._buildrow(dup) if dup else None
        
        sql = self._insert_sql( rows, dup )
        
        affectrows, lastid, info = connpool.write( self.conn_args, sql )
        
        return affectrows, lastid
        
    def _insert_sql( self, rows, dup = None, ignore = True ):
        '''
        INSERT [LOW_PRIORITY | DELAYED | HIGH_PRIORITY] [IGNORE]
            [INTO] tbl_name [(col_name,...)]
            {VALUES | VALUE} ({expr | DEFAULT},...),(...),...
            [ ON DUPLICATE KEY UPDATE
              col_name=expr
                [, col_name=expr] ... ]
        '''
        
        cols = set( sum( [ r.keys() for r in rows ] , [] ) )
        
        rows = [ [ r.get( c, 'DEFAULT' ) for c in cols ]
                 for r in rows ]
        
        sql = ' '.join( [
            
            'INSERT',
            # LOW_PRIORITY or DELAYED or ''
            'IGNORE' if ignore else '',
            'INTO',
            '`'+self.name+'`',
            '(%s)' % ( ','.join( [ '`%s`' % (c,) for c in cols ] ) ),
            'VALUES',
            ','.join( [ '(%s)' % ( ','.join(r), ) for r in rows ] ),
            ('ON DUPLICATE KEY UPDATE %s' %
                ( ','.join( [ '`%s`=%s' % i for i in dup.items() ] ), )
            ) if dup else '',
        ] )
        
        return sql
    
    def _select( self, connpool,
                 cond=None, condx=[], cols=None, limit=None, offset=None,
                 order=None ):
        '''
        return ( result rows, result )
        '''
        
        cond = self._buildrow(cond) if cond else None
        
        sql = self._select_sql( cond, condx, cols, limit, offset, order )
        
        rst = connpool.read( self.conn_args , sql )
        
        cols = cols or self.defaultcols
        
        rst = [ dict(zip(cols,row)) for row in rst ]
        
        return len(rst), rst
    
    def _select_sql( self,
                     cond=None, condx=[], cols=None,
                     limit=None, offset=None,
                     order=None, vset=None ):
        '''
        SELECT
            [ALL | DISTINCT | DISTINCTROW ]
              [HIGH_PRIORITY]
              [STRAIGHT_JOIN]
              [SQL_SMALL_RESULT] [SQL_BIG_RESULT] [SQL_BUFFER_RESULT]
              [SQL_CACHE | SQL_NO_CACHE] [SQL_CALC_FOUND_ROWS]
            select_expr [, select_expr ...]
            [FROM table_references
            [WHERE where_condition]
            [GROUP BY {col_name | expr | position}
              [ASC | DESC], ... [WITH ROLLUP]]
            [HAVING where_condition]
            [ORDER BY {col_name | expr | position}
              [ASC | DESC], ...]
            [LIMIT {[offset,] row_count | row_count OFFSET offset}]
            [PROCEDURE procedure_name(argument_list)]
            [INTO OUTFILE 'file_name'
                [CHARACTER SET charset_name]
                export_options
              | INTO DUMPFILE 'file_name'
              | INTO var_name [, var_name]]
            [FOR UPDATE | LOCK IN SHARE MODE]]
        '''
        
        cols = cols or self.defaultcols
        
        sql = ' '.join( [
            
            'SELECT',
            'DISTINCT' if vset else '',
            ','.join([ '`%s`' % (c,) for c in cols ]),
            'FROM `%s`' % self.name ,
            'WHERE' if cond or condx!=[] else '',
                ','.join( [ '`%s`=%s' % i for i in cond.items() ] ) \
                                                                if cond else '',
                ',' if cond and condx !=[] else '',
                ','.join( [ i._tosql() for i in condx ] ),
            'ORDER BY' if order else '',
                ','.join( [ '`%s` DESC' % o[1:] if o.startswith('~') else \
                            ( '`%s`' % o )
                            for o in order ] ) if order else '',
            ('LIMIT %d' % (limit,) ) if limit else '',
            ('OFFSET %d' % (offset,) ) if limit and offset else '',
            
        ] )
        
        return sql
        
    def _delete( self, connpool, cond=None, condx=[], limit=None ):
        '''
        return ( affect rows, None )
        '''
        cond = self._buildrow(cond) if cond else None
        
        sql = self._delete_sql( cond, condx, limit )
        
        affectrows, lastid, info = connpool.write( self.conn_args, sql )
        
        return affectrows, None
        
    def _delete_sql( self, cond=None, condx=[], limit=None, ignore = True ):
        '''
        DELETE [LOW_PRIORITY] [QUICK] [IGNORE] FROM tbl_name
            [WHERE where_condition]
            [ORDER BY ...]
            [LIMIT row_count]
        '''
        
        sql = ' '.join( [
            
            'DELETE',
            'IGNORE' if ignore else '',
            'FROM `%s`' % self.name ,
            'WHERE' if cond or condx!=[] else '',
                ','.join( [ '`%s`=%s' % i for i in cond.items() ] ) \
                                                                if cond else '',
                ',' if cond and condx !=[] else '',
                ','.join( [ i._tosql() for i in condx ] ),
            ('LIMIT %d' % (limit,) ) if limit else '',
            
        ] )
        
        return sql
        
    def _replace( self, connpool, rows ):
        '''
        return ( affect rows, lastid )
        '''
        
        rows = [ self._buildrow(row) for row in rows ]
        
        sql = self._replace_sql( rows )
        
        affectrows, lastid, info = connpool.write( self.conn_args, sql )
        
        return affectrows, lastid
        
    def _replace_sql( self, rows ):
        '''
        REPLACE [LOW_PRIORITY | DELAYED]
            [INTO] tbl_name [(col_name,...)]
            {VALUES | VALUE} ({expr | DEFAULT},...),(...),...
        '''
        
        cols = set( sum( [ r.keys() for r in rows ] , [] ) )
        
        rows = [ [ r.get( c, 'DEFAULT' ) for c in cols ]
                 for r in rows ]
        
        sql = ' '.join( [
            
            'REPLACE',
            # LOW_PRIORITY or DELAYED or ''
            'INTO',
            '`'+self.name+'`',
            '(%s)' % ( ','.join( [ '`%s`' % (c,) for c in cols ] ) ),
            'VALUES',
            ','.join( [ '(%s)' % ( ','.join(r), ) for r in rows ] ),
            
        ] )
        
        return sql
        
    def _update( self, connpool, row, cond=None, condx=[], limit=None):
        '''
        return ( matched rows, affectrows )
        '''
        
        row = self._buildrow(row)
        cond = self._buildrow(cond) if cond else None
        
        sql = self._update_sql( row, cond, condx, limit )
        
        affectrows, lastid, info = connpool.write( self.conn_args, sql )
        
        return info['Rows matched'], affectrows
        
        
    def _update_sql( self, row, cond=None, condx=[],
                           limit=None, ignore = True  ):
        '''
        UPDATE [LOW_PRIORITY] [IGNORE] table_reference
            SET col_name1={expr1|DEFAULT} [, col_name2={expr2|DEFAULT}] ...
            [WHERE where_condition]
            [ORDER BY ...]
            [LIMIT row_count]
        '''
        
        sql = ' '.join( [
            
            'UPDATE',
            'IGNORE' if ignore else '',
            '`%s`' % self.name ,
            'SET',
                ','.join( [ '`%s`=%s' % i for i in row.items() ] ),
            'WHERE' if cond or condx!=[] else '',
                ','.join( [ '`%s`=%s' % i for i in cond.items() ] ) \
                                                                if cond else '',
                ',' if cond and condx !=[] else '',
                ','.join( [ i._tosql for i in condx ] ),
            ('LIMIT %d' % (limit,) ) if limit else '',
            
        ] )
        
        return sql
    
    



class ListWithHashKey(list):
    
    def __init__( self, l, hashseed ):
        
        self.hashkey = hash(hashseed)
        
        super( ListWithHashKey, self ).__init__(l)
        
        return
    
    def __hash__( self ):
        
        return self.hashkey



class Table ( object ) :
    '''
    table class of easysql
    '''
    
    @staticmethod
    def getresult( conn ):
        
        rst = conn.store_result()
        
        return rst.fetch_row( rst.num_rows() )
        
    
    @staticmethod
    def _sliceparser( slc ):
        '''
        table[ col, ..., cond,... , offset:limit:order ]
        '''
        
        print slc
        
        if type( slc ) not in ArrayTypes :
            slc = [slc,]
        
        if type(slc[-1]) == types.SliceType :
            single = False
            offset = slc[-1].start
            limit = slc[-1].stop
            order = slc[-1].step
            order = order if order in ArrayTypes or order==None else [order,]
            slc = slc[:-1]
        else :
            single = True
            offset = None
            limit = None
            order = None
        
        slc = [ s if type(s) in ArrayTypes else [s,] for s in slc ]
        slc = sum( slc, [] )
        
        cols  = [ s for s in slc if type(s) in types.StringTypes ]
        cond  = [ s for s in slc if type(s) == types.DictType ]
        condx = [ s for s in slc if type(s) == SQLCondType ]
        
        print single, cols, cond, condx, offset, limit, order
        return single, cols, cond, condx, offset, limit, order
    
    @staticmethod
    def _slice( slc, single ):
        
        single.append( ( slc.start, slc.stop ) )
        
        if slc.step == None :
            return []
        elif slc.step in ArrayTypes :
            return slc.step
        
        return [slc.step]
    
    def __init__ ( self, tablets = [], name=None ):
        
        self.name = name
        
        self.colconv = []
        self.colset = set([])
        
        self.connpool = SQLConnectionPool()
        self.tablets = tablets
        
        return
        
    def _splitter( self, row ):
        
        return [ListWithHashKey(self.tablets, ''),]
    
    def _gettablets( self, tbl ):
        
        return random.choice(tbl)
        
    def _conv( self, row, k_in, k_out, conv ):
        
        if any([ k not in row for k in k_in ]):
            return []
        
        return zip( k_out, conv( *[ row[k] for k in k_in ] ) )
        
    def _encoderow( self, row ):
        
        newcols = [     self._conv( row, cc[0], cc[1], cc[2] )
                    for cc in self.colconv ]
        
        return dict(row.items()+sum(newcols,[]))
        
    def _decoderow( self, row ):
        
        newcols = [     self._conv( row, cc[1], cc[0], cc[3] )
                    for cc in self.colconv ]
        
        return dict( [ (k, v) for k, v in row.items()
                              if k not in self.colset ]\
                     + sum( newcols, [] ) )
        
    def setsplitter( self, splitter ):
        
        return
        
    def setconverter( self, encoder, decoder=None,
                            encoder_key=None, decoder_key=None ):
        
        if decoder == None :
            decoder = lambda x : x
        
        if decoder_key == None :
            decoder_key = encoder_key
        
        self.colconv += [( encoder_key, decoder_key, encoder, decoder),]
        
        self.colset = self.colset & set( decoder_key )
        
        return
        
    def _write( self, rows, ondup = None ):
        
        rows = [ self._encoderow(row) for row in rows ]
        
        tbls = [ self._splitter(row) for row in rows ]
        tblc = [ r for r, t in zip(rows, tbls) if len(t) != 1 ]
        if tblc != [] :
            raise PrimaryKeyError, \
                           ( 'Can not find the tablet on write', tblc )
        tbls = [ t[0] for t in tbls ]
        
        tblrows = [ ( tbl, [ r for r, t in zip(rows,tbls) if t == tbl ] )
                    for tbl in set(tbls) ]
        
        rsts = [ self._gettablets(tbl)._insert( self.connpool, rows, ondup )
                 for tbl, rows in tblrows ]
        
        n, lastids = zip(*rsts)
        n = sum(n)
        
        return n, lastids
    
    def _replace( self, rows ):
        
        rows = [ self._encoderow(row) for row in rows ]
        tbls = [ self._splitter(row) for row in rows ]
        tblc = [ r for r, t in zip(rows, tbls) if len(t) != 1 ]
        if tblc != [] :
            raise PrimaryKeyError, \
                           ( 'Can not find the tablet on replace', tblc )
        tbls = [ t[0] for t in tbls ]
        
        tblrows = [ ( tbl, [ r for r, t in zip(rows,tbls) if t == tbl ] )
                    for tbl in set(tbls) ]
        
        rsts = [ self._gettablets(tbl)._replace( self.connpool, rows )
                 for tbl, rows in tblrows ]
        
        n, lastids = zip(*rsts)
        n = sum(n)
        
        return n, lastids

    
    def _read( self, cond, condx=[],
                     cols=None, limit=None, offset=None, order=None ):
        
        print 'order>',order
        
        cond = self._encoderow(cond) if cond else cond
        tbls = self._splitter(cond) # todo : set to all tablets if cond is none
        
        tlimit = limit
        rst = []
        nx = 0
        for tbl in tbls : # read lazy
            n, r = self._gettablets(tbl)._select( self.connpool,
                                                  cond, condx, cols, tlimit,
                                                  None, order
                                                )
            nx += n
            rst = rst + r
            tlimit = ( tlimit - n ) if tlimit != None else tlimit
            if tlimit <= 0 :
                break
        
        
        rst = [ self._decoderow(r) for r in rst ]
        
        return nx, rst
        
    def _set( self, row, cond, condx=[], limit = None ):
        
        cond = self._encoderow(cond) if cond else cond
        tbls = self._splitter(cond) # todo : set to all tablets if cond is none
        
        row = self._buildrow(row)
        
        tlimit = limit
        nx = 0
        for tbl in tbls :
            n, r = self._gettablets(tbl)._update( self.connpool,
                                                  row, cond, condx, tlimit )
            nx += n
            tlimit = ( tlimit - n ) if tlimit != None else tlimit
            if tlimit <= 0 :
                break
        
        return nx, None
    
    def _delete( self, cond, condx=[], limit = None ):
        
        cond = self._encoderow(cond) if cond else cond
        tbls = self._splitter(cond) # todo : set to all tablets if cond is none
        
        tlimit = limit
        nx = 0
        for tbl in tbls : # read lazy
            n, r = self._gettablets(tbl)._delete( self.connpool,
                                                  cond, condx, tlimit )
            nx += n
            tlimit = ( tlimit - n ) if tlimit != None else tlimit
            if tlimit <= 0 :
                break
        
        return nx, None
        
    def __lshift__ ( self, rows ):
        '''
        table << {'attr':'inserted'}
        table << [{'attr':'inserted'},]
        '''
        
        if type(rows) == types.DictType :
            rows = [rows,]
            single = True
        elif type(rows) in ( types.ListType, types.TupleType ) :
            single = False
        else :
            raise TypeError, 'easysql.__lshift__ indices must row|[row,...]'
        
        n, lastid = self._write( rows )
        
        if single == True and n == 0:
            raise DuplicateError, ''
        
        return self
    
    def __iadd__ ( self, rows ):
        '''
        table += [{'attr':'inserted'},]
        '''
        
        if type(rows) in ( types.ListType, types.TupleType ) :
            single = False
        else :
            raise TypeError, 'easysql.__iadd__ argment must row|[row,...]'
        
        n, lastid = self._write( rows )
        
        if n != len(rows):
            raise DuplicateError, ''
        
        return self
    
    def append( self, row, ondup=None ):
        '''
        lastid = table.append( {'attr':'inserted'} )
        
        lastid = table.append( {'attr':'inserted'},
                                     ondup = {'attr':'updated'} )
                                     
        return None or lastid
        '''
        
        n, lastid = self._write( [row,], ondup )
        
        if n == 1 :
            return None
        else :
            return lastid[0]
            
    def extend( self, rows ):
        '''
        lastid = table.expend( [{'attr':'inserted'},] )
        
        return successed number
        '''
        
        n, lastid = self._write( rows )
        
        return n
        
    def get( self, cond, default=NoArg, keys=[] ):
        '''
        table.get({'ID':1}, default=None, keys=[] )
        '''
        
        n, rst = self._read( cond, [], cols=keys, limit=1)
        
        if n != 1 and default != NoArg :
            return default
        
        if n != 1 :
            raise NotFoundError, 'not found'
        
        return rst[0]
    
    def __rshift__ ( self, cond ):
        '''
        a = {'ID':1} ; table >> a
        '''
        
        n, rst = self._read( cond, limit = 1 )
        
        if n != 1 :
            raise NotFoundError, 'not found'
        
        cond.update(rst[0])
        
        return rst[0]
        
    def gets( self, cond, keys=[], limit=None, offset=None):
        '''
        table.gets( {'a':1}, keys=[], limit=n, offset = p )
        '''
        
        n, rst = self._read( cond, [], cols=keys, limit=limit, offset=offset )
        
        return rst

    def __getitem__( self, slc ):
        '''
        table[{'ID':1}]
        '''
        
        single, keys, cond, condx, offset, limit, order = \
                                                       self._sliceparser( slc )
        
        n, rst = self._read( cond, condx, keys, limit, offset, order )
        
        if single == False :
            return rst
            
        if n != 1 :
            raise NotFoundError, 'not found'
        
        return rst[0]
        
    def set( self, cond, row ):
        '''
        table.set( {'ID':1}, {'attr':'updated'} )
        '''
        
        if row == {} :
            raise TypeError, \
                      ( 'value must at least one to set', value, condk )
        
        n, x = self._set( row, cond, [], 1 )
        
        if n == 0 :
            raise NotFoundError, 'no found'
        
        return
    
    def sets( self, cond, row, limit ):
        '''
        table.sets( {'ID':1}, {'attr':'updated'}, limit=n )
        '''
        
        if row == {} :
            raise TypeError, \
                      ( 'value must at least one to set', value, condk )
        
        n, x = self._set( row, cond, [], limit )
        
        return n
        
    def __setitem__( self, slc, value ):
        '''
        table[{'ID':1}] = {'A':1}
        '''
        
        single, keys, cond, condx, offset, limit, order = \
                                                       self._sliceparser( slc )
        
        cond = dict(   ( cond.items() if cond else [] ) \
                     + [ ( k, value[k] ) for k in keys ] )
        
        row = dict([ (k, v) for k, v in value.items() if k not in keys ])
        
        if row == {} :
            raise TypeError, \
                      ( 'value must at least one to set', value, condk )
            
        n, x = self._set( row, cond, condx, limit )
        
        if single == True and n == 0 :
            raise NotFoundError, 'not found'
        
        return
    
    def __ilshift__( self, rows ):
        '''
        table <<= {'attr':'inserted'}
        table <<= [{'attr':'inserted'},]
        '''
        
        if type(rows) == types.DictType :
            rows = [rows,]
            single = True
        elif type(rows) in ( types.ListType, types.TupleType ) :
            single = False
        else :
            raise TypeError, 'easysql << must row|[row,...]'
        
        n, x = self._replace( rows )
        
        return self
        
    def load( self, row ):
        '''
        table.load( {'attr':'replaced'} )
        '''
        
        n, x = self._replace( [row, ] )
        
        if n == 0 :
            raise EasySqlException, 'row error in load.'
        
        return x[0]
        
    def loads( self, rows ):
        '''
        table.loads( [{'attr':'replaced'},] )
        '''
        
        n, x = self._replace( rows )
        
        return n
    
    def remove( self, cond ):
        
        n, x = self._delete( cond, [], 1 )
        
        if n == 0 :
            raise NotFoundError, 'not found'
        
        return
    
    def removes( self, cond, limit=None ):
        
        n, x = self._delete( cond, [], limit )
        
        return n
    
    def __delitem__( self, slc ):
        '''
        del table[{'attr1':1}]
        del table[{'attr1':1},::]
        '''
        
        single, cols, cond, condx, offset, limit, order = \
                                                       self._sliceparser( slc )
        
        n, x = self._delete( cond, condx, limit )
        
        if single == True and n == 0 :
            raise NotFoundError, 'not found'
        
        return
    
    def __contains__( self, name ):
        '''
        {} in table
        '''
        
        return
    
    def __invert__( self, obj ):
        '''
        (~table)[...]
        SQL(table)[...]
        table.sql[]
        '''
        
        return
    
    def __add__( self, other ):
        
        return Table( self.tablets + other.tablets, self.name )
        
    def __len__( self ):
        
        return len(tablets)
        
    @staticmethod
    def sum( table ):
        
        return Table( sum([ t.tablets for t in table ],[]), self.name )



class DataBase ( object ):
    
    def __init__( self, tables ):
        
        self.tables = dict( [ ( t.name, t ) for t in tables ] )
        
    def __getattr__( self, key ):
        
        return self.tables[key]
        
    @staticmethod
    def bytablename( tbls ):
        
        tbls = [    sum( [ t for t in tbls if t.name == tn ],
                           Table([], tn) )
                 for tn in set([ t.name for t in tbls ]) ]
        
        return DataBase(tbls)
        
    def keys( self ):
        
        return self.tables.keys()


def maketables( host, port, user, passwd, db, tablename=None ):
    '''
    SHOW TALBES
    DESCRIBE
    SHOW GRANTS
    '''
    
    p = SQLConnectionPool()
    
    conn_args = ( host, port, user, passwd, db )
    
    tblnames = p.read( conn_args,
                       "SHOW FULL TABLES FROM `%s` "
                                "WHERE table_type = 'BASE TABLE'" % (db,) )
    
    tblnames = [ t[0] for t in tblnames
                 if tablename==None or t[0]==tablename ]
    
    tblcols = [     p.read( conn_args, "DESCRIBE `%s`.`%s`" % (db,n) )
                for n in tblnames ]
    
    tblcols = [ [ col[0] for col in cols ] for cols in tblcols ]
    
    tablets = [     Tablet( n, conn_args, cols )
                for n, cols in zip(tblnames, tblcols) ]
    
    return [ Table( [t,], t.name ) for t in tablets ]




if __name__ == '__main__' :
    
    #t = Table([Tablet('testtable'),])
    #
    #
    #print '-- insert --'
    #
    #t << {'a':1,'b':2} << {'c':1,'d':2}
    #print t.append( {'a':1,'b':2} )
    #
    #t << [{'a':1,'b':2},{'c':1,'d':2}]
    #t += [{'a':1,'b':2},]
    #print t.extend([{'a':1,'b':2},{'c':1,'d':2}])
    #
    #t.append( {'a':1}, ondup = {'b':2} )
    #
    #print '-- select --'
    #
    #print t[{'a':1}]
    #print t['a','b']
    #print t.get( {'a':1} )
    #
    #x = {'a':1}
    #t >> x
    #print 'x', x
    #
    #print t[::{'a':1}]
    #print t['a','b',:50:]
    #print t.gets( {'a':1}, limit=3, offset=8 )
    #
    #print '-- update --'
    #
    #t[{'a':1}] = {'b':this('c')+1}
    #t['a'] = {'a':1,'b':this('c')+2}
    #t.set( {'a':1}, {'b':default()} )
    #
    #t[::{'attr1':1}] = {'b':2}
    #t['a',::] = {'a':1,'b':this('c')+2}
    #t.sets( {'a':1}, {'b':2}, limit=5 )
    #
    #print '-- replace --'
    #
    #t <<= {'a':1}
    #print t.load( {'a':1} )
    #t <<= [{'a':1},]
    #print t.loads( [{'a':1},] )
    #
    #
    #print '-- delete --'
    #
    #del t[{'a':1}]
    #t.remove({'a':1})
    #del t[::{'a':1}]
    #t.removes({'a':1})
    
    t = maketables( '127.0.0.1', 3306, 'S3ADMIN', 'vll9ver5t@l1',
                    'HybridS3Admin', 'AdminUser' )[0]
    
    a =  { 'Account':'admin9',
           'md5Password':'0',
           'AccessKey':'022QF06E7MXBSH9DHM06',
           'SecretAccessKey':'kWcrlUX5JEDGM/LtmEENI/aVmYvHNif5zB+d9+ct',
           'Email':'x@x',
         }
    
    b =  { 'Account':'admin45',
           'md5Password':'0',
           'AccessKey':'022QF06E7MXBSH9DHM78',
           'SecretAccessKey':'kWcrlUX5JEDGM/LtmEENI/aVmYvHNif5zB+d9+ct',
           'Email':'x@x',
         }
    
    print t.append( a, ondup={'Email':'z@x'} )
    print t.extend( [a, b] )
    
    print t[{'Account':'admin'}]
    
    
