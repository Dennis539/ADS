from bs4 import BeautifulSoup
import nbformat as nbf
import requests
import os
import html
import time
from urllib.parse import urljoin

precode = """import pcraster as pcr
pcr.setrandomseed(8)
buildgMap = pcr.readmap("mapalgebra/buildg.map")
firestatMap = pcr.readmap("mapalgebra/firestat.map")
iswaterMap = pcr.readmap("mapalgebra/iswater.map")
phreaticMap = pcr.readmap("mapalgebra/phreatic.map")
rainstorMap = pcr.readmap("mapalgebra/rainstor.map")
roadsMap = pcr.readmap("mapalgebra/roads.map")
topoMap = pcr.readmap("mapalgebra/topo.map")
waterMap = pcr.readmap("mapalgebra/water.map")
dumpMap = pcr.readmap("mapalgebra/dump.map")
isroadMap = pcr.readmap("mapalgebra/isroad.map")
loggingMap = pcr.readmap("mapalgebra/logging.map")
pointsMap = pcr.readmap("mapalgebra/points.map")
rainyearMap = pcr.readmap("mapalgebra/rainyear.map")
soilsMap = pcr.readmap("mapalgebra/soils.map")
treesMap = pcr.readmap("mapalgebra/trees.map")
wellsMap = pcr.readmap("mapalgebra/wells.map")"""
def create_notebook(soup: BeautifulSoup, pure_python: bool = True):

    nb = nbf.v4.new_notebook()
    cells = [nbf.v4.new_code_cell(precode)]
    title = soup.find("title").get_text()
    print(title)
    notebook_path, notebook_folder = title.split("Keesje")
    notebook_path = notebook_path.replace(":", " - ")
    # Example: put each <p> into a markdown cell and each <pre><code> into code cells
    for tag in soup.find_all(["p", "pre","blockquote", "table", "ul"]):
        if tag.name == "p" and (tag.find_parent("blockquote") or tag.find_parent("table") or tag.find_parent("ul")):
            continue
        if tag.name == "p":
            cells.append(nbf.v4.new_markdown_cell(tag.get_text()))
        elif tag.name in ["blockquote", "table", "ul"]:
            # answers = "- " + "\n- ".join([sub_tag.get_text() for sub_tag in tag.find_all("p")])
            # cells.append(nbf.v4.new_markdown_cell(answers))
            if tag.name == "ul" and tag.findChildren("a"):
                continue
            cells.append(nbf.v4.new_markdown_cell(str(tag)))
        elif tag.name == "pre":
            code = tag.get_text()
            if code and type(code) == str:
                code = code.replace("<Enter>", "").replace("<enter>", "")
                if pure_python and code.startswith(("aguila", "gdal")):
                    code = f'import subprocess \nsubprocess.call("""{code}""", shell=True)'
                cells.append(nbf.v4.new_code_cell(code))


    nb["cells"] = cells

    if not os.path.exists(notebook_folder):
        os.mkdir(notebook_folder)

    with open(os.path.join("", notebook_path + ".ipynb"), "w", encoding="utf-8") as f:
        nbf.write(nb, f)

    print("Notebook created:", notebook_path)



base_link = "https://karssenberg.geo.uu.nl/labs/"
intermediate_link = "https://karssenberg.geo.uu.nl/labs/mapalgebra/"
end_path = "01_pcrasterMaps.html"

while True:
    if ".." in end_path:
        intermediate_link = urljoin(base_link, end_path.split("/")[1]) + "/"
        final_path = urljoin(intermediate_link, end_path.split("/")[-1])
    else:
        final_path = urljoin(intermediate_link, end_path)
    res = requests.get(final_path, verify=False)

    site_text = res.text.replace("&#8212;", "Keesje" )
    soup = BeautifulSoup(site_text, "lxml")
    if ".." not in end_path:
        create_notebook(soup, False)

    next_link = soup.find("a", {"title" : "Next document"})
    end_path = next_link["href"]
    if not end_path:
        break
    print(final_path)

    time.sleep(0.1)
