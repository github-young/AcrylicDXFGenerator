# coding: utf-8
from pywebio import start_server
from pywebio.output import put_text, put_link

from genDXF_TubeShelf_webio import genTubeHolder
from genDXF_Holder_webio import genHolder
from genDXF_CaseSingleWall_webio import genCaseSingleWall


def index():
    put_text("Portal page for all DXF pattern generators:\n")
    put_link(name="Tube Holder", app="genTubeHolder")
    put_text("")
    put_link(name="Case", app="genCaseSingleWall")
    put_text("")
    put_link(name="Regular Holder", app="genHolder")


if __name__ == "__main__":
    port = 8080
    host = "127.0.0.1"
    start_server(
        [index, genTubeHolder, genCaseSingleWall, genHolder], port, host, debug=True
    )
