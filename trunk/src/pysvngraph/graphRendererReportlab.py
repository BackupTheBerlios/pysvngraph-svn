#!/usr/bin/env python
# coding: iso-8859-1

from graphRenderer import graphRendererBase,graphColor
from reportlab.lib import colors
import reportlab.pdfgen.canvas

# --------------------------------------------- class : graphColor --
# -------------------------------------------------------------------

class graphColorReportlab(graphColor) :
    def get_reportlab_color(self) :
        return colors.Color((1.0*self._r)/0xff,(1.0*self._g)/0xff,(1.0*self._b)/0xff)

# --------------------------------- class : graphRendererReportlab --
# -------------------------------------------------------------------

class graphRendererReportlab( graphRendererBase ) :
    Color = graphColorReportlab
    default_extension = ".pdf"

    def __init__( self, *args, **kwargs ) :
        graphRendererBase.__init__(self,args,kwargs)

        local_params = {
            'filename' : 'graph.pdf',
            'stroke_width' : '2',
            #'natural_size_x' : 595.5,
            #'natural_size_y' : 841,
            'natural_size_x' : 575.5,
            'natural_size_y' : 821,
            }
        for key in local_params :
            if key in kwargs :
                self.set_param(key,kwargs[key])
            else :
                self.set_param(key,local_params[key])
        self._canvas = None

    def set_filename( self, filename ) :
        self.set_param('filename',filename)

    def _start_drawing(self) :
        '''this method has to be called between the graph parameters set, and the real drawings. Until this method is called, no file will be created.'''
        self._canvas = reportlab.pdfgen.canvas.Canvas(self.get_param('filename'))
        self._canvas.setFontSize(size=8)
        self._canvas.setFillColor(self._params['default_background_color'].get_reportlab_color())
        self._canvas.rect(0,0,595.5,841, stroke=0, fill=1)

    def _draw_line( self, x0, y0, x1, y1, color=None, *args, **kwargs ) :
        color = color or self._params['default_stroke_color']
        self._canvas.setStrokeColor(color.get_reportlab_color())
        self._canvas.line(
            self._get_xlab(x0), 
            self._get_ylab(y0), 
            self._get_xlab(x1), 
            self._get_ylab(y1)
            )

    def _draw_rect( self, x0, y0, x1, y1, color=None, fillcolor=None, text=None, *args, **kwargs ) :
        fillcolor = fillcolor or self._params['default_fill_color']
        color = color or self._params['default_stroke_color']
        self._canvas.setFillColor(fillcolor.get_reportlab_color())
        self._canvas.setStrokeColor(color.get_reportlab_color())
        self._canvas.rect(
            min(self._get_xlab(x0),self._get_xlab(x1)), 
            min(self._get_ylab(y0),self._get_ylab(y1)), 
            abs(self._get_xlab(x1)-self._get_xlab(x0)), 
            abs(self._get_ylab(y1)-self._get_ylab(y0)), 
            stroke=1, 
            fill=1
            )
        if text and not(self.get_param('no_text')) :
            self._canvas.setFillColor(colors.black)
            self._canvas.drawString(
                min(self._get_xlab(x0),self._get_xlab(x1))+2, 
                min(self._get_ylab(y0),self._get_ylab(y1))+2, 
                text
                )

    def _draw_text( self, x, y, text=None, position=5, *args, **kwargs ) :
        if not(self.get_param('no_text')) :
            self._canvas.setFillColor(colors.black)
            self._canvas.drawString(
                self._get_xlab(x)+2, 
                self._get_ylab(y)+2, 
                text
                )

    def _stop_drawing(self) :
        self._canvas.save()

    def _get_xlab(self,x) :
        return 10+x

    def _get_ylab(self,y) :
        return 831-y

def test() :
    g = graphRendererReportlab()
    g.test()

if __name__ == '__main__' :
    test()
