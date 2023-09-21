#coding: utf-8
# Author: Yang XU <yxucn@connect.ust.hk>
# LICENSE: MIT
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
    top = genTopPoints(p, shift=np.array([p.l/2, p.w/2]))
    F  = genFBPoints(p, shift=np.array([p.l+p.t, 0]))
    B  = genFBPoints(p, shift=np.array([2*(p.l+p.t), 0]))
    L  = genLRPoints(p, shift=np.array([3*(p.l+p.t), 0]))
    R  = genLRPoints(p, shift=np.array([3*(p.l+p.t), p.w+p.t]))
    pointsGroup = top + [F, B, L, R]
    return pointsGroup

def genTopPoints(p, shift):
    points = []
    roundCornerBulge = -(np.sqrt(2)-1)
    points += [[(p.t, 0, 0, 0, roundCornerBulge), (0, p.t), (0, p.w-p.t, 0, 0, roundCornerBulge), (p.t, p.w), (p.l-p.t, p.w, 0, 0, roundCornerBulge), (p.l, p.w-p.t), (p.l, p.t, 0, 0, roundCornerBulge), (p.l-p.t, 0), (p.t, 0)]]
    points += [[(-p.ll/2, p.w/2-p.m-p.t), (-p.ll/2, p.w/2-p.m), (p.ll/2, p.w/2-p.m), (p.ll/2, p.w/2-p.m-p.t), (-p.ll/2, p.w/2-p.m-p.t)]+shift]
    points += [[(-p.ll/2, -p.w/2+p.m), (-p.ll/2, -p.w/2+p.m+p.t), (p.ll/2, -p.w/2+p.m+p.t), (p.ll/2, -p.w/2+p.m), (-p.ll/2, -p.w/2+p.m)]+shift]
    points += [[(-p.l/2+p.m, -p.ww/2), (-p.l/2+p.m, p.ww/2), (-p.l/2+p.m+p.t, p.ww/2), (-p.l/2+p.m+p.t, -p.ww/2), (-p.l/2+p.m, -p.ww/2)]+shift]
    points += [[(p.l/2-p.m-p.t, -p.ww/2), (p.l/2-p.m-p.t, p.ww/2), (p.l/2-p.m, p.ww/2), (p.l/2-p.m, -p.ww/2), (p.l/2-p.m-p.t, -p.ww/2)]+shift]
    return points

def genFBPoints(p, shift):
    points = []
    incH = p.incH
    extraGap = p.extraGap
    points1 = np.array([(0, 0), (0, p.h), (p.m, p.h), (p.m, p.hh), (p.m+p.t, p.hh), (p.m+p.t, p.h), ((p.l-p.ll)/2, p.h), ((p.l-p.ll)/2, p.h+p.t), ((p.l+p.ll)/2, p.h+p.t), ((p.l+p.ll)/2, p.h), (p.l-p.m-p.t, p.h), (p.l-p.m-p.t, p.hh), (p.l-p.m, p.hh), (p.l-p.m, p.h), (p.l, p.h), (p.l, 0)])+shift
    pointsBulge = [(p.l-p.m-extraGap+shift[0], 0+shift[1]), (p.l-p.m-extraGap+shift[0], incH+shift[1], 0, 0, p.bulgeL), (p.m+extraGap+shift[0], incH+shift[1]), (p.m+extraGap+shift[0], 0+shift[1])]
    # pointsBulge = [(p.l-p.m-p.t+shift[0], 0+shift[1], 0, 0, p.bulgeL)]
    points2 = np.array([(p.m+p.t, 0), (0, 0)])+shift
    points += points1.tolist()
    points += pointsBulge
    points += points2.tolist()
    return points

def genLRPoints(p, shift):
    points = []
    incH = p.incH
    extraGap = p.extraGap
    points1 = np.array([(0, 0), (0, p.m), (p.h-p.hh, p.m), (p.h-p.hh, p.m+p.t), (0, p.m+p.t)])+shift
    pointsBulge = [(0+shift[0], p.m+extraGap+shift[1]), (incH+shift[0], p.m+extraGap+shift[1]), (incH+shift[0], p.m+extraGap+shift[1], 0, 0, p.bulgeW), (incH+shift[0], p.w-p.m-extraGap+shift[1]), (0+shift[0], p.w-p.m-extraGap+shift[1])]
    points2 = np.array([(0, p.w-p.m-2*p.t), (0, p.w-p.m-p.t), (p.h-p.hh, p.w-p.m-p.t), (p.h-p.hh, p.w-p.m), (0, p.w-p.m), (0, p.w), (p.h, p.w), (p.h, (p.w+p.ww)/2), (p.h+p.t, (p.w+p.ww)/2), (p.h+p.t, (p.w-p.ww)/2), (p.h, (p.w-p.ww)/2), (p.h, 0), (0, 0)])+shift
    points += points1.tolist()
    points += pointsBulge
    points += points2.tolist()
    return points

