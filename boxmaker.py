#!/usr/bin/env python
# coding=utf-8
#
# Copyright (C) 2020 Sudhir Palliyil, sudhir@kreu.org
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
"""
Creating SVG paths for sides of a tabbed box, to be cut on a laser cutter. For Inkscape 1.0
"""

import inkex,simplestyle
from lxml import etree


def drawS(XYstring):         # Draw lines from a list
    #global parent
    name='part'
    style = { 'stroke': '#000000', 'fill': 'none' }
    drw = {'style':str(inkex.Style(style)),inkex.addNS('label','inkscape'):name,'d':XYstring}
    #drw = {'style':simplestyle.formatStyle(style),inkex.addNS('label','inkscape'):name,'d':XYstring}
    etree.SubElement(parent, inkex.addNS('path','svg'), drw )


# def side((rx,ry),(sox,soy),(eox,eoy),tabVec,length,(dirx,diry),isTab):

def side(r,s,e,tabVec,length,dir,isTab):
    (rx,ry)=r
    (sox,soy)=s
    (eox,eoy)=e
    (dirx,diry)=dir
    #       root startOffset endOffset tabVec length  direction  isTab

    divs=int(length/nomTab)  # divisions
    if not divs%2: divs-=1   # make divs odd
    divs=float(divs)
    tabs=(divs-1)/2          # tabs for side
  
    if equalTabs:
        gapWidth=tabWidth=length/divs
    else:
        tabWidth=nomTab
        gapWidth=(length-tabs*nomTab)/(divs-tabs)
    
    if isTab:                 # kerf correction
        gapWidth-=correction
        tabWidth+=correction
        first=correction/2
    else:
        gapWidth+=correction
        tabWidth-=correction
        first=-correction/2
    
    s=[] 
    firstVec=0; secondVec=tabVec
    dirxN=0 if dirx else 1 # used to select operation on x or y
    diryN=0 if diry else 1
    (Vx,Vy)=(rx+sox*thickness,ry+soy*thickness)
    s='M '+str(Vx)+','+str(Vy)+' '

    if dirxN: Vy=ry # set correct line start
    if diryN: Vx=rx

    # generate line as tab or hole using:
    #   last co-ord:Vx,Vy ; tab dir:tabVec  ; direction:dirx,diry ; thickness:thickness
    #   divisions:divs ; gap width:gapWidth ; tab width:tabWidth

    for n in range(1,int(divs)):
        if n%2:
            Vx=Vx+dirx*gapWidth+dirxN*firstVec+first*dirx
            Vy=Vy+diry*gapWidth+diryN*firstVec+first*diry
            s+='L '+str(Vx)+','+str(Vy)+' '
            Vx=Vx+dirxN*secondVec
            Vy=Vy+diryN*secondVec
            s+='L '+str(Vx)+','+str(Vy)+' '
        else:
            Vx=Vx+dirx*tabWidth+dirxN*firstVec
            Vy=Vy+diry*tabWidth+diryN*firstVec
            s+='L '+str(Vx)+','+str(Vy)+' '
            Vx=Vx+dirxN*secondVec
            Vy=Vy+diryN*secondVec
            s+='L '+str(Vx)+','+str(Vy)+' '
        (secondVec,firstVec)=(-secondVec,-firstVec) # swap tab direction
        first=0
    s+='L '+str(rx+eox*thickness+dirx*length)+','+str(ry+eoy*thickness+diry*length)+' '
    return s

class BoxMaker(inkex.Effect):
    """Please rename this class, don't keep it unnamed"""
    def add_arguments(self, pars):
        #pars.add_argument("--my_option", type=inkex.Boolean,\
        #    help="An example option, put your options here")
        pars.add_argument('--unit',type=str,
            dest='unit',default='mm',help='Measure Units')
        pars.add_argument('--inside',type=int,
            dest='inside',default=0,help='Int/Ext Dimension')
        pars.add_argument('--length',type=float,
            dest='length',default=100,help='Length of Box')
        pars.add_argument('--width',type=float,
            dest='width',default=100,help='Width of Box')
        pars.add_argument('--depth',type=float,
            dest='height',default=100,help='Height of Box')
        pars.add_argument('--tab',type=float,
            dest='tab',default=25,help='Nominal Tab Width')
        pars.add_argument('--equal',type=int,
            dest='equal',default=0,help='Equal/Prop Tabs')
        pars.add_argument('--thickness',type=float,
            dest='thickness',default=10,help='Thickness of Material')
        pars.add_argument('--kerf',type=float,
            dest='kerf',default=0.5,help='Kerf (width) of cut')
        pars.add_argument('--clearance',type=float,
            dest='clearance',default=0.01,help='Clearance of joints')
        pars.add_argument('--style',type=int,
            dest='style',default=25,help='Layout/Style')
        pars.add_argument('--spacing',type=float,
            dest='spacing',default=25,help='Part Spacing')

    def effect(self):
        global parent,nomTab,equalTabs,thickness,correction
        # Get access to main SVG document element and get its dimensions.
        svg = self.document.getroot()

        # Get the attibutes:
        widthDoc  = self.svg.unittouu(svg.get('width'))
        heightDoc = self.svg.unittouu(svg.get('height'))
        
        # Create a new layer.
        layer = etree.SubElement(svg, 'g')
        layer.set(inkex.addNS('label', 'inkscape'), 'box')
        layer.set(inkex.addNS('groupmode', 'inkscape'), 'layer')

        parent=self.svg.get_current_layer()
        #inkex.utils.debug(parent)

        # Get script's option values.
        unit=self.options.unit
        inside=self.options.inside
        X = self.svg.unittouu( str(self.options.length)  + unit )
        Y = self.svg.unittouu( str(self.options.width) + unit )
        Z = self.svg.unittouu( str(self.options.height)  + unit )
        thickness = self.svg.unittouu( str(self.options.thickness)  + unit )
        nomTab = self.svg.unittouu( str(self.options.tab) + unit )
        equalTabs=self.options.equal
        kerf = self.svg.unittouu( str(self.options.kerf)  + unit )
        clearance = self.svg.unittouu( str(self.options.clearance)  + unit )
        layout=self.options.style
        spacing = self.svg.unittouu( str(self.options.spacing)  + unit )        

        if inside: # if inside dimension selected correct values to outside dimension
          X+=thickness*2
          Y+=thickness*2
          Z+=thickness*2
        correction=kerf-clearance

        # check input values mainly to avoid python errors
        # TODO restrict values to *correct* solutions
        error=0
        if min(X,Y,Z)==0:
            inkex.errormsg(_('Error: Dimensions must be non zero'))
            error=1
        if max(X,Y,Z)>max(widthDoc,heightDoc)*10: # crude test
            inkex.errormsg(_('Error: Dimensions Too Large'))
            error=1
        if min(X,Y,Z)<3*nomTab:
            inkex.errormsg(_('Error: Tab size too large'))
            error=1
        if nomTab<thickness:
            inkex.errormsg(_('Error: Tab size too small'))
            error=1	  
        if thickness==0:
            inkex.errormsg(_('Error: Thickness is zero'))
            error=1	  
        if thickness>min(X,Y,Z)/3: # crude test
            inkex.errormsg(_('Error: Material too thick'))
            error=1	  
        if correction>min(X,Y,Z)/3: # crude test
            inkex.errormsg(_('Error: Kerf/Clearence too large'))
            error=1	  
        if spacing>max(X,Y,Z)*10: # crude test
            inkex.errormsg(_('Error: Spacing too large'))
            error=1	  
        if spacing<kerf:
            inkex.errormsg(_('Error: Spacing too small'))
            error=1	  

        if error: exit()

        # layout format:(rootx),(rooty),Xlength,Ylength,tabInfo
        # root= (spacing,X,Y,Z) * values in tuple
        # tabInfo= <abcd> 0=holes 1=tabs
        if   layout==1: # Diagramatic Layout
            pieces=[[(2,0,0,1),(3,0,1,1),X,Z,0b1010],[(1,0,0,0),(2,0,0,1),Z,Y,0b1111],
                [(2,0,0,1),(2,0,0,1),X,Y,0b0000],[(3,1,0,1),(2,0,0,1),Z,Y,0b1111],
                [(4,1,0,2),(2,0,0,1),X,Y,0b0000],[(2,0,0,1),(1,0,0,0),X,Z,0b1010]]
        elif layout==2: # 3 Piece Layout
            pieces=[[(2,0,0,1),(2,0,1,0),X,Z,0b1010],[(1,0,0,0),(1,0,0,0),Z,Y,0b1111],
                    [(2,0,0,1),(1,0,0,0),X,Y,0b0000]]
        elif layout==3: # Inline(compact) Layout
            pieces=[[(1,0,0,0),(1,0,0,0),X,Y,0b0000],[(2,1,0,0),(1,0,0,0),X,Y,0b0000],
                    [(3,2,0,0),(1,0,0,0),Z,Y,0b0101],[(4,2,0,1),(1,0,0,0),Z,Y,0b0101],
                    [(5,2,0,2),(1,0,0,0),X,Z,0b1111],[(6,3,0,2),(1,0,0,0),X,Z,0b1111]]
        elif layout==4: # Diagramatic Layout with Alternate Tab Arrangement
            pieces=[[(2,0,0,1),(3,0,1,1),X,Z,0b1001],[(1,0,0,0),(2,0,0,1),Z,Y,0b1100],
                    [(2,0,0,1),(2,0,0,1),X,Y,0b1100],[(3,1,0,1),(2,0,0,1),Z,Y,0b0110],
                    [(4,1,0,2),(2,0,0,1),X,Y,0b0110],[(2,0,0,1),(1,0,0,0),X,Z,0b1100]]

        for piece in pieces: # generate and draw each piece of the box
            (xs,xx,xy,xz)=piece[0]
            (ys,yx,yy,yz)=piece[1]
            x=xs*spacing+xx*X+xy*Y+xz*Z  # root x co-ord for piece
            y=ys*spacing+yx*X+yy*Y+yz*Z  # root y co-ord for piece
            dx=piece[2]
            dy=piece[3]
            tabs=piece[4]
            a=tabs>>3&1; b=tabs>>2&1; c=tabs>>1&1; d=tabs&1 # extract tab status for each side
            # generate and draw the sides of each piece
            #inkex.utils.debug(side((x,y),(d,a),(-b,a),-thickness if a else thickness,dx,(1,0),a))
            drawS(side((x,y),(d,a),(-b,a),-thickness if a else thickness,dx,(1,0),a))          # side a
            drawS(side((x+dx,y),(-b,a),(-b,-c),thickness if b else -thickness,dy,(0,1),b))     # side b
            drawS(side((x+dx,y+dy),(-b,-c),(d,-c),thickness if c else -thickness,dx,(-1,0),c)) # side c
            drawS(side((x,y+dy),(d,-c),(d,a),-thickness if d else thickness,dy,(0,-1),d))      # side d

        #selectedObject = self.svg.selected[self.options.ids[0]]
        #typeOfSelectedObject = selectedObject.tag
        #inkex.utils.debug("I am a: ")
        #inkex.utils.debug(pieces)
        #inkex.utils.debug(" !")
        #for elem in self.svg.get_selected():
        #    elem.style['fill']='red'

if __name__ == '__main__':
    BoxMaker().run()