# -*- coding: utf-8 -*-
"""
Parameter optimization and design study for 3D printed concrete.
Supports parametric sweeps and sensitivity analysis.
"""

import sys
import os
import json

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False


class DesignVariable:
    """
    Design variable definition for parametric study.
    
    Attributes:
        name: Variable name
        param_path: Path to parameter in Config (e.g., 'beam_height')
        min_val: Minimum value
        max_val: Maximum value
        num_points: Number of sampling points
        values: List of specific values (optional, overrides min/max/num)
    """
    
    def __init__(self, name, param_path, min_val=None, max_val=None, 
                 num_points=5, values=None):
        self.name = name
        self.param_path = param_path
        self.min_val = min_val
        self.max_val = max_val
        self.num_points = num_points
        self.values = values
        
        if values is None and (min_val is None or max_val is None):
            raise ValueError("Either values or min_val/max_val must be provided")
    
    def get_values(self):
        """Generate or return parameter values."""
        if self.values is not None:
            return self.values
        
        # Generate linear spacing
        step = (self.max_val - self.min_val) / (self.num_points - 1)
        return [self.min_val + i * step for i in range(self.num_points)]


class DesignStudy:
    """
    Design study for 3D printed concrete parametric analysis.
    
    Manages multiple design points and results collection.
    """
    
    def __init__(self, name, base_config):
        """
        Initialize design study.
        
        Args:
            name: Study name
            base_config: Base Config object
        """
        self.name = name
        self.base_config = base_config
        self.variables = []
        self.design_points = []
        self.results = []
    
    def add_variable(self, variable):
        """
        Add a design variable to the study.
        
        Args:
            variable: DesignVariable object
        """
        self.variables.append(variable)
    
    def generate_design_points(self):
        """
        Generate all design points from variable combinations.
        
        Returns:
            List of (config_dict, point_id) tuples
        """
        import itertools
        
        # Get values for each variable
        var_values = [v.get_values() for v in self.variables]
        var_names = [v.name for v in self.variables]
        var_paths = [v.param_path for v in self.variables]
        
        # Generate all combinations
        design_points = []
        point_id = 0
        
        for combination in itertools.product(*var_values):
            point_id += 1
            config_dict = {}
            
            # Build config dictionary
            for i, (name, path, value) in enumerate(zip(var_names, var_paths, combination)):
                config_dict[path] = value
            
            design_points.append((config_dict, point_id))
        
        self.design_points = design_points
        return design_points
    
    def create_config_for_point(self, config_dict):
        """
        Create a Config object for a specific design point.
        
        Args:
            config_dict: Dictionary of parameter values
            
        Returns:
            Config object
        """
        import copy
        config = copy.deepcopy(self.base_config)
        
        # Apply parameter values
        for path, value in config_dict.items():
            parts = path.split('.')
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
        
        return config


def run_parametric_study(study, model_creator_func, output_dir='parametric_results'):
    """
    Run a parametric study with multiple design points.
    
    Args:
        study: DesignStudy object
        model_creator_func: Function to create model (takes config, returns model)
        output_dir: Directory for output files
        
    Returns:
        List of results dictionaries
    """
    if not ABAQUS_AVAILABLE:
        print("Warning: Abaqus not available. Parametric study cannot run.")
        return []
    
    import os
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    results = []
    design_points = study.generate_design_points()
    
    print("Running parametric study: {}".format(study.name))
    print("Total design points: {}".format(len(design_points)))
    print("")
    
    for config_dict, point_id in design_points:
        print("Design Point {}: {}".format(point_id, config_dict))
        
        # Create config for this point
        config = study.create_config_for_point(config_dict)
        
        # Create model
        try:
            model = model_creator_func(config)
            
            # Save model
            model_name = '{}_DP{}'.format(study.name, point_id)
            mdb.saveAs(pathName=os.path.join(output_dir, '{}.cae'.format(model_name)))
            
            # Create and submit job
            job = mdb.Job(name=model_name, model=model.name)
            job.submit()
            job.waitForCompletion()
            
            # Collect results
            result = {
                'point_id': point_id,
                'parameters': config_dict,
                'job_name': model_name,
                'status': 'completed'
            }
            
            # Extract key results from ODB
            try:
                odb = openOdb(path='{}.odb'.format(model_name))
                # Extract relevant results here
                result['max_stress'] = extract_max_stress(odb)
                result['max_displacement'] = extract_max_displacement(odb)
                odb.close()
            except:
                result['status'] = 'completed_no_results'
            
            results.append(result)
            
        except Exception as e:
            print("  Error: {}".format(e))
            results.append({
                'point_id': point_id,
                'parameters': config_dict,
                'status': 'failed',
                'error': str(e)
            })
    
    study.results = results
    
    # Save results summary
    summary_file = os.path.join(output_dir, '{}_summary.json'.format(study.name))
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\nParametric study completed. Results saved to: {}".format(output_dir))
    return results


