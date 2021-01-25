import numpy as np
import pandas as pd

from nomad import client, config
from nomad.metainfo import units
from nomad.client import ArchiveQuery
from mendeleev import element


class Nomad_query:
    def __init__(self,):
        self.query={'domain':'dft'}
        config.client.url = 'http://nomad-lab.eu/prod/rae/api'
        
        pass
    
    def search_params(self,atoms,crystal_system ='', dft_codeName='', compound_type=''):
        """
        atoms: array of strings of elements ex: ['O', 'V']
        
        """
        self.query['atoms'] = atoms
        
        if crystal_system is not '':
            self.query['dft.compound_type'] = crystal_system
        if dft_codeName is not '':
            self.query['code_name'] = dft_codeName
        if compound_type is not '':
            self.query['compound_type'] = compound_type
        
        return self
        
    def find_all_query(self,section_workflow=True, metadata='all', max_entries=23000):
        
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
        
        print(self.query)
        query = ArchiveQuery(
            query=self.query,
            required = required,
            per_page=1000,
            max=max_entries,
        )
        
        return query
    
        
    
    def get_pd_df(self, section_workflow=True, metadata='all', max_entries=23000):
        
        # get the query
        try:
            query = self.find_all_query(section_workflow, metadata, max_entries)
            number_queried = query.total
        except Exception as e:
            raise "Invalid query. "

        scale_factor = 10**10
        df = pd.DataFrame()
        
        from tqdm import tqdm as tqdm

        from pymatgen import Composition
        from matminer.featurizers.composition import ElementFraction
        ef = ElementFraction()

        from ase.calculators.emt import EMT
        from ase import Atoms
        from ase.structure import molecule
        

        
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
                
            except AttributeError:
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

            df=df.append({
                'Space_group_number':int(space_group),
                'Atomic_density':density,
                'Formula':comp,
                'Element_fractions':ef.featurize(comp),
                'Calc_id':entry_calc_id,
                'Pot Energy':pot_energy,
            },ignore_index=True)

        df[ef.feature_labels()] = pd.DataFrame(df['Element_fractions'].tolist(), index= df.index)
        print(df)
        df = df.drop(columns = ['Element_fractions'])
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
    
if __name__=='__main__':
    
    #nomad = Nomad_query().search_params(atoms=['O','H'])
    #print(nomad.find_all_query())
    
    #print(Nomad_query().get_all_data('BZHXcQA0SaIVu7YDWlwsT2rI086j'))
   # print(Nomad_query().find_all_query())
    print(Nomad_query().search_params(atoms=['Ag', 'Pd'], crystal_system='binary').get_pd_df(metadata=''))
