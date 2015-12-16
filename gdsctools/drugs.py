"""

Small functionalities to retrive chembl/chemspider identifiers
based on a drug name

"""

from easydev import Progress


__all__ = ["extract_drug_identifiers", "ChemSpiderSearch"]


def extract_drug_identifiers(drug_lists):
    drug_ids = []
    for drug in drug_lists:
        drug = str(drug)
        if drug.lower().startswith('drug_'):
            drug_ids.append(drug.split("_")[1])
        else:
            drug_ids.append(drug.split("_")[0])
    drug_ids = [int(x) for x in drug_ids]
    return drug_ids


class ChemSpiderSearch(object):
    """This class uses ChemSpider to identify drug name


    c = ChemSpiderSearch()
    c.search_in_chemspider()
    c.search_from_smile_inchembl()
    df = c.find_chembl_ids()

    It happends that most of public names can be found
    and almost none of non-public are not found. As expected.




    """
    def __init__(self, drug_list):

        from bioservices.chemspider import ChemSpider
        from bioservices import ChEMBL

        self._chembl = ChEMBL(cache=True)
        self._cs = ChemSpider(cache=True)
        self._cs_find = self._cs.find
        self._cs_get = self._cs.GetExtendedCompoundInfo

        self.drugs = sorted(set(drug_list))

    def find_chembl_ids(self):
        # don't know how to search for a chembl id given the drug name...
        # so we use chemspider
        #self.search_in_chemspider()

        # but chemspider returns molecular information (not chembl id)
        # so given the smile string, we look back in chembl for valid entries
        #self.search_from_smile_inchembl()

        # finally, get the chembl identifiers
        drugs = []
        chembl_ids = []
        chemspider_ids = []

        for drug in self.drugs:

            try:
                entry = self.results_chembl[drug]

                ids = ",".join([x['chemblId'] for x in entry])
                drugs.append(drug)
                chembl_ids.append(ids)
            except:
                print('skipping' + drug)
                continue

            ids = ",".join([str(x) for x in self.results[drug]])
            chemspider_ids.append(ids)

        import pandas as pd
        df = pd.DataFrame([drugs, chembl_ids, chemspider_ids],
                index=['DRUG_NAME','CHEMBL_ID','CHEMSPIDER_ID'])
        df = df.T
        return df

    def search_in_chemspider(self):
        N = len(self.drugs)

        pb = Progress(N)
        self.results = {}
        for i in range(0, N):
            drug = self.drugs[i]
            try:
                res = self._cs_find(drug)
            except:
                print drug, 'failed'
                res = []
            self.results[drug] = res
            pb.animate(i+1)


    def search_from_smile_inchembl(self):

        N = len(self.drugs)

        pb= Progress(N)
        self.results_chembl = {}
        for i in range(0, N):
            drug = self.drugs[i]
            self.results_chembl[drug] = []

            if self.results[drug]:
                for chemspider_id in self.results[drug]:
                    chemspider_entry = self._cs_get(chemspider_id)
                    smile = chemspider_entry['smiles']
                    # now search in chembl
                    res_chembl = self._chembl.get_compounds_by_SMILES(smile)
                    try:
                        res_chembl['compounds']
                        self.results_chembl[drug].extend(res_chembl['compounds'])
                    except:
                        pass

            pb.animate(i+1)

