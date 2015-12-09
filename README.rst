O*NET Neighbors
===============

Visualization of `O*NET <https://www.onetonline.org/>`_ occupations as a network graph.

`See the O*NET Neighbors graph here <https://jaza.github.io/onet-neighbors/>`_.

**Note:** this is still a work in progress. Don't expect a terribly pretty or usable graph just yet.

Many thanks to the blog post: `R vs Python: head to head data analysis <https://www.dataquest.io/blog/python-vs-r/>`_, particularly for guidance with `PCA <http://setosa.io/ev/principal-component-analysis/>`_ and scatter plots.

Also thanks to the `Cotrino Language Network <http://languagenetwork.cotrino.com/>`_ prototype, upon which the front-end of this prototype is heavily based. Much like the Language Network, this visualization is powered by a `Force-Directed Network Graph <http://bl.ocks.org/mbostock/4062045>`_ in `D3.js <http://d3js.org/>`_.

The data processing done for this prototype is quite rudimentary at the moment. It's treating all O*NET knowledge, skills, and abilities scores for all occupations as being of equal significance. The scores should ideally be weighted in some intelligent way (e.g. with `Random Forests <https://en.wikipedia.org/wiki/Random_forest>`_?), before being visualized.


Quickstart
----------

Check out the repository ::

    git clone https://github.com/Jaza/onet-neighbors.git
    cd onet-neighbors

Start a local web server ::

    python -m SimpleHTTPServer

And navigate to ``http://localhost:8000/`` in your web browser. You should see the graph writhing around in all its glory.


Dependencies
------------

To process the O*NET data locally, you'll need a few things installed. Most importantly, Python's `NumPy <http://www.numpy.org/>`_ and `SciPy <http://www.scipy.org/>`_ libraries. These can easily be installed on Ubuntu / Debian with ::

    sudo apt-get install python-numpy
    sudo apt-get install python-scipy

The other Python dependencies can be installed more easily with ``pip`` (recommended to install inside a virtualenv) ::

    pip install -r requirements.txt

Plus, you need the O*NET data itself. Go the `O*NET Production Database page <https://www.onetcenter.org/database.html>`_, click the "All Files" tab, and click the "Text" download link for the latest version of the database. Extract the tab-delimited text files to a folder called ``onetdb`` in the project root (or anywhere else you want).


O*NET Data Processing Scripts
-----------------------------

To build a CSV of all O*NET occupations and their knowledge / skills / abilities in a single matrix ::

    python scripts/make_occupation_matrix_csv.py --occupation-tsv="./onetdb/occupation_data.tsv" --knowledge-tsv="./onetdb/knowledge.tsv" --skills-tsv="./onetdb/skills.tsv" --abilities-tsv="./onetdb/abilities.tsv" --output-csv="./csv/occupation_matrix.csv"

To reduce the dimensions of the Occupation Matrix using PCA, and to render the PCA data as a scatter plot ::

    python scripts/render_pca_plot.py --input-csv="./csv/occupation_matrix.csv"

To make a JS file with all occupations in an array ::

    python scripts/make_occupation_list_js.py --input-csv="./csv/occupation_matrix.csv" --output-js="./js/occupation-list.js"

To reduce the dimensions of the Occupation Matrix using PCA, find each occupation's nearest neighbors using `k-d trees <https://en.wikipedia.org/wiki/K-d_tree>`_, and make a JavaScript file with all neighbors in an array ::

    python scripts/make_occupation_neighbors_js.py --input-csv="./csv/occupation_matrix.csv" --output-js="./js/occupation-neighbors.js"
