#!/usr/bin/env python
# coding: iso-8859-1

# --------------------------------------------- class : graphColor --
# -------------------------------------------------------------------

class graphColor :
    COLORS = {
        'black'  : (0x00,0x00,0x00),
        'white'  : (0xff,0xff,0xff),
        'red'    : (0xff,0x00,0x00),
        'green'  : (0x00,0xff,0x00),
        'blue'   : (0x00,0x00,0xff),
        'yellow' : (0xff,0xff,0x88),
        'brown'  : (0x88,0x44,0x22),
        'lightyellow' : (0xff,0xff,0xcc),
        'lightblue' : (0xcc,0xcc,0xff),
        'uglybrown'   : (0xff,0xcc,0x66),
        }
    def __init__( self, r=None, g=None, b=None, name=None ) :
        if r!=None and g!=None and b!=None :
            self._r = r
            self._g = g
            self._b = b
        elif name!=None :
            if not(self._set_color(name)) :
                raise ValueError('%r is not a valid color name' % (name,))
        elif r!=None :
            if not(self._set_color(r)) :
                raise ValueError('%r is not a valid color name' % (r,))
        else :
            raise ValueError('You must specifie either r,g,b colors or a color name')

    def _set_color(self,name) :
        if name in self.COLORS :
            self._r = self.COLORS[name][0]
            self._g = self.COLORS[name][1]
            self._b = self.COLORS[name][2]
        else :
            return False
        return True

    def __str__(self) :
        return "#%02x%02x%02x" % (self._r,self._g,self._b)


# -------------------------------------- class : graphRendererBase --
# -------------------------------------------------------------------