def extract_max_stress(odb):
    """Extract maximum stress from ODB."""
    try:
        last_frame = odb.steps.values()[-1].frames[-1]
        stress_field = last_frame.fieldOutputs['S']
        max_stress = max([val.maxPrincipal for val in stress_field.values])
        return max_stress
    except:
        return None


def extract_max_displacement(odb):
    """Extract maximum displacement from ODB."""
    try:
        last_frame = odb.steps.values()[-1].frames[-1]
        disp_field = last_frame.fieldOutputs['U']
        max_disp = max([val.magnitude for val in disp_field.values])
        return max_disp
    except:
        return None


def create_sensitivity_study(base_config, param_name, param_path, 
                             variations=[0.8, 0.9, 1.0, 1.1, 1.2]):
    """
    Create a sensitivity study for a single parameter.
    
    Args:
        base_config: Base Config object
        param_name: Parameter name for display
        param_path: Path to parameter in Config
        variations: List of variation factors (relative to base value)
        
    Returns:
        DesignStudy object
    """
    study = DesignStudy('Sensitivity_{}'.format(param_name), base_config)
    
    # Get base value
    parts = param_path.split('.')
    obj = base_config
    for part in parts[:-1]:
        obj = getattr(obj, part)
    base_value = getattr(obj, parts[-1])
    
    # Create values
    values = [base_value * v for v in variations]
    
    variable = DesignVariable(
        name=param_name,
        param_path=param_path,
        values=values
    )
    
    study.add_variable(variable)
    return study


def create_layer_thickness_study(base_config, thicknesses=[5.0, 10.0, 15.0, 20.0]):
    """
    Create a study for layer thickness optimization.
    
    Args:
        base_config: Base Config object
        thicknesses: List of layer thicknesses to test
        
    Returns:
        DesignStudy object
    """
    study = DesignStudy('LayerThickness', base_config)
    
    variable = DesignVariable(
        name='LayerThickness',
        param_path='layer_height',
        values=thicknesses
    )
    
    study.add_variable(variable)
    return study


def create_rebar_ratio_study(base_config, diameters=[4.0, 6.0, 8.0, 10.0]):
    """
    Create a study for rebar diameter optimization.
    
    Args:
        base_config: Base Config object
        diameters: List of rebar diameters to test
        
    Returns:
        DesignStudy object
    """
    study = DesignStudy('RebarDiameter', base_config)
    
    variable = DesignVariable(
        name='RebarDiameter',
        param_path='rebar_diameter',
        values=diameters
    )
    
    study.add_variable(variable)
    return study


def create_span_depth_study(base_config, 
                            spans=[200.0, 250.0, 300.0, 350.0, 400.0],
                            depths=[30.0, 40.0, 50.0, 60.0, 70.0]):
    """
    Create a study for span-to-depth ratio optimization.
    
    Args:
        base_config: Base Config object
        spans: List of beam spans
        depths: List of beam depths
        
    Returns:
        DesignStudy object
    """
    study = DesignStudy('SpanDepthRatio', base_config)
    
    span_var = DesignVariable(
        name='BeamSpan',
        param_path='beam_length',
        values=spans
    )
    
    depth_var = DesignVariable(
        name='BeamDepth',
        param_path='beam_height',
        values=depths
    )
    
    study.add_variable(span_var)
    study.add_variable(depth_var)
    return study
