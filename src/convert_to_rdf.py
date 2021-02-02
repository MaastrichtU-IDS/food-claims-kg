# -*- coding: utf-8 -*-
"""Convert_FHClaimToRDF.ipynb
Convert Food Health Claims to RDF Knowledge Graph
"""
from __future__ import print_function

# import for RDF knowledge graph
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
import json
import requests

# To query UMLS API
from umls_authentication import UmlsAuthentication
import argparse
import time

UMLS = Namespace("https://identifiers.org/umls:")
FOODHKG_INST = Namespace("http://www.w3id.org/foodhkg/Instances/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
RDF = Namespace("http://www.w3.org/1999/02/22-rdf-syntax-ns#")
OWL = Namespace("http://www.w3.org/2002/07/owl#")
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

phenotypes_hash = {}
umls_api_found_count = 0


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
        "http://www.informatics.jax.org/vocab/gene_ontology/GO:", "http://identifiers.org/go/")
    return term.strip()


def get_phenotype_curie(phenotype_uri):
    """Extract Phenotypes CURIE from the URI
    """
    if '/MEDDRA/' in phenotype_uri:
        phenotype_id = phenotype_uri.split("/MEDDRA/", 1)[1]
        return 'MEDDRA:' + phenotype_id
    if '/HP:' in phenotype_uri:
        phenotype_id = phenotype_uri.split("/HP:", 1)[1]
        return 'HP:' + phenotype_id
    # if '/GO:' in phenotype_uri:
    #     phenotype_id = phenotype_uri.split("/GO:",1)[1]
    #     return 'GO:' + phenotype_id


def add_umls_mappings():
    """This function will add owl:sameAs mappings to the UMLS.
    It first try using the Translator NodeNormalization API
    If we dont find a UMLS identifier as preferred ID
    Then we query the UMLS API using the labels to find UMLS id
    """
    print(str(len(phenotypes_hash.keys())) +
          ' MEDDRA and HP identifiers to resolve to UMLS')
    # Resolve CURIEs to UMLS using Translator NodeNormalization
    resolve_curies = requests.get('https://nodenormalization-sri.renci.org/get_normalized_nodes',
                                  params={'curie': phenotypes_hash.keys()})

    # Query OpenPredict API with OMIM IDs
    resp = resolve_curies.json()
    print(resp)
    matchCount = 0
    umls_api_found_count = 0
    for resolve_id, ids in resp.items():
        if ids and ids['id']['identifier'].startswith('UMLS:'):
            matchCount += 1
            # print('Got a match for ' + resolve_id + ' => ' + ids['id']['identifier'])
            # print(ids)
            # Create owl:sameAs to UMLS
            dataset.add((URIRef(phenotypes_hash[resolve_id]['uri']),
                         OWL['sameAs'], UMLS[ids['id']['identifier'].replace('UMLS:', '')]))
        else:
            print('\nNo match for ' + resolve_id +
                  ' in Translator API, trying UMLS API with label: ' + phenotypes_hash[resolve_id]['label'])
            umls_id = search_term_in_umls_api(
                phenotypes_hash[resolve_id]['label'])
            print("URI found with UMLS API:")
            print(umls_id)
            if umls_id:
                umls_api_found_count += 1
                dataset.add((URIRef(phenotypes_hash[resolve_id]['uri']),
                             OWL['sameAs'], UMLS[umls_id]))

    print(str(matchCount) + ' matches to UMLS on ' +
          str(len(phenotypes_hash.keys())) + ' id searched in Translator API')
    print(str(umls_api_found_count) + ' matches to UMLS on ' +
          str(len(phenotypes_hash.keys())) + ' id searched with UMLS API')


