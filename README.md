[![Generate RDF from Google doc](https://github.com/MaastrichtU-IDS/food-claims-kg/workflows/Generate%20RDF%20from%20Google%20doc/badge.svg)](actions)

A RDF knowledge graph for food health claims.

The easiest way to explore the knowledge graph is to use the various API calls at http://grlc.io/api-git/MaastrichtU-IDS/food-claims-kg 

> API powered by [grlc.io](http://grlc.io)

The SPARQL endpoint is accessible at https://graphdb.dumontierlab.com/repositories/FoodHealthClaimsKG

## Check the SPARQL queries

Queries from the grlc API can be checked and changed in the `.rq` files. Variable starting with an underscore, such as `_claimlabel`, are asked to the user as parameter of the generated call.

## Run conversion scripts

Clone the repository:

```bash
git clone https://github.com/MaastrichtU-IDS/food-claims-kg.git
cd food-claims-kg
```

Install requirements:

```bash
pip3 install -r requirements.txt
```

Download the data:

```bash
mkdir -p data/output
wget -O data/food-claims-kg.xlsx "https://docs.google.com/spreadsheets/d/1RWZ6AlGB8m7PO5kjsbbbeI4ETLwvKLOvkrzOpl8zAM8/export?format=xlsx&id=1RWZ6AlGB8m7PO5kjsbbbeI4ETLwvKLOvkrzOpl8zAM8"
```

Run the conversion script:

```bash
python3 src/convert_to_rdf.py
```

## grlc API examples

IRI variable with defaults value (not working for our repo):

* https://github.com/albertmeronyo/lodapi/blob/master/dbpedia_test.rq
* API: http://grlc.io/api-git/albertmeronyo/lodapi#/dbpedia/get_dbpedia_test

String variable: 

* https://github.com/CLARIAH/wp4-queries-hisco/blob/master/get-hisco-hiscam.rq
* API: http://grlc.io/api-git/CLARIAH/wp4-queries-hisco#/hisco/get_get_hisco_hiscam

Enumerate:

* https://github.com/CLARIAH/grlc-queries/blob/master/enumerate.rq
* API: http://grlc.io/api-git/CLARIAH/grlc-queries/#/default/get_enumerate