def genPatternDXF(p, pointsGroup, fileName="output.dxf"):
    # Create a new DXF document.
    doc = ezdxf.new(dxfversion='AC1027', setup=True, units=4)
    msp = doc.modelspace()
    for points in pointsGroup:
        msp.add_lwpolyline(points)
    if p.r != 0:
        msp.add_circle((p.l/2, p.w/2), p.r)
    # save dxf
    doc.saveas(fileName)
    return 0


def rmDXFfile():
    try:
        for f in glob.glob("*.dxf"):
            os.remove(f)
    except:
        pass


def genHolder():
    rmDXFfile()
    put_image(open("images/Holder.png", 'rb').read()).style('display:block;margin-left:auto;margin-right:auto;width:75%')
    data = input_group(label="Holder DXF generator (Unit: mm)", inputs=[
        radio(label='Acrylic thickness', options=[5, 3], name='t', inline=True, value=5),
        input(label='margin', name='m', type=FLOAT, value=10),
        input(label='length', name='l', type=FLOAT, value=120),
        input(label='width', name='w', type=FLOAT, value=100,),
        input(label='height', name='h', type=FLOAT, value=160),
        input(label='radius (input 0 to disable)', name='r', type=FLOAT, value=45),
        input(label='Arc increased height', name='incH', type=FLOAT, value=80),
        radio(label='Manually set bulge value? (Do not choose "Yes" unless you know its meaning)', options=["No", "Yes"], name='bf', inline=True, value="No"),
        input(label='bulge along length side: [0, 1]', name='bl', type=FLOAT, value=0),
        input(label='bulge along width side: [0, 1]', name='bw', type=FLOAT, value=0)
    ])
    ## Params
    p = Params()
    ## Input params
    p.t = data["t"]*mm                            # Acrylic thickness
    p.l = data["l"]*mm                            # Length
    p.w = data["w"]*mm                            # Width
    p.h = data["h"]*mm                            # Height
    p.incH = min((p.h-2*p.t)/2, data["incH"]*mm)  # increased height for bulge
    #assert p.h >= p.incH+2*p.t                    # incH should be smaller than total height
    p.m = max(2*p.t, data["m"]*mm)                # margin: Distance between foot and edge
    #assert p.m >= 2*p.t                           # margin should not be too thin
    p.r = min((min(p.l, p.w) - 2*p.m - 4*p.t)/2, data["r"]*mm)              # Radius of top hole; set 0 to disable
    #assert 2*p.r <= min(p.l, p.w)-2*p.m-2*p.t # Radius should be kept within the margin
    p.extraGap = 3*p.t              # distance between bulge and slot
    ## Generated params
    p.ll = int(p.l/3/mm)
    p.ww = int(p.w/3/mm)
    p.hh = p.h/2
    if data["bf"] != "Yes":
        p.bulgeL = min(1, (2*p.h-4*p.t-2*p.incH)/(p.l - 2*p.m - 2*p.extraGap))
        p.bulgeW = min(1, (2*p.h-4*p.t-2*p.incH)/(p.w - 2*p.m - 2*p.extraGap))
    else:
        p.bulgeL = min(1, data["bl"])
        p.bulgeW = min(1, data["bw"])
    # print(p.bulgeL, p.bulgeW)
    assert p.bulgeL*p.bulgeW >= 0
    ## Generate points
    pointsGroup = genAllPoints(p)
    ## Generate DXF
    dxfFileName = "Holder_{:d}x{:d}x{:d}-{:d}_for{:d}mm.dxf".format(int(p.l/mm), int(p.w/mm), int(p.h/mm), int(p.m/mm), int(p.t/mm))
    genPatternDXF(p, pointsGroup, dxfFileName)
    dxfFileContent = open(dxfFileName, 'rb').read()
    put_button("Click to download: "+dxfFileName, lambda: download(dxfFileName, dxfFileContent))
    return 0

if __name__ == '__main__':
    port = 8080
    host = "127.0.0.1"
    start_server(main, port, host, debug=True)