def search_term_in_umls_api(search_string):
    """This function will query the UMLS API to resolve labels.
    It uses the umls_authentication.py file
    """
    apikey = os.environ['UMLS_APIKEY']
    if apikey:
        # Sleep 2s between each API calls
        time.sleep(2)
        version = 'current'
        uri = "https://uts-ws.nlm.nih.gov"
        content_endpoint = "/rest/search/"+version
        # get at ticket granting ticket for the session
        AuthClient = UmlsAuthentication(apikey)
        tgt = AuthClient.gettgt()
        pageNumber = 0

        while True:
            # generate a new service ticket for each page if needed
            ticket = AuthClient.getst(tgt)
            pageNumber += 1
            query = {'string': search_string,
                     'ticket': ticket, 'pageNumber': pageNumber}
            # query['includeObsolete'] = 'true'
            # query['includeSuppressible'] = 'true'
            # query['returnIdType'] = "sourceConcept"
            # query['sabs'] = "SNOMEDCT_US"
            r = requests.get(uri+content_endpoint, params=query)
            r.encoding = 'utf-8'
            items = json.loads(r.text)
            jsonData = items["result"]
            # print (json.dumps(items, indent = 4))

            print("Results for page " + str(pageNumber))
            for result in jsonData["results"]:
                try:
                    print("ui: " + result["ui"])
                    print("name: " + result["name"])
                    print("Source Vocabulary: " + result["rootSource"])
                except:
                    NameError
                try:
                    print("uri: " + result["uri"])
                    # Troncate after /CUI/ to get ID
                    # https://uts-ws.nlm.nih.gov/rest/content/2020AA/CUI/C0027794
                    return result["uri"][result["uri"].find('/CUI/')+5:]
                except:
                    NameError
            # Either our search returned nothing, or we're at the end
            if jsonData["results"][0]["ui"] == "NONE":
                break
    else:
        print("No UMLS APIKEY found: skipping UMLS API search. Set it as environment variable UMLS_APIKEY")


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


def createFoodProp(dataset, food_uri, food_label, food_type, food_source,
                   rec_dose_unit, rec_dose_value, rec_freq):
    """
    Create triples related to food properties
    """
    food_type = food_type.strip()
    if food_type != '':
        dataset.add((food_uri, RDF['type'],
                     FOODHKG_CLS[food_type]))
        dataset.add((food_uri, RDFS['label'],  Literal(food_label)))
        dataset.add((food_uri, FOODHKG_PROPS['source'],  Literal(food_source)))
        hash_text = ''
        if str(food_source) != 'nan':
            hash_text += str(food_source)
        if str(rec_dose_unit) != 'nan':
            hash_text += str(rec_dose_unit)
        if str(rec_dose_value) != 'nan':
            hash_text += str(rec_dose_value)
        if str(rec_freq) != 'nan':
            hash_text += str(rec_freq)

        rec_dose_schedule_uri = FOODHKG_INST[get_hash(hash_text)]

        dataset.add(
            (food_uri, SCHEMA['recommendedIntake'],  rec_dose_schedule_uri))
        dataset.add(
            (rec_dose_schedule_uri, RDF['type'],  SCHEMA['DoseSchedule']))
        if str(rec_dose_unit) != 'nan':
            dataset.add(
                (rec_dose_schedule_uri, SCHEMA['doseUnit'],  Literal(rec_dose_unit)))
        if str(rec_dose_value) != 'nan':
            dataset.add(
                (rec_dose_schedule_uri, SCHEMA['doseValue'],  Literal(rec_dose_value)))
        if str(rec_freq) != 'nan':
                (rec_dose_schedule_uri, SCHEMA['frequency'],  Literal(rec_freq)))


def createFoodObject(dataset, row):
    """
    Create food URI and triples related to food properties
    """
    # food_amount = row['NEW Food Matrix']
    # print(food_amount)
    # rec_dose_unit = ''
    # rec_dose_value = ''
    # rec_freq = ''
    # food_source = ''
    # if food_amount.strip() != '':
    #     fp_text = food_amount.strip().split('\n')
    #     for fp in fp_text:
    #         fp_tuple = fp.split(': ')
    #         if len(fp_tuple) != 2:
    #             continue
    #         # print(tp_tuple)
    #         key = fp_tuple[0]
    #         value = fp_tuple[1].strip()
    #         if key == 'Matrix':
    #             food_source = value
    #         if key == '- Unit':
    #             rec_dose_unit = value
    #             if 'day' in value:
    #                 rec_freq = 'daily'
    #             else:
    #                 rec_freq = 'per meal'
    #         if key == '- Value' or key == 'Value':
    #             rec_dose_value = value

    # print(food_label, food_onto_term, food_type, food_source,
    #       rec_dose_unit, rec_dose_value, rec_freq)

    food_onto_term = str(row['Food Ontology Term'])
    food_label = row['Food']
    food_type = row['NEW Food Type']
    food_amount = row['NEW Food Matrix']
    food_source = food_amount.split('\n')[0].replace('Matrix', '')
    dose_unit = row['Unit']
    dose_value = row['Value']
    dose_freq = row['Frequency']
    fooduri_list = []
    # if there is no ontology term define for this food, create one
    if food_onto_term == 'nan':
        fooduri = FOODHKG_INST[get_hash(food_label)]
        createFoodProp(dataset, fooduri, food_label, food_type, food_source,
                       dose_unit, dose_value, dose_freq)
        fooduri_list.append(fooduri)
    else:
        for fooduri in food_onto_term.split(';'):
            fooduri = fooduri.strip()
            if fooduri == '':
                continue
            fooduri = URIRef(fooduri)
            createFoodProp(dataset, fooduri, food_label, food_type, food_source,
                           dose_unit, dose_value, dose_freq)
            fooduri_list.append(fooduri)
    return fooduri_list


