# -*- coding: utf-8 -*-
"""
Element birth-death (Model Change) for 3D printing simulation.
Controls layer-by-layer activation of concrete elements.
"""

from abaqus import *
from abaqusConstants import *


def create_layer_element_sets(assembly, config):
    """
    Create element sets for each printed layer.
    
    Args:
        assembly: Assembly object
        config: Config object
        
    Returns:
        dict: Dictionary mapping layer index to element set name
    """
    layer_sets = {}
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    
    for i in range(layer_count):
        z_min = i * config.layer_height
        z_max = (i + 1) * config.layer_height
        
        # Find elements in this layer by their centroid position
        elements = beam_instance.elements
        layer_elements = []
        
        # Note: Elements need to be generated first by meshing
        # This is a placeholder for the logic
        # In practice, we'll create sets based on cells before meshing
        
        set_name = 'LayerElements_%d' % (i + 1)
        layer_sets[i] = set_name
    
    return layer_sets


def create_cell_sets_for_layers(assembly, config):
    """
    Create cell sets for each layer (before meshing).
    These will be used to create element sets after meshing.
    
    Args:
        assembly: Assembly object
        config: Config object
        
    Returns:
        dict: Dictionary mapping layer index to cell set name
    """
    layer_sets = {}
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    cells = beam_instance.cells
    
    for i in range(layer_count):
        z_min = i * config.layer_height
        z_max = (i + 1) * config.layer_height
        
        # Find cells in this layer by their centroid z-coordinate
        layer_cells = []
        for cell in cells:
            center = cell.getCentroid()
            if z_min <= center.coordinates[2] < z_max:
                layer_cells.append(cell)
        
        # Create set for this layer's cells
        if layer_cells:
            set_name = 'LayerCells_%d' % (i + 1)
            assembly.Set(
                name=set_name,
                cells=layer_cells,
                instance=beam_instance
            )
            layer_sets[i] = set_name
    
    return layer_sets


def setup_model_change_for_printing(model, assembly, config):
    """
    Setup Model Change interactions for layer-by-layer printing.
    
    This function creates Model Change interactions that activate
    concrete elements layer by layer during the printing simulation.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        list: List of ModelChange interaction names
    """
    model_change_interactions = []
    layer_count = config.get_layer_count()
    
    beam_instance = assembly.instances['Beam-1']
    
    # Create cell sets for each layer
    layer_cell_sets = create_cell_sets_for_layers(assembly, config)
    
    # Create Model Change interactions for each layer
    for i in range(layer_count):
        step_name = 'PrintLayer%d' % (i + 1)
        
        # Create the analysis step if it doesn't exist
        if step_name not in model.steps.keys():
            previous_step = 'Initial' if i == 0 else 'PrintLayer%d' % i
            model.StaticStep(
                name=step_name,
                previous=previous_step,
                description='Activate layer %d' % (i + 1),
                timePeriod=1.0,
                nlgeom=OFF,
                maxNumInc=100,
                initialInc=0.1,
                minInc=1e-05,
                maxInc=1.0
            )
        
        # Get the cell set for this layer
        cell_set_name = layer_cell_sets.get(i)
        if cell_set_name and cell_set_name in assembly.sets.keys():
            cell_set = assembly.sets[cell_set_name]
            
            # Create Model Change interaction to activate this layer
            interaction_name = 'ActivateLayer%d' % (i + 1)
            
            # Model Change: Add elements (activate)
            model_change = model.ModelChange(
                name=interaction_name,
                createStepName=step_name,
                region=cell_set,
                regionType=GEOMETRY,
                activeInStep=True,
                includeStrain=False
            )
            
            model_change_interactions.append(interaction_name)
    
    return model_change_interactions


def deactivate_all_layers_initially(model, assembly, config):
    """
    Deactivate all concrete elements in the Initial step.
    This ensures elements are only activated during printing steps.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        ModelChange interaction object
    """
    beam_instance = assembly.instances['Beam-1']
    
    # Get all cells (will become elements after meshing)
    all_cells = beam_instance.cells
    
    # Create set for all concrete
    if 'AllConcreteCells' not in assembly.sets.keys():
        assembly.Set(
            name='AllConcreteCells',
            cells=all_cells,
            instance=beam_instance
        )
    
    all_concrete_set = assembly.sets['AllConcreteCells']
    
    # Create Model Change to remove (deactivate) all elements in Initial step
    # This makes them inactive at the start
    deactivate_interaction = model.ModelChange(
        name='DeactivateAllLayers',
        createStepName='Initial',
        region=all_concrete_set,
        regionType=GEOMETRY,
        activeInStep=False,  # False means remove/deactivate
        includeStrain=False
    )
    
    return deactivate_interaction


def create_printing_sequence(model, assembly, config):
    """
    Create complete printing sequence with Model Change.
    
    This is the main function that sets up the entire layer-by-layer
    activation sequence for 3D printing simulation.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        dict: Dictionary containing setup information
    """
    results = {
        'deactivate_interaction': None,
        'activate_interactions': [],
        'steps': []
    }
    
    print("Setting up Model Change for 3D printing simulation...")
    
    # Step 1: Deactivate all layers in Initial step
    print("  Deactivating all layers in Initial step...")
    results['deactivate_interaction'] = deactivate_all_layers_initially(
        model, assembly, config
    )
    
    # Step 2: Create activation interactions for each layer
    print("  Creating layer activation sequence...")
    results['activate_interactions'] = setup_model_change_for_printing(
        model, assembly, config
    )
    
    # Step 3: Record step names
    layer_count = config.get_layer_count()
    results['steps'] = ['PrintLayer%d' % (i + 1) for i in range(layer_count)]
    
    print("  Model Change setup complete:")
    print("    - All layers deactivated in Initial step")
    print("    - %d layers will be activated sequentially" % layer_count)
    
    return results


def verify_model_change_setup(model, assembly, config):
    """
    Verify Model Change setup is correct.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        bool: True if setup is valid
    """
    try:
        # Check if deactivate interaction exists
        if 'DeactivateAllLayers' not in model.interactions.keys():
            print("Warning: DeactivateAllLayers interaction not found")
            return False
        
        # Check if layer activation interactions exist
        layer_count = config.get_layer_count()
        for i in range(layer_count):
            interaction_name = 'ActivateLayer%d' % (i + 1)
            if interaction_name not in model.interactions.keys():
                print("Warning: %s interaction not found" % interaction_name)
                return False
        
        print("Model Change setup verified successfully")
        return True
        
    except Exception as e:
        print("Error verifying Model Change setup: %s" % str(e))
        return False
