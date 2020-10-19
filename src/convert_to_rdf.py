# -*- coding: utf-8 -*-
"""Convert_FHClaimToRDF.ipynb
Convert Food Health Claims to RDF Knowledge Graph
"""


# import for RDF knowledge
from rdflib import Graph, URIRef, Literal, RDF, ConjunctiveGraph
from rdflib import Namespace
from rdflib import Dataset

import pandas as pd
import os
import re

import io
from io import BytesIO
import hashlib
import base64
import re

UMLS = Namespace("http://www.w3id.org/umls/")
FOODHKG_INST = Namespace("http://www.w3id.org/foodhkg/Instances/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
BASE = Namespace("http://www.w3id.org/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
SCHEMA = Namespace("http://schema.org/")
MP = Namespace("http://purl.org/mp/")
NP = Namespace("http://www.nanopub.org/nschema#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
FOODHKG_PROPS = Namespace("http://www.w3id.org/foodhkg/props/")
FOODHKG_CLS = Namespace("http://www.w3id.org/foodhkg/classes/")
DOI = Namespace("http://doi.org/")
PICO = Namespace("http://data.cochrane.org/ontologies/pico/")


def convert_json(dataset):
    data_json = {'nodes': [], 'edges': []}
    for n in dataset.all_nodes():
        print(n)
        if isinstance(n, URIRef):
            data_json['nodes'].append({'id': str(n)})
    i = 0
    for s, p, o in dataset:
        print(s, p, o)
        if isinstance(o, URIRef):
            data_json['edges'].append(
                {'id': str(i), 'source': str(s), 'target': str(o)})
            i += 1
    return data_json


def get_hash(s):
    s1 = hashlib.sha256(s.encode('utf-8')).digest()
    return re.sub(r'=', '', base64.b64encode(s1, b'-_').decode('utf-8'))


def normalize(term):
    term = term.replace(
        "http://www.informatics.jax.org/vocab/gene_ontology/GO:", "https://bio2rdf.org/go/")
    return term.strip()


def createPhenotypeRelTriples(dataset, hr_subj, pheno_uri, pheno_label):
    dataset.add((pheno_uri, RDF['type'],  FOODHKG_CLS['Phenotype']))
    dataset.add((pheno_uri, RDFS['label'],  Literal(pheno_label)))
    dataset.add((hr_subj, FOODHKG_PROPS['hasPhenotype'],  pheno_uri))
    return dataset


def createFoodRelTriples(dataset, hr_subj, fooduri, food_type, food_label):
    dataset.add((hr_subj, FOODHKG_PROPS['hasFood'],  fooduri))
    food_type = food_type.strip()
    if food_type != '':
        dataset.add((fooduri, RDF['type'],
                     FOODHKG_CLS[food_type]))
        dataset.add((fooduri, RDFS['label'],  Literal(food_label)))
    return dataset


def createSupportingRefTriples(sdataset, supp_subj, suppref_subj, suppref_doi, ref_label):
    pred = MP['supports']
    dataset.add((suppref_subj, pred, supp_subj))
    dataset.add((suppref_subj, RDF['type'], MP['Reference']))
    dataset.add((suppref_subj, RDFS['label'],  Literal(ref_label)))
    if "no DOI" not in suppref_doi:
        suppref_doi = suppref_doi.replace(' ', '')
        dataset.add(
            (suppref_subj, DCAT['identifier'],  DOI[suppref_doi]))
    return dataset


def turn_into_mp(row, dataset):
    # Claim
    claim_subj = FOODHKG_INST[get_hash(row['Claim'])]
    pred = RDF['type']
    obj = URIRef('http://purl.org/mp/Claim')
    dataset.add((claim_subj, pred, obj))
    # define the claim label
    dataset.add((claim_subj, RDFS['label'],  Literal(row['Claim'])))
    opinion_subj = FOODHKG_INST[get_hash(row['EFSA Opinion Reference'])]
    dataset.add((opinion_subj, FOODHKG_PROPS['advises'],  claim_subj))
    dataset.add((opinion_subj, RDF['type'],  FOODHKG_CLS['Opinion']))

    # micropublication (a MP conssists of claim, statement, representation of fine-grained NP)
    # each ESFA opinion is a MP
    mp_subj = FOODHKG_INST[get_hash(
        row['EFSA Opinion Reference']+row['Claim'])]
    dataset.add((mp_subj, RDF['type'], MP['Micropublication']))
    # each MP argues a claim
    dataset.add((mp_subj, MP['argues'],  claim_subj))

    # to define fine-granular facts (triples facts) using Nanopublication (NP)
    hr_subj = FOODHKG_INST[get_hash(
        row['Health relationship']+row['Phenotype']+row['Food'])]
    dataset.add((mp_subj, MP['represents'],  hr_subj))
    # np_subj = FOODHKG_INST[get_hash(row['Health relationship']+row['EFSA Opinion Reference'])]
    # dataset.add((np_subj, RDF['type'],  NP['Nanopublication']))
    # Assertions for NP
    # dataset.add((np_subj, NP['hasAssertion'],  hr_subj))
    dataset.add((hr_subj, RDFS['label'],  Literal(row['Health relationship'])))
    # sub type of food health effect/categorization
    hr_type = FOODHKG_INST[get_hash(row['Health relationship'])]
    dataset.add((hr_subj, RDF['type'],  hr_type))
    dataset.add((hr_type, RDF['type'],  FOODHKG_CLS['FoodHealthEffect']))
    dataset.add((hr_type, RDFS['label'],  Literal(row['Health relationship'])))

    if str(row['Phenotype Ontology Term']) == 'nan':
        pheno_uri = FOODHKG_INST[get_hash(row['Phenotype'])]
        dataset = createPhenotypeRelTriples(
            dataset, hr_subj, pheno_uri, row['Phenotype'])
    else:
        for pheno_uri in row['Phenotype Ontology Term'].split(';'):
            pheno_uri = pheno_uri.strip()
            if pheno_uri == '':
                continue
            # pheno_uri = normalize(pheno_uri)
            pheno_uri = URIRef(pheno_uri)
            dataset = createPhenotypeRelTriples(
                dataset, hr_subj, pheno_uri, row['Phenotype'])

    if str(row['Food Ontology Term']) == 'nan':
        fooduri = FOODHKG_INST[get_hash(row['Food'])]
        dataset = createFoodRelTriples(
            dataset, hr_subj, fooduri, row['Food Type'], row['Food'])
    else:
        for fooduri in row['Food Ontology Term'].split(','):
            fooduri = fooduri.replace(' ', '')
            if fooduri == '':
                continue
            fooduri = URIRef(fooduri)
            dataset = createFoodRelTriples(
                dataset, hr_subj, fooduri, row['Food Type'], row['Food'])

    if row['Target population'] != '':
        if row['Target population ontology term'] != '':
            if row['Target population ontology term'] == 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C18241':
                targetPopUri = URIRef(
                    'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C18241')
            else:
                targetPopUri = FOODHKG_INST[get_hash(
                    row['Target population ontology term'])]
                tp_text = row['Target population ontology term'].split('\n')
                for tp in tp_text:
                    tp_tuple = tp.split(': ')
                    if len(tp_tuple) != 2:
                        continue
                    print(tp_tuple)
                    pred = tp_tuple[0]
                    obj = tp_tuple[1].strip()
                    if not obj.startswith('http'):
                        dataset.add((targetPopUri, PICO[pred], Literal(obj)))
                    else:
                        dataset.add(
                            (targetPopUri, FOODHKG_PROPS[pred], URIRef(obj)))
        dataset.add((targetPopUri, RDFS['label'],
                     Literal(row['Target population'])))
        dataset.add(
            (hr_subj, FOODHKG_PROPS['hasTargetPopulation'],  targetPopUri))

    for i in range(1, 9):
        if str(row[f'Supporting Evidence Text {i}']) == 'nan':
            continue
        supp_subj = FOODHKG_INST[get_hash(
            row[f'Supporting Evidence Text {i}'])]

        pred = MP['supports']
        # statemtent supports the claim
        dataset.add((supp_subj, pred,  claim_subj))
        # is type of Statement
        dataset.add((supp_subj, RDF['type'], MP['Statement']))
        # label of Statement
        dataset.add((supp_subj, RDFS['label'],  Literal(
            row[f'Supporting Evidence Text {i}'])))

        suppRef = row[f'Supporting Evidence Reference {i}']
        # if references for statement exist
        if str(suppRef) != 'nan' and len(suppRef) > 3 and suppRef.lower() != "no reference":
            refs = suppRef.split(';')
            for ref in refs:
                print(ref)
                ref_tuple = ref.split(':')
                suppref_text = ref_tuple[0]
                suppref_doi = ref_tuple[1]
                suppref_subj = FOODHKG_INST[get_hash(suppref_text)]
                dataset = createSupportingRefTriples(dataset,
                                                     supp_subj, suppref_subj, suppref_doi, ref)

    return dataset


if __name__ == '__main__':
    df = pd.read_excel('data/food-claims-kg.xlsx',
                       sheet_name='13. Authorised')

    dataset = Dataset()
    for index, row in df.iterrows():
        print('-', row['Supporting Evidence Reference 1'], '-',
              row['Status'], ':', row['Health relationship'])
        if row['Status'] == 'Finished':
            dataset = turn_into_mp(row, dataset)

    df = pd.read_excel('data/food-claims-kg.xlsx',
                       sheet_name='14. Authorised')

    for index, row in df.iterrows():
        if row['Finished?'] == 'Finished':
            dataset = turn_into_mp(row, dataset)

    dataset.serialize('data/output/food_health_kg.ttl', format='turtle')