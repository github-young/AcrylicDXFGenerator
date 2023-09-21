#coding:utf-8
import numpy as np
import ezdxf
import glob, os
from pywebio import start_server
from pywebio.platform import path_deploy
from pywebio.input import input, input_group, FLOAT, NUMBER, radio
from pywebio.output import put_file, put_text, put_image, put_button
from pywebio.session import download

mm = 1
cm = 10
um = 1e-3

class Params():
    pass

def genAllPoints(p):
    pointsGroup = []
    bottom = genBottomPoints(p, shift = np.array([p.l/2+p.t+p.m, p.w/2+p.t+p.m]))
    top = genBottomPoints(p, shift = np.array([3*p.l/2+4*p.t+3*p.m, p.w/2+p.t+p.m]))
    front = genSidePoints(L=p.l, LL=p.ll, H=p.h, shift=np.array([0, p.w+p.h+7*p.t+2*p.m]), p=p)
    left = genSidePoints(L=p.w, LL=p.ww, H=p.h, shift=np.array([p.l+6*p.t, p.w+p.h+7*p.t+2*p.m]), p=p)
    back = genSidePoints(L=p.l, LL=p.ll, H=p.h, shift=np.array([0, p.w+4*p.t+2*p.m]), p=p)
    right = genSidePoints(L=p.w, LL=p.ww, H=p.h, shift=np.array([p.l+6*p.t, p.w+4*p.t+2*p.m]), p=p)
    pointsGroup = bottom + top + [front, back, left, right]
    return pointsGroup

def genBottomPoints(p, shift):
    pointsGroup = []
    pointsGroup += [np.array([(-(p.l/2+p.t+p.m), -(p.w/2+p.t+p.m)), (-(p.l/2+p.t+p.m), p.w/2+p.t+p.m), (p.l/2+p.t+p.m, p.w/2+p.t+p.m), (p.l/2+p.t+p.m, -(p.w/2+p.t+p.m)), (-(p.l/2+p.t+p.m), -(p.w/2+p.t+p.m))])+shift]
    pointsGroup += [np.array([(-(p.l/2+p.t), -p.ww/2), (-(p.l/2+p.t), p.ww/2), (-p.l/2, p.ww/2), (-p.l/2, -p.ww/2), (-(p.l/2+p.t), -p.ww/2)])+shift]
    pointsGroup += [np.array([(p.l/2, -p.ww/2), (p.l/2, p.ww/2), (p.l/2+p.t, p.ww/2), (p.l/2+p.t, -p.ww/2), (p.l/2, -p.ww/2)])+shift]
    pointsGroup += [np.array([(-p.ll/2, p.w/2), (-p.ll/2, p.w/2+p.t), (p.ll/2, p.w/2+p.t), (p.ll/2, p.w/2), (-p.ll/2, p.w/2)])+shift]
    pointsGroup += [np.array([(-p.ll/2, -p.w/2-p.t), (-p.ll/2, -p.w/2), (p.ll/2, -p.w/2), (p.ll/2, -p.w/2-p.t), (-p.ll/2, -p.w/2-p.t)])+shift]
    return pointsGroup

def genSidePoints(L, LL, H, shift, p):
    points = []
    assert LL == p.ll or LL == p.ww
    HH = H/2
    errorFactor = 4/5
    points += [(0, 0), (0, (H-HH)/2), (p.t, (H-HH)/2), (p.t , (H+HH)/2), (0, (H+HH)/2), (0, H), (p.t+(L-LL)/2-p.e, H), (p.t+(L-LL)/2-p.e*errorFactor, H+p.t), (p.t+(L+LL)/2+p.e*errorFactor, H+p.t), (p.t+(L+LL)/2+p.e, H), (p.t+L, H), (p.t+L, (H+HH)/2+p.e), (p.t+L+p.t, (H+HH)/2+p.e*errorFactor), (p.t+L+p.t, (H-HH)/2-p.e*errorFactor), (p.t+L, (H-HH)/2-p.e), (p.t+L, 0), (p.t+(L+LL)/2+p.e, 0), (p.t+(L+LL)/2+p.e*errorFactor, -p.t), (p.t+(L-LL)/2-p.e*errorFactor, -p.t), (p.t+(L-LL)/2-p.e, 0), (0, 0)]
    return np.array(points)+shift

def genPatternDXF(pointsGroup, fileName="output.dxf"):
    # Create a new DXF document.
    doc = ezdxf.new(dxfversion='AC1027', setup=True, units=4)
    msp = doc.modelspace()
    for points in pointsGroup:
        msp.add_lwpolyline(points)
    # save dxf
    doc.saveas(fileName)
    return 0

def rmDXFfile():
    try:
        for f in glob.glob("*.dxf"):
            os.remove(f)
    except:
        pass


def genCaseSingleWall():
    rmDXFfile()
    put_image(open("images/CaseSingleWall.jpg", 'rb').read()).style('display:block;margin-left:auto;margin-right:auto;width:50%')
    data = input_group(label="Simple Case DXF generator (Unit: mm)", inputs=[
        radio(label='Acrylic thickness', options=[3, 5, 2], name='t', inline=True, value=3),
        input(label='length', name='l', type=FLOAT, value=60),
        input(label='width', name='w', type=FLOAT, value=40,),
        input(label='height', name='h', type=FLOAT, value=20),
        input(label='margin', name='m', type=FLOAT, value=3),
        input(label='tolerance (0.20~0.25 mm). Try small samples first', name='e', type=FLOAT, value=0.022)
    ])
    ## Params
    p = Params()
    ## Input params
    p.t = data["t"]*mm                 # Acrylic thickness
    p.l = data["l"]*mm                 # Length
    p.w = data["w"]*mm                 # Width
    p.h = data["h"]*mm                 # Height
    p.m = max(p.t, data["m"]*mm)       # margin: Distance between hole and edge
    p.e = data["e"]*mm          # Error for the cutting: 0.20~0.22 mm
    ## Generated params
    p.ll = int(p.l/3/mm)
    p.ww = int(p.w/3/mm)
    ## Generate points
    pointsGroup = genAllPoints(p)
    ## Generate DXF
    dxfFileName = "Case_{:d}x{:d}x{:d}_for{:d}mm.dxf".format(int(p.l/mm), int(p.w/mm), int(p.h/mm), int(p.t/mm))
    genPatternDXF(pointsGroup, dxfFileName)
    dxfFileContent = open(dxfFileName, 'rb').read()
    put_button("Click to download: "+dxfFileName, lambda: download(dxfFileName, dxfFileContent))
    return 0

if __name__ == '__main__':
    port = 8080
    host = "127.0.0.1"
    start_server(main, port, host, debug=True)