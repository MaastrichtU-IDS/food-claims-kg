A RDF knowledge graph for food health claims accessible at https://graphdb.dumontierlab.com/repositories/FoodHealthClaimsKG

## Question answering

Using SPARQL queries

### 1. What are claims related to a specific food/food component’s health effect? 

Example: List all claims related to the health effect of “Calcium”

```SPARQL
PREFIX mp: <http://purl.org/mp/>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
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

> <a href="https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX fhcp%3A  PREFIX rdfs%3A  SELECT  %3Fclaim %3Fclaim_label {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fmp mp%3Arepresents %3Fhfe .    %3Fhfe fhcp%3AhasPhenotype %3Fpheno .    %3Fhfe fhcp%3AhasFood %3Ffood .    FILTER (%3Ffood %3D ) }&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 2. What are the supporting statements about a food health claim?

Example: List all supporting statements for the claim "Calcium contributes to normal blood clotting". 

```SPARQL
SELECT  ?claim ?claim_label ?statement ?statement_label
WHERE {
    ?mp mp:argues  ?claim.
    ?claim rdfs:label ?claim_label .
    ?statement mp:supports ?claim .
    ?statement rdfs:label ?statement_label .
    FILTER (?claim_label = "Calcium contributes to normal muscle function")
}
```

> <a href='https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX fhcp%3A  PREFIX rdfs%3A  PREFIX rdf%3A  SELECT  %3Fclaim %3Fclaim_label %3Fstatement %3Fstatement_label {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fstatement mp%3Asupports %3Fclaim .    %3Fstatement rdfs%3Alabel %3Fstatement_label .    FILTER (%3Fclaim_label %3D "Calcium contributes to normal muscle function") }&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>

### 3. Which references have the EFSA opinions used for supporting a food health claim?

Example: List all references listed in the EFSA opinion for the claim "Calcium contributes to normal blood clotting". 

```SPARQL
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
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

> <a href='https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX fhcp%3A  PREFIX rdfs%3A  PREFIX rdf%3A  SELECT  %3Fclaim %3Fclaim_label %3Freference %3Freference_label {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fstatement mp%3Asupports %3Fclaim .    %3Freference mp%3Asupports %3Fstatement .    %3Freference rdfs%3Alabel %3Freference_label .    %3Freference rdf%3Atype mp%3AReference .    FILTER (%3Fclaim_label %3D "Calcium contributes to normal blood clotting") }&endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>

### 4. What are the number of references listed for each claim.

Example: List all claims and the numbers of their references (Some of them have “0” reference.)

```SPARQL
PREFIX mp: <http://purl.org/mp/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
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

> <a href="https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX rdfs%3A  PREFIX rdf%3A  SELECT %3Fclaim %3Fclaim_label (count(%3Freference ) as %3Fnumber_of_claims) WHERE  {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fstatement mp%3Asupports %3Fclaim .    OPTIONAL {    %3Freference mp%3Asupports %3Fstatement .    %3Freference rdfs%3Alabel %3Freference_label .    %3Freference rdf%3Atype mp%3AReference .     } } GROUP BY %3Fclaim %3Fclaim_label  &endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 5. Which publication was most frequently cited in the EFSA opinions?

Example: List the most frequently cited publications in the EFSA opinions.

```SPARQL
PREFIX mp: <http://purl.org/mp/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
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

> <a href="https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX rdfs%3A  PREFIX rdf%3A  SELECT %3Freference %3Freference_label (count(%3Fclaim ) as %3Fnumber_of_claims) WHERE  {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fstatement mp%3Asupports %3Fclaim .    %3Freference mp%3Asupports %3Fstatement .    %3Freference rdfs%3Alabel %3Freference_label .    %3Freference rdf%3Atype mp%3AReference .  } GROUP BY %3Freference %3Freference_label  &endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table">Execute the query on YASGUI</a>

### 6. What are health claims associated with phenotypes/diseases?

Example: List all health claims associated with "Normal energy-yielding metabolism"  phenotype. 

```SPARQL
PREFIX mp: <http://purl.org/mp/>
PREFIX fhcp: <http://www.w3id.org/foodhkg/props/>
PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
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

> <a href='https://yasgui.triply.cc/#query=PREFIX mp%3A  PREFIX fhcp%3A  PREFIX rdfs%3A  PREFIX rdf%3A  SELECT %3Fclaim_label %3Fpheno_label %3Fpheno  {    %3Fmp mp%3Aargues  %3Fclaim.    %3Fclaim rdfs%3Alabel %3Fclaim_label .    %3Fmp mp%3Arepresents %3Fhfe .    %3Fhfe fhcp%3AhasPhenotype %3Fpheno .    %3Fpheno rdfs%3Alabel %3Fpheno_label .    %3Fhfe fhcp%3AhasFood %3Ffood .    FILTER (%3Fpheno_label %3D "Normal energy-yielding metabolism") } &endpoint=https%3A%2F%2Fgraphdb.dumontierlab.com%2Frepositories%2FFoodHealthClaimsKG&requestMethod=POST&tabTitle=Query&headers={}&contentTypeConstruct=text%2Fturtle&contentTypeSelect=application%2Fsparql-results%2Bjson&outputFormat=table'>Execute the query on YASGUI</a>