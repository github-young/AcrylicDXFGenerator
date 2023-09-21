# coding: utf-8
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


class Params:
    pass


def genPoints4Polyline(p):
    pointsGroup = []
    sideLeft = genSide(p, shift=np.array([p.Lx + 5 * p.t, 0]))
    sideRight = genSide(p, shift=np.array([p.Lx + 5 * p.t, p.Lh + p.Lh]))
    ## shift for top, botton and middle
    top = genTopBottom(p, shift=p.shiftTB + np.array([0, 0]))
    bottom = genTopBottom(p, shift=p.shiftTB + np.array([0, p.Ly + p.t]))
    middle = genMiddle(p, shift=p.shiftMiddle)
    ## Merge together
    pointsGroup = sideLeft + sideRight + top + bottom + middle
    return pointsGroup


def genTopBottom(p, shift):
    points = []
    points1 = (
        np.array(
            [
                (0, 0),
                (-2 * p.t, 0),
                (-2 * p.t, p.Ly),
                (p.Lx + 2 * p.t, p.Ly),
                (p.Lx + 2 * p.t, 0),
                (0, 0),
            ]
        )
        + shift
    )
    points2 = (
        np.array([(0, p.Ly1), (-p.t, p.Ly1), (-p.t, p.Ly2), (0, p.Ly2), (0, p.Ly1)])
        + shift
    )
    points3 = (
        np.array(
            [
                (p.Lx, p.Ly1),
                (p.Lx, p.Ly2),
                (p.Lx + p.t, p.Ly2),
                (p.Lx + p.t, p.Ly1),
                (p.Lx, p.Ly1),
            ]
        )
        + shift
    )
    points += [points1.tolist()]
    points += [points2.tolist()]
    points += [points3.tolist()]
    return points


def genMiddle(p, shift):
    points = []
    points1 = (
        np.array(
            [
                (0, 0),
                (-p.err, 0),
                (-p.err, p.Ly1),
                (-p.t - p.err, p.Ly1),
                (-p.t - p.err, p.Ly2),
                (-p.err, p.Ly2),
                (-p.err, p.Ly),
                (p.Lx + p.err, p.Ly),
                (p.Lx + p.err, p.Ly2),
                (p.Lx + p.err + p.t, p.Ly2),
                (p.Lx + p.err + p.t, p.Ly1),
                (p.Lx + p.err, p.Ly1),
                (p.Lx + p.err, 0),
                (0, 0),
            ]
        )
        + shift
    )
    points += [points1.tolist()]
    return points


def genSide(p, shift):
    points = []
    points1 = (
        np.array(
            [
                (0, 0),
                (0, p.Lh),
                (p.Ly1, p.Lh),
                (p.Ly1, p.Lh + p.t),
                (p.Ly2, p.Lh + p.t),
                (p.Ly2, p.Lh),
                (p.Ly, p.Lh),
                (p.Ly, 0),
                (p.Ly2, 0),
                (p.Ly2, -p.t),
                (p.Ly1, -p.t),
                (p.Ly1, 0),
                (0, 0),
            ]
        )
        + shift
    )
    points2 = (
        np.array(
            [
                (p.Ly1, p.hl),
                (p.Ly1, p.hl + p.t),
                (p.Ly2, p.hl + p.t),
                (p.Ly2, p.hl),
                (p.Ly1, p.hl),
            ]
        )
        + shift
    )
    points += [points1.tolist()]
    points += [points2.tolist()]
    return points


def genCircles(p, msp, shift=np.array([0, 0])):
    if p.d > 0:
        for i in range(p.nx):
            for j in range(p.ny):
                msp.add_circle((i * p.dx + shift[0], j * p.dy + shift[1]), p.d / 2)
    return 0


def genPatternDXF(p, pointsGroup, fileName="output.dxf"):
    # Create a new DXF document.
    doc = ezdxf.new(dxfversion="AC1027", setup=True, units=4)
    msp = doc.modelspace()
    for points in pointsGroup:
        msp.add_lwpolyline(points)
    genCircles(p, msp, shift=np.array([0, 0]))
    genCircles(p, msp, shift=p.shiftMiddle - p.shiftTB)
    # save dxf
    doc.saveas(fileName)
    return 0


def rmDXFfile():
    try:
        for f in glob.glob("*.dxf"):
            os.remove(f)
    except:
        pass


def genTubeHolder():
    rmDXFfile()
    put_image(open("images/TubeShelf.png", "rb").read()).style(
        "display:block;margin-left:auto;margin-right:auto;width:75%"
    )
    put_text(
        "Reference diameters for different tubes:\n1.5 mL: \n5 mL: 13.5\n15 mL: 16.5\n50 mL: 30"
    )
    data = input_group(
        label="Tube Shelf DXF generator (Unit: mm)",
        inputs=[
            radio(
                label="Acrylic thickness",
                options=[3, 5],
                name="t",
                inline=True,
                value=3,
            ),
            input(label="Diameter", name="d", type=FLOAT, value=16.5),
            input(label="X number", name="nx", type=NUMBER, value=9),
            input(label="Y number", name="ny", type=NUMBER, value=3),
            input(label="X period", name="dx", type=FLOAT, value=25.0),
            input(label="Y period", name="dy", type=FLOAT, value=25.0),
            input(label="Lower height", name="hl", type=FLOAT, value=30.0),
            input(label="Upper height", name="hu", type=FLOAT, value=20.0),
            radio(
                label='Manually set fine value? (Do not choose "Yes" unless you know its meaning)',
                options=["No", "Yes"],
                name="mannual",
                inline=True,
                value="No",
            ),
            input(
                label="Extra length of middle board", name="err", type=FLOAT, value=0.1
            ),
        ],
    )
    ## Params
    p = Params()
    ## Input params
    p.t = data["t"] * mm
    p.d = data["d"] * mm
    p.nx = data["nx"] * mm
    p.ny = data["ny"] * mm
    p.dx = data["dx"] * mm
    p.dy = data["dy"] * mm
    p.hl = data["hl"] * mm
    p.hu = data["hu"] * mm
    assert min(p.dx, p.dy) > p.d
    if data["mannual"] != "Yes":
        p.err = data["err"]
    else:
        p.err = 0.1 * mm
    ## Derived parmas
    p.mx = min(10 * mm, p.d / 2)
    p.my = min(6 * mm, p.d / 2)
    p.Lx = 2 * p.mx + (p.nx - 1) * p.dx + p.d
    p.Ly = 2 * p.my + (p.ny - 1) * p.dy + p.d
    p.Lh = p.hl + p.t + p.hu
    p.Lyy = int(p.Ly / 3)
    p.Ly1 = (p.Ly - p.Lyy) / 2
    p.Ly2 = p.Ly1 + p.Lyy
    p.shiftTB = np.array([-p.mx - p.d / 2, -p.my - p.d / 2])
    p.shiftMiddle = p.shiftTB + np.array([0, 2 * p.Ly + 2 * p.t])
    ## Generate points
    pointsGroup = genPoints4Polyline(p)
    ## Generate DXF
    dxfFileName = "Holder_d_{:.1f}_{:d}x{:d}_for{:d}mm.dxf".format(
        (p.d / mm), int(p.nx), int(p.ny), int(p.t / mm)
    )
    genPatternDXF(p, pointsGroup, dxfFileName)
    dxfFileContent = open(dxfFileName, "rb").read()
    put_button(
        "Click to download: " + dxfFileName,
        lambda: download(dxfFileName, dxfFileContent),
    )
    return 0


if __name__ == "__main__":
    port = 8080
    host = "127.0.0.1"
    start_server(main, port, host, debug=True)
