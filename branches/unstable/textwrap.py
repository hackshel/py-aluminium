# -*- coding: utf-8 -*-

import sys

__all__ = ['TextWrapper', 'wrap', 'fill', 'dedent']

class TextWrapper(object):
    
    x = ['Word','Compound','Blank','Empty']
    y = ['space','initials','tails','letter','terminal']
    
    statmachine = [
        # Word                     Compound               Blank                     Empty
        [(None ,'SP','Blank'   ),  (None ,'SP',None   ),  (None ,'SP',None      ),  (None ,'SP','Blank'   ),], # Space
        [(None ,'W' ,'Compound'),  (None ,'W' ,None   ),  ('End','W' ,'Compound'),  ('End','W' ,'Compound'),], # Initials
        [(None ,'W' ,None      ),  (None ,'W' ,'Word' ),  (None ,'W' ,'Word'    ),  (None ,'W' ,'Word'    ),], # tails
        [(None ,'W' ,None      ),  (None ,'W' ,'Word' ),  ('End','W' ,'Word'    ),  ('End','W' ,'Word'    ),], # letters
        [('End','W' ,'Empty'   ),  (None ,'W' ,'Empty'),  ('End','W' ,'Empty'   ),  ('End','W' ,None      ),], # chinese
    ]
    
    initials = u'([{<$'\
               u'￥（【“‘《'
               
    tails = u'!%)]:;>?,.'\
            u'·！…）】、：；”’》，。？'
               
    letter = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'\
             'abcdefghijklmnopqrstuvwxyz'\
             '0123456789'\
             '~`@#^&*_-+=|\\"\'/'

    def __init__(self,
                 width=70,
                 initial_indent="",
                 subsequent_indent="",
                 expand_tabs=True,
                 replace_whitespace=True,
                 fix_sentence_endings=False,
                 break_long_words=True,
                 drop_whitespace=True,
                 break_on_hyphens=True):
        self.width = width
        self.initial_indent = initial_indent
        self.subsequent_indent = subsequent_indent
        self.expand_tabs = expand_tabs
        self.replace_whitespace = replace_whitespace
        self.fix_sentence_endings = fix_sentence_endings
        self.break_long_words = break_long_words
        self.drop_whitespace = drop_whitespace
        self.break_on_hyphens = break_on_hyphens

    @classmethod
    def chrtype( cls, c ):
        if c == ' ':
            return 0
        elif c in cls.initials :
            return 1
        elif c in cls.tails :
            return 2
        elif c in cls.letter :
            return 3
        else :
            return 4
    
    def _split_iter( self, inp ):
        
        s = self.x.index('Compound')
        start = 0
        cur = 0
        
        width = 0
        width_cur = 0
        
        for i, c in enumerate(inp) :
            
            ctype = self.chrtype(c)
            ending, acc, nxt = self.statmachine[ctype][s]
            
            if ending :
                yield start, cur+1, i, width_cur
                start = i
                width = 0
                width_cur = 0
                
            width += self.getchrwidth(c)
            
            if acc == 'W' :
                cur = i
                width_cur = width
                
            if nxt :
                s = self.x.index(nxt)
                
        yield start, cur+1, i, width_cur
        
        return
        
    @staticmethod
    def getchrwidth( c ):
        return 1 if ord(c) < 256 else 2
    
    @classmethod
    def _wrap_long_word( cls, word, width ):
        
        anticur = width
        start = 0
        
        for i, c in enumerate(word) :
            
            w = cls.getchrwidth(c)
            anticur -= w
            
            if anticur < 0 :
                yield start, i+1, None
                
                start = i
                anticur = width - w
            
        yield start, i+1, anticur
        
        return
    
    def wrap( self, text, width=70 ):
        
        r = []
        l = []
        
        for i in self._wrap_iter( text, width ):
            if i == None :
                r.append(''.join(l))
                l = []
        
        return r

    def fill( self, text, width=70 ):
        return '\n'.join( self.wrap( text, width ) )
        
    def show( self, text, width=70 ):
        
        for i in self._wrap_iter( text, width ):
            sys.stdout.write(i if i!= None else '\n')
        
        return
    
    def _wrap_iter( self, text, width=70 ):
        
        anticur = width
        
        for wst, bst, ed, ww in self._split_iter(text):
            
            if anticur < ww :
                
                yield None
                anticur = width
                    
                if ww > width :
                    
                    word = text[wst:bst]
                    
                    for subst, subed, subcur in self._wrap_long_word( word, width ):
                        
                        yield word[subst:subed]
                        if subcur == None:
                            yield None
                        anticur = subcur
                        
                else :
                    yield text[wst:bst]
                    anticur -= ww
            else :
                yield text[wst:bst]
                anticur -= ww
                
            blankwidth = ed-bst
            
            if anticur >= blankwidth :
                yield ' '*blankwidth
                
            anticur -= blankwidth
        
        return
  




import re
# the function in follows is copy from textwrap in standard lib 

def wrap(text, width=70, **kwargs):
    """Wrap a single paragraph of text, returning a list of wrapped lines.

    Reformat the single paragraph in 'text' so it fits in lines of no
    more than 'width' columns, and return a list of wrapped lines.  By
    default, tabs in 'text' are expanded with string.expandtabs(), and
    all other whitespace characters (including newline) are converted to
    space.  See TextWrapper class for available keyword args to customize
    wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    return w.wrap(text)

def fill(text, width=70, **kwargs):
    """Fill a single paragraph of text, returning a new string.

    Reformat the single paragraph in 'text' to fit in lines of no more
    than 'width' columns, and return a new string containing the entire
    wrapped paragraph.  As with wrap(), tabs are expanded and other
    whitespace characters converted to space.  See TextWrapper class for
    available keyword args to customize wrapping behaviour.
    """
    w = TextWrapper(width=width, **kwargs)
    return w.fill(text)


# -- Loosely related functionality -------------------------------------

_whitespace_only_re = re.compile('^[ \t]+$', re.MULTILINE)
_leading_whitespace_re = re.compile('(^[ \t]*)(?:[^ \t\n])', re.MULTILINE)

def dedent(text):
    """Remove any common leading whitespace from every line in `text`.

    This can be used to make triple-quoted strings line up with the left
    edge of the display, while still presenting them in the source code
    in indented form.

    Note that tabs and spaces are both treated as whitespace, but they
    are not equal: the lines "  hello" and "\thello" are
    considered to have no common leading whitespace.  (This behaviour is
    new in Python 2.5; older versions of this module incorrectly
    expanded tabs before searching for common leading whitespace.)
    """
    # Look for the longest leading string of spaces and tabs common to
    # all lines.
    margin = None
    text = _whitespace_only_re.sub('', text)
    indents = _leading_whitespace_re.findall(text)
    for indent in indents:
        if margin is None:
            margin = indent

        # Current line more deeply indented than previous winner:
        # no change (previous winner is still on top).
        elif indent.startswith(margin):
            pass

        # Current line consistent with and no deeper than previous winner:
        # it's the new winner.
        elif margin.startswith(indent):
            margin = indent

        # Current line and previous winner have no common whitespace:
        # there is no margin.
        else:
            margin = ""
            break

    # sanity check (testing/debugging only)
    if 0 and margin:
        for line in text.split("\n"):
            assert not line or line.startswith(margin), \
                   "line = %r, margin = %r" % (line, margin)

    if margin:
        text = re.sub(r'(?m)^' + margin, '', text)
    return text
        









if __name__ == '__main__' :
    
    tw = TextWrapper()
    
    w = 23
    
    print '-'*w
    
    tw.show( 'The quick brown fox jumps over the lazy dog', w )
    print 
    print 
    
    tw.show( 'The quick brown fox jumps over the lazy dog.', w )
    print 
    print 
    
    tw.show( 'The quick brown fox ( jumps ) over the lazy doooooooooooooooooooooooooog.', w )
    print 
    print 
    
    tw.show( 'A quick movement of the enemy will jeopardize six gunboats.', w )
    print
    print
    
    tw.show( '"Who am taking the ebonics quiz?", the prof jovially axed.', w )
    print
    print
    
    tw.show( 'The quick brown fox jumps over a lazy dog.', w)
    print
    print
    
    tw.show( '   Waaaaaaatch "Jeopardy!", Alex Trebek\'s fun TV quiz game.', w)
    print
    print
    
    tw.show( 'JoBlo\'s movie review of The Yards: Mark Wahlberg, Joaquin Phoenix, Charlize Theron...', w)
    print 
    print
    
    tw.show( u'I sang, and thought I sang very well; '\
             u'but he just looked up into my face with a very '\
             u'quizzical expression, and said, ‘How long have been singing, '\
             u'Mademoiselle?’', w)
    print 
    print
    
    print '-'*w
    
    print
    print
    
    for w in [23,26,29,32] :
    
        print '-'*w
        
        tw.show( u'包含有字母表中所有字母并且言之成义的句子称为全字母句（英语：pangram或holoalphabetic sentence，希腊语：pan gramma（意为“每一个字母”））。'\
                 u'全字母句被用于显示字体和测试打字机。英语中最知名的全字母句是“The quick brown fox jumps over the lazy dog（敏捷的棕色狐狸跳过懒狗身上）”。'\
                 u'一般，有趣的全字母句都很短；写出一个包含有最少重复字母的全字母句是一件富有挑战性的工作。长的全字母句在正确的前提下，显著地富有启迪性，或是很幽默，或是很古怪。'\
                 u'从某种意义上，全字母句是漏字文（英语：Lipogram）的对立物，因为后者在文章中有意不使用一个或几个特定字母。', w )
        print 
        print
        
        print '-'*w
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    