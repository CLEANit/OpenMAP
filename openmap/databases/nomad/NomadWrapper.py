import numpy as np
import pandas as pd

from nomad import client, config
from nomad.metainfo import units
from nomad.client import ArchiveQuery
from mendeleev import element

from openmap.computing.log import logger

# based partly on https://nomad-lab.eu/index.php?page=AItutorials

class NomadWrapper(object):
    def __init__(self,):
        self.query={'domain':'dft'}
        config.client.url = 'http://nomad-lab.eu/prod/rae/api'
        pass
    
    def search_params(self,atoms, only_atoms=False, searchable_quantities = [], crystal_system ='', dft_codeName='',band_gap=[], compound_type=''):
        """
        :param atoms: array of strings of elements ex: ['O', 'V']
        :param crystal_system: string. "Compound type" on Nomad online search. One of 'binary', 'ternary', 
                            'quaternary', 'quinary', 'sexinary', ...
        :param 
        """
        if only_atoms:

            self.query['only_atoms'] = atoms
        else:
            self.query['atoms'] = atoms
        
        if crystal_system is not '':
            self.query['dft.compound_type'] = crystal_system
        if dft_codeName is not '':
            self.query['code_name'] = dft_codeName
        if compound_type is not '':
            self.query['compound_type'] = compound_type
        
        if band_gap is not []:
            l = len(band_gap)
            if l == 1:
                self.query['encyclopedia.properties.band_gap'] = band_gap
            #TODO band_gap range    
            #elif l==2:

        #if searchable_quantities is not []:
        #    self.query['dft.searchable_quantities'] = searchable_quantities
        
        return self
        
    def find_all_query(self,section_workflow=True, metadata='all', max_entries=23000):
        """
        Gets all data 
        """
        required={}
        if metadata is 'all':
            required['section_metadata']='*'
        elif metadata is '':
            # if no metadata required, get only the id 
            required['section_metadata'] = {
                'calc_id':'*'
                }
        else:
            required['section_metadata'] = metadata
        
        if section_workflow:
            required['section_workflow'] = {
                'calculation_result_ref': {
                    'single_configuration_calculation_to_system_ref': {
                        'chemical_composition_reduced': '*',
                        'chemical_composition': '*',
                        'section_symmetry': '*',
                        'simulation_cell': '*',
                        'lattice_vectors': '*',
                        'atom_species': '*',
                        'atom_labels': '*',
                        'atom_positions': '*',
                    }
                }
            }
        #TODO section_run stuff
        if self.query.get('dft.searchable_quantities') is not None:
            required['section_run'] = {}

        print('query: ', self.query)
        query = ArchiveQuery(
            query=self.query,
            required = required,
            per_page=1000,
            max=max_entries,
        )
        
        return query
    
        
    
    def get_pd_df(self, section_workflow=True, metadata='all', max_entries=23000):
        """
        Creates Pandas Dataframe from loaded data. 
        """
        # get the query
        try:
            query = self.find_all_query(section_workflow, metadata, max_entries)
            number_queried = query.total
            if number_queried==0:
                raise Exception("No results found on Nomad Database for this query.")
        except Exception as e:
            logger.info("Exception raised with nomad query.")
            raise Exception(e)
        

        scale_factor = 10**10
        df = pd.DataFrame()
        
        from tqdm.auto import tqdm

        from pymatgen import Composition
        from matminer.featurizers.composition import ElementFraction
        ef = ElementFraction()

        from ase.calculators.emt import EMT
        from ase import Atoms
        from ase.structure import molecule

        logger.info('Wrapping data on the Nomad Project Database')
        for entry in tqdm(range(number_queried)):
            try:
                calc = query[entry].section_workflow.calculation_result_ref
                formula_red = calc.single_configuration_calculation_to_system_ref.chemical_composition_reduced
                crystal = calc.single_configuration_calculation_to_system_ref.section_symmetry[0].crystal_system
                space_group = calc.single_configuration_calculation_to_system_ref.section_symmetry[0].space_group_number
                elements = np.sort(calc.single_configuration_calculation_to_system_ref.atom_species)
                # Dimensions of the cell are rescaled to angstroms.
                x,y,z = calc.single_configuration_calculation_to_system_ref.simulation_cell.magnitude * scale_factor
                lat_x, lat_y, lat_z = calc.single_configuration_calculation_to_system_ref.lattice_vectors.magnitude * scale_factor

                entry_calc_id = query[entry].section_metadata.calc_id
                
                search = self.query.get('dft.searchable_quantities')
                searchable_quantities = {}
                if search is not None:
                    if 'stress_tensor' in search:
                        searchable_quantities['stress_tensor'] = query[entry].section_run[-1].section_single_configuration_calculation.stress_tensor
                    #TODO implement other searchable quantities
            except AttributeError as e:
                logger.info(f'AttributeError in get_pd_df: {e}.')
                continue
            except Exception as e:
                logger.info(f'Unhandled exception in get_pd_df: {e}')
                continue
            
            n_atoms = len (elements)

            # The volume of the cell is obtained as scalar triple product of the three base vectors.
            # The triple scalar product is obtained as determinant of the matrix composed with the three vectors.
            cell_volume =  np.linalg.det ([x,y,z])

            # The atomic density is given by the number of atoms in a unit cell.
            density = n_atoms /  cell_volume

            unique_elements = []
            for an in np.unique(elements):
                unique_elements.append(element(int(an)))
            

            fractions = []
            for el in unique_elements:
                fractions.append(np.sum(np.where (elements==el.atomic_number,1,0)) / len(elements))
            # get Composition object 
            comp = Composition(formula_red)
    
            # estimate potential energy 
            #TODO implement energy with VASP
            pot_energy = Atoms(formula_red, calculator=EMT()).get_potential_energy()
            
            
            dict_append = {
                'spacegroup':int(space_group),
                'atomic_density':density,
                'composition':comp,
                # 'Element_fractions':ef.featurize(comp),
                'id':entry_calc_id,
                'pot_Energy':pot_energy,
                'volume': cell_volume,
                'source':'nomad'
            }
            dict_append.update(searchable_quantities)
            df=df.append(dict_append, ignore_index=True)
        
        # df[ef.feature_labels()] = pd.DataFrame(df['Element_fractions'].tolist(), index= df.index)
        # df = df.drop(columns = ['Element_fractions'])
        return df

    def get_all_data(self,calc_id):
        """
        Get all data for a specific calc id.
        """
        query=ArchiveQuery(
            query={
                'domain': 'dft',
                'calc_id':[f'{calc_id}']
            },
            required = {
                'section_run':'*',
                'section_workflow':'*',
                'section_metadata':'*',
            }
        )
        return query
    
    @staticmethod
    def get_structure(calc_id):
        """
        Gets loads structure.cif file as ase object from nomad.
        :param calc_id: list of strings of calc_id's from nomad db (as strings)
        
        :return: List of ase objects
        """
        # query the calc id(s) for the filenames
        query = ArchiveQuery(
            query={
                'domain':'dft',
                'calc_id':calc_id#['jOot82SGvtp2-2_DXylc2K8PrvX8']
            },
            required={
                'section_metadata':{
                    'files':'*',
                    'upload_id':'*',
                    'calc_id':'*'
                }
            }
        )
        all_structures = []
        
        import requests as re
        import io, os
        from ase.io import read
        for q in query:
            upload_id = q.section_metadata.upload_id
            calc_id = q.section_metadata.calc_id
            
            files = q.section_metadata.files
            structure_file = [i for i in files if 'final_structure' in i]
            
            # get the file from nomad
            url = f'http://nomad-lab.eu/prod/rae/api/raw/calc/{upload_id}/{calc_id}/final_structure.cif'
            try:
                file = re.get(url)
                file.raise_for_status()
            except FileNotFoundError:
                print(f'Error finding structure for calc_id {calc_id}')
                continue
           # write as cif file and load using ase
        
            #TODO bypass the write then read
            # maybe using io.BytesIo(file.content)
            with open('__temp_io.cif', 'w') as f:
                f.write(file.text)
                
            structure = read('__temp_io.cif')
            
            all_structures.append(structure)
            
        os.remove('__temp_io.cif')
        return all_structures

if __name__=='__main__':
    
    #print(Nomad_query().get_all_data('BZHXcQA0SaIVu7YDWlwsT2rI086j'))
   # print(Nomad_query().find_all_query())
    print(NomadWrapper().search_params(atoms=['Ag', 'Pd'],searchable_quantities=['stress_tensor'], crystal_system='binary').get_pd_df(metadata=''))

    print(get_structure(['S0xHBMMVvsFsGJk8ybV0ImXuKVjx', 'UOOSveY9WFetIm7S8-j3y7WYum86']))