class graphRendererBase :
    Color = graphColor
    default_extension = ".none"
    def __init__( self, *args, **kwargs ) :
        self._params = {
            'x' : 768,
            'y' : 1024,
            'default_background_color' : self.Color('white'),
            'default_stroke_color' : self.Color('brown'),
            'default_fill_color' : self.Color('yellow'),
            'default_border' : 1,
            'no_text' : False,
            'use_buffer' : True,
            'fit_to_size' : False,
            'max_size_x' : 0,
            'max_size_y' : 0,
            'natural_size_x' : 0,
            'natural_size_y' : 0,
            }
        for key in kwargs :
            if key in self._params :
                self.set_param(key,kwargs[key])
        self._geobuffer = []
        self._geos_by_z = {}

    def set_param( self, name, value ) :
        self._params[name] = value

    def get_param( self, name ) :
        return self._params[name]

    def set_diagramme_size( self, x, y ) :
        self.set_param('x',x)
        self.set_param('y',y)

    def set_fit_to_size( self ) :
        self.set_param('fit_to_size',True)

    def set_default_background_color( self, default_background_color ) :
        self.set_param('default_background_color',default_background_color)

    def set_default_stroke_color( self, default_stroke_color ) :
        self.set_param('default_stroke_color',default_stroke_color)

    def set_default_fill_color( self, default_fill_color ) :
        self.set_param('default_fill_color',default_fill_color)

    def start_drawing(self) :
        '''this method has to be called between the graph parameters set, and the real drawings. Until this method is called, no file will be created.'''
        if not(self.get_param('use_buffer')) :
            self._start_drawing()
        pass

    def _append_geo( self, geo ) :
        z  = geo[1]['z']
        self._geos_by_z[z] = self._geos_by_z.get(z,[])
        self._geos_by_z[z].append(geo)
        for xstr in ('x0','x1','x') :
            if xstr in geo[1] : 
                if geo[1][xstr]>self.get_param('max_size_x') :
                    self.set_param('max_size_x',geo[1][xstr])
        for ystr in ('y0','y1','y') :
            if ystr in geo[1] : 
                if geo[1][ystr]>self.get_param('max_size_y') :
                    self.set_param('max_size_y',geo[1][ystr])
            
        
    def draw_line( self, x0, y0, x1, y1, color=None, z=0 ) :
        if self.get_param('use_buffer') :
            geo = ('line',{ 'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'color':color, 'z':z })
            self._append_geo(geo)
        else :
            self._draw_line( x0, y0, x1, y1, color, z )
        pass

    def draw_rect( self, x0, y0, x1, y1, color=None, fillcolor=None, text=None, z=0 ) :
        if self.get_param('use_buffer') :
            geo = ('rect',{ 'x0':x0, 'y0':y0, 'x1':x1, 'y1':y1, 'color':color, 'fillcolor':fillcolor, 'text':text, 'z':z })
            self._append_geo(geo)
        else :
            self._draw_rect( x0, y0, x1, y1, color, fillcolor, text, z )
        pass

    def draw_text( self, x, y, text=None, position=5, z=0 ) :
        if self.get_param('use_buffer') :
            geo = ('text',{ 'x':x, 'y':y, 'text':text, 'position':position, 'z':z })
            self._append_geo(geo)
        else :
            self._draw_text( x, y, text, position, z )
        pass

    def stop_drawing(self) :
        '''this method has to be called to end the drawing.'''
        if self.get_param('use_buffer') :
            self._start_drawing()

            zorder = self._geos_by_z.keys()
            zorder.sort()
            geofuncs = {
                'line' : self._draw_line,
                'rect' : self._draw_rect,
                'text' : self._draw_text,
                }
            for z in zorder :
                for geo in self._geos_by_z[z] :
                    for xstr in ('x0','x1','x') :
                        if xstr in geo[1] and self.get_param('fit_to_size') and (self.get_param('natural_size_x') > 0): 
                            geo[1][xstr] = geo[1][xstr]*self.get_param('natural_size_x')/self.get_param('max_size_x')
                    for ystr in ('y0','y1','y') :
                        if ystr in geo[1] and self.get_param('fit_to_size') and (self.get_param('natural_size_y') > 0): 
                            geo[1][ystr] = geo[1][ystr]*self.get_param('natural_size_y')/self.get_param('max_size_y')
                    geofuncs[geo[0]](**(geo[1]))

            self._stop_drawing()
        else :
            self._stop_drawing()
        pass

    def test(self) :
        self.set_diagramme_size(800,600)
        self.set_default_background_color(self.Color(0x00,0x00,0xcc))
        self.set_default_stroke_color(self.Color(0x00,0x00,0x00))
        self.set_default_fill_color(self.Color(0xff,0xff,0xff))
        self.start_drawing()
        self.draw_rect(10,10,110,110)
        self.draw_rect(10,210,110,310,self.Color(0xcc,0xcc,0xff),self.Color(0x80,0x80,0xcc),"poide")
        self.draw_text(10,160,"praf")
        self.draw_line(60,110,60,210)
        self.draw_line(70,110,70,210,self.Color(0xcc,0xcc,0xff))
        self.stop_drawing()

# -------------------------------------- class : graphRendererHTML --
# -------------------------------------------------------------------

class graphRendererHTML( graphRendererBase ) :
    default_extension = ".html"
    HEADER = "<html>\n" + \
             "<head>\n" + \
             "<style type='text/css'>\n" + \
             """<!--\n""" + \
             """body {\n""" + \
             """    position: absolute;\n""" + \
             """    background-color: %(default_background_color)s;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """}\n""" + \
             """.rectborder {\n""" + \
             """    position:absolute;\n""" + \
             """    background-color: %(default_stroke_color)s;\n""" + \
             """    border: 0px;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """}\n""" + \
             """.rect {\n""" + \
             """    position:absolute;\n""" + \
             """    background-color: %(default_fill_color)s;\n""" + \
             """    border: 0;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """}\n""" + \
             """.hline {\n""" + \
             """    position:absolute;\n""" + \
             """    background-color: %(default_stroke_color)s;\n""" + \
             """    border:0px;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """    font-size:1px;\n""" + \
             """}\n""" + \
             """.vline {\n""" + \
             """    position:absolute;\n""" + \
             """    background-color: %(default_stroke_color)s;\n""" + \
             """    border:0px;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """    font-size:1px;\n""" + \
             """}\n""" + \
             """.none {\n""" + \
             """    position:absolute;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """    visibility: hidden;\n""" + \
             """}\n""" + \
             """.textonly {\n""" + \
             """    position:absolute;\n""" + \
             """    border: solid 0px %(default_stroke_color)s;\n""" + \
             """    margin: 0px;\n""" + \
             """    padding: 0px;\n""" + \
             """}\n""" + \
             """.textonly, \n""" + \
             """.rect {\n""" + \
             """    font-size:10px;\n""" + \
             """    font-family:'Verdana;sans-serif';\n""" + \
             """}\n""" + \
             """-->\n""" + \
             """\n""" + \
             """\n""" + \
             """\n""" + \
             """\n""" + \
             """\n""" + \
             """\n""" + \
             """</style>\n""" + \
             """</head>\n""" + \
             """<body>\n""" + \
             """\n""" + \
             """\n"""
    FOOTER = """</body>\n""" + \
             """</html>\n""" + \
             """\n"""
    def __init__( self, *args, **kwargs ) :
        graphRendererBase.__init__(self,args,kwargs)

        local_params = {
            'filename' : 'graph.html',
            }
        for key in local_params :
            if key in kwargs :
                self.set_param(key,kwargs[key])
            else :
                self.set_param(key,local_params[key])
        self._handle = None

    def set_filename( self, filename ) :
        self.set_param('filename',filename)

    def _start_drawing(self) :
        '''this method has to be called between the graph parameters set, and the real drawings. Until this method is called, no file will be created.'''
        self._handle = open(self.get_param('filename'),'wt')
        self._handle.write(self.HEADER % self._params)

    def _draw_line( self, x0, y0, x1, y1, color=None, *args, **kwargs ) :
        extrastyle = ""
        if color :
            extrastyle += ";background-color:%s" % (color,)
        spanclass = "none"
        if x0==x1 :
            spanclass = "vline"
        elif y0==y1 :
            spanclass = "hline"

        border = self.get_param('default_border')
        self._handle.write("<span class='%s' style='left:%dpx;top:%dpx;width:%dpx;height:%dpx%s'></span>\n" % (spanclass,min(x0,x1),min(y0,y1),abs(x0-x1)+border,abs(y0-y1)+border,extrastyle))

    def _draw_rect( self, x0, y0, x1, y1, color=None, fillcolor=None, text=None, *args, **kwargs ) :
        extrastyleborder = ""
        extrastyle = ""
        textcontent = ""
        if fillcolor :
            extrastyle += ";background-color:%s" % (fillcolor,)
        if text :
            textcontent = text
        if color :
            extrastyleborder += ";background-color:%s" % (color,)
        border = self.get_param('default_border')
        self._handle.write("<span class='rectborder' style='left:%dpx;top:%dpx;width:%dpx;height:%dpx%s'>%s</span>\n" % (min(x0,x1),min(y0,y1),abs(x0-x1),abs(y0-y1),extrastyleborder,''))
        self._handle.write("<span class='rect' style='left:%dpx;top:%dpx;width:%dpx;height:%dpx%s'>%s</span>\n" % (min(x0,x1)+border,min(y0,y1)+border,abs(x0-x1)-2*border,abs(y0-y1)-2*border,extrastyle,''))
        if textcontent and not(self.get_param('no_text')):
            self._draw_text( min(x0,x1)+2,min(y0,y1)+2, textcontent, position=7 )


    def _draw_text( self, x, y, text=None, position=5, *args, **kwargs ) :
        if not(self.get_param('no_text')) :
            extrastyle = ""
            textcontent = ""
            if text :
                textcontent = text
            self._handle.write("<span class='textonly' style='left:%dpx;top:%dpx;%s'>%s</span>\n" % (x,y,extrastyle,textcontent))

    def _stop_drawing(self) :
        '''this method has to be called to end the drawing.'''
        self._handle.write(self.FOOTER % self._params)
        self._handle.close()

def test() :
    g = graphRendererHTML()
    g.test()

if __name__ == '__main__' :
    test()