def createTargetPopulationObject(dataset, row):
    tp_onto_term = row['Target population ontology term']
    if tp_onto_term == '':
        return None

    tp_prop = {}
    tp_text = tp_onto_term.split('\n')
    social_con = ''
    age = ''
    sex = ''
    condition = ''
    tp_label = row['Target population']
    print(tp_text, tp_label)
    for tp in tp_text:
        tp_tuple = tp.split(': ')
        if len(tp_tuple) != 2:
            continue
        # print(tp_tuple)
        key = tp_tuple[0]
        value = tp_tuple[1].strip()
        if key == 'socialContext':
            social_con = value
        elif key == 'age':
            age = value
        elif key == 'sex':
            sex = value
        elif key == 'condition':
            condition = value
        tp_prop[key] = value

    if tp_onto_term == 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C18241':
        targetPopUri = URIRef(
            'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C18241')
    else:
        targetPopUri = FOODHKG_INST[get_hash(tp_onto_term)]

    dataset.add((targetPopUri, RDFS['label'], Literal(tp_label)))
    print('Target Population', social_con, age, sex, condition)
    for pred, obj in tp_prop.items():
        if not obj.startswith('http'):
            dataset.add((targetPopUri, PICO[pred], Literal(obj)))
        else:
            dataset.add((targetPopUri, FOODHKG_PROPS[pred], URIRef(obj)))

    return targetPopUri


def createPhenotypeObject(dataset, pheno_onto_term, pheno_label):
    if str(pheno_onto_term) == 'nan':
        pheno_uri = FOODHKG_INST[get_hash(pheno_label)]
    else:
        for pheno_uri in pheno_onto_term.split(';'):
            pheno_uri = pheno_uri.strip()
            if pheno_uri == '':
                continue
            # pheno_uri = normalize(pheno_uri)
            pheno_uri = URIRef(pheno_uri)
    dataset.add((pheno_uri, RDF['type'],  FOODHKG_CLS['Phenotype']))
    dataset.add((pheno_uri, RDFS['label'],  Literal(pheno_label)))

    phenotypes_hash[get_phenotype_curie(pheno_uri)] = {
        'uri': pheno_uri, 'label': pheno_label}
    return pheno_uri


def createHealthEffectObject(dataset, effect_type):
    hr_type = FOODHKG_INST[get_hash(effect_type)]
    dataset.add((hr_type, RDF['type'],  FOODHKG_CLS['FoodHealthEffect']))
    dataset.add((hr_type, RDFS['label'],  Literal(effect_type)))
    return hr_type


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

    # create Health Effect object
    effect_type = row['Relationship-effect']
    print('Phenotype', row['Phenotype'], 'Effect', effect_type)
    hr_type = createHealthEffectObject(dataset, effect_type)
    dataset.add((hr_subj, RDF['type'],  hr_type))

    # create Phenotype object
    ph_onto_term = row['Phenotype Ontology Term']
    pheno_label = row['Phenotype']
    pheno_uri = createPhenotypeObject(dataset, ph_onto_term, pheno_label)
    dataset.add((hr_subj, FOODHKG_PROPS['hasPhenotype'],  pheno_uri))

    # create Food object
    fooduri_list = createFoodObject(dataset, row)
    # link food object to Health Effect object
    for food_uri in fooduri_list:
        dataset.add((hr_subj, FOODHKG_PROPS['hasFood'],  food_uri))

    # create Target Population object
    targetPopUri = createTargetPopulationObject(dataset, row)
    # link Target Population object to Health Effect object
    if targetPopUri != None:
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
                # print(ref)
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
    # add_umls_mappings()

    dataset.serialize('data/output/food_health_kg.ttl', format='turtle')
