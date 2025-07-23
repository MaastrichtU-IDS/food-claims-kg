A RDF knowledge graph for food health claims.

* SPARQL endpoint accessible at https://graphdb.dumontierlab.com/repositories/FoodHealthClaimsKG
* OpenAPI with [grlc.io](http://grlc.io) at http://grlc.io/api-git/MaastrichtU-IDS/food-claims-kg
* Or using the URL: http://grlc.io/api-url?specUrl=https://raw.githubusercontent.com/MaastrichtU-IDS/food-claims-kg/main/urls.yml

## Question answering

Using SPARQL queries

### 1. What are claims related to a specific food/food component’s health effect? 

Example: List all claims related to the health effect of “Calcium”

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>
PREFIX mp: <http://purl.org/mp/>

SELECT  ?claim ?claim_label
WHERE {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?mp mp:represents ?hfe .
    ?hfe fhcp:hasPhenotype ?pheno .
    ?hfe fhcp:hasFood ?food .
    FILTER (?food = <https://foodb.ca/compounds/FDB003513>)
}
```

> <a href="https://yasgui.triply.cc/#query=PREFIX%20fhcp%3A%20%3Chttp%3A%2F%2Fwww.w3id.org%2Ffoodhkg%2Fprops%2F%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0A%0ASELECT%20%20%3Fclaim%20%3Fclaim_label%0AWHERE%20%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fmp%20mp%3Arepresents%20%3Fhfe%20.%0A%20%20%20%20%3Fhfe%20fhcp%3AhasPhenotype%20%3Fpheno%20.%0A%20%20%20%20%3Fhfe%20fhcp%3AhasFood%20%3Ffood%20.%0A%20%20%20%20FILTER%20(%3Ffood%20%3D%20%3Chttps%3A%2F%2Ffoodb.ca%2Fcompounds%2FFDB003513%3E)%0A%7D&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 2. What are the supporting statements about a food health claim?

Example: List all supporting statements for the claim "Calcium contributes to normal blood clotting". 

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>
PREFIX mp: <http://purl.org/mp/>

SELECT ?claim ?claim_label ?statement ?statement_label
WHERE {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?statement mp:supports ?claim .
    ?statement rdfs:label ?statement_label .
    FILTER (?claim_label = "Calcium contributes to normal muscle function")
}
```

> <a href='https://yasgui.triply.cc/#query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20fhcp%3A%20%3Chttp%3A%2F%2Fwww.w3id.org%2Ffoodhkg%2Fprops%2F%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0A%0ASELECT%20%3Fclaim%20%3Fclaim_label%20%3Fstatement%20%3Fstatement_label%0AWHERE%20%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fstatement%20mp%3Asupports%20%3Fclaim%20.%0A%20%20%20%20%3Fstatement%20rdfs%3Alabel%20%3Fstatement_label%20.%0A%20%20%20%20FILTER%20(%3Fclaim_label%20%3D%20%22Calcium%20contributes%20to%20normal%20muscle%20function%22)%0A%7D&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>

### 3. Which references have the EFSA opinions used for supporting a food health claim?

Example: List all references listed in the EFSA opinion for the claim "Calcium contributes to normal blood clotting". 

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mp: <http://purl.org/mp/>

SELECT  ?claim ?claim_label ?reference ?reference_label
WHERE {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?statement mp:supports ?claim .
    ?reference mp:supports ?statement .
    ?reference rdfs:label ?reference_label .
    ?reference rdf:type mp:Reference .
    FILTER (?claim_label = "Calcium contributes to normal blood clotting")
}
```

> <a href='https://yasgui.triply.cc/#query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0A%0ASELECT%20%20%3Fclaim%20%3Fclaim_label%20%3Freference%20%3Freference_label%0AWHERE%20%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fstatement%20mp%3Asupports%20%3Fclaim%20.%0A%20%20%20%20%3Freference%20mp%3Asupports%20%3Fstatement%20.%0A%20%20%20%20%3Freference%20rdfs%3Alabel%20%3Freference_label%20.%0A%20%20%20%20%3Freference%20rdf%3Atype%20mp%3AReference%20.%0A%20%20%20%20FILTER%20(%3Fclaim_label%20%3D%20%22Calcium%20contributes%20to%20normal%20blood%20clotting%22)%0A%7D&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>

### 4. What are the number of references listed for each claim.

Example: List all claims and the numbers of their references (Some of them have “0” reference.)

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mp: <http://purl.org/mp/>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>

SELECT ?claim ?claim_label (count(?reference ) as ?number_of_claims)
WHERE  {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?statement mp:supports ?claim .
    OPTIONAL {
    ?reference mp:supports ?statement .
    ?reference rdfs:label ?reference_label .
    ?reference rdf:type mp:Reference . 
    }
}
GROUP BY ?claim ?claim_label
```

> <a href="https://yasgui.triply.cc/#query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0APREFIX%20fhcp%3A%20%3Chttp%3A%2F%2Fwww.w3id.org%2Ffoodhkg%2Fprops%2F%3E%0A%0ASELECT%20%3Fclaim%20%3Fclaim_label%20(count(%3Freference%20)%20as%20%3Fnumber_of_claims)%0AWHERE%20%20%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fstatement%20mp%3Asupports%20%3Fclaim%20.%0A%20%20%20%20OPTIONAL%20%7B%0A%20%20%20%20%3Freference%20mp%3Asupports%20%3Fstatement%20.%0A%20%20%20%20%3Freference%20rdfs%3Alabel%20%3Freference_label%20.%0A%20%20%20%20%3Freference%20rdf%3Atype%20mp%3AReference%20.%20%0A%20%20%20%20%7D%0A%7D%0AGROUP%20BY%20%3Fclaim%20%3Fclaim_label&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 5. Which publication was most frequently cited in the EFSA opinions?

Example: List the most frequently cited publications in the EFSA opinions.

```SPARQL
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mp: <http://purl.org/mp/>

SELECT ?reference ?reference_label (count(?claim ) as ?number_of_claims)
WHERE  {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?statement mp:supports ?claim .
    ?reference mp:supports ?statement .
    ?reference rdfs:label ?reference_label .
    ?reference rdf:type mp:Reference . 
}
GROUP BY ?reference ?reference_label
```

> <a href="https://yasgui.triply.cc/#query=PREFIX%20fhcp%3A%20%3Chttp%3A%2F%2Fwww.w3id.org%2Ffoodhkg%2Fprops%2F%3E%0APREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0A%0ASELECT%20%3Freference%20%3Freference_label%20(count(%3Fclaim%20)%20as%20%3Fnumber_of_claims)%0AWHERE%20%20%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fstatement%20mp%3Asupports%20%3Fclaim%20.%0A%20%20%20%20%3Freference%20mp%3Asupports%20%3Fstatement%20.%0A%20%20%20%20%3Freference%20rdfs%3Alabel%20%3Freference_label%20.%0A%20%20%20%20%3Freference%20rdf%3Atype%20mp%3AReference%20.%20%0A%7D%0AGROUP%20BY%20%3Freference%20%3Freference_label&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 6. What are health claims associated with phenotypes/diseases?

Example: List all health claims associated with "Normal energy-yielding metabolism"  phenotype. 

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX mp: <http://purl.org/mp/>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>

SELECT ?claim_label ?pheno_label ?pheno 
{
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?mp mp:represents ?hfe .
    ?hfe fhcp:hasPhenotype ?pheno .
    ?pheno rdfs:label ?pheno_label .
    ?hfe fhcp:hasFood ?food .
    FILTER (?pheno_label = "Normal energy-yielding metabolism")
}
```

> <a href='https://yasgui.triply.cc/#query=PREFIX%20rdfs%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F2000%2F01%2Frdf-schema%23%3E%0APREFIX%20rdf%3A%20%3Chttp%3A%2F%2Fwww.w3.org%2F1999%2F02%2F22-rdf-syntax-ns%23%3E%0APREFIX%20mp%3A%20%3Chttp%3A%2F%2Fpurl.org%2Fmp%2F%3E%0APREFIX%20fhcp%3A%20%3Chttp%3A%2F%2Fwww.w3id.org%2Ffoodhkg%2Fprops%2F%3E%0A%0ASELECT%20%3Fclaim_label%20%3Fpheno_label%20%3Fpheno%20%0A%7B%0A%20%20%20%20%3Fmp%20mp%3Aargues%20%20%3Fclaim.%0A%20%20%20%20%3Fclaim%20rdfs%3Alabel%20%3Fclaim_label%20.%0A%20%20%20%20%3Fmp%20mp%3Arepresents%20%3Fhfe%20.%0A%20%20%20%20%3Fhfe%20fhcp%3AhasPhenotype%20%3Fpheno%20.%0A%20%20%20%20%3Fpheno%20rdfs%3Alabel%20%3Fpheno_label%20.%0A%20%20%20%20%3Fhfe%20fhcp%3AhasFood%20%3Ffood%20.%0A%20%20%20%20FILTER%20(%3Fpheno_label%20%3D%20%22Normal%20energy-yielding%20metabolism%22)%0A%7D&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers=%7B%7D&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>

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

