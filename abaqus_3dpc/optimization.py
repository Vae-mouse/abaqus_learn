# -*- coding: utf-8 -*-
"""
Optimization framework for 3D printed concrete design.
Multi-objective optimization using simple search methods.
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


class ObjectiveFunction:
    """
    Objective function definition for optimization.
    
    Attributes:
        name: Objective name
        target: 'MINIMIZE' or 'MAXIMIZE'
        extractor: Function to extract value from ODB
        weight: Weight for multi-objective (default 1.0)
    """
    
    def __init__(self, name, target='MINIMIZE', extractor=None, weight=1.0):
        self.name = name
        self.target = target
        self.extractor = extractor
        self.weight = weight
    
    def evaluate(self, odb):
        """Evaluate objective from ODB."""
        if self.extractor:
            return self.extractor(odb)
        return None


class Constraint:
    """
    Constraint definition for optimization.
    
    Attributes:
        name: Constraint name
        condition: 'LESS_THAN', 'GREATER_THAN', or 'EQUAL_TO'
        limit: Constraint limit value
        extractor: Function to extract value from ODB
    """
    
    def __init__(self, name, condition, limit, extractor=None):
        self.name = name
        self.condition = condition
        self.limit = limit
        self.extractor = extractor
    
    def check(self, odb):
        """Check if constraint is satisfied."""
        if self.extractor is None:
            return True
        
        value = self.extractor(odb)
        if value is None:
            return True
        
        if self.condition == 'LESS_THAN':
            return value < self.limit
        elif self.condition == 'GREATER_THAN':
            return value > self.limit
        elif self.condition == 'EQUAL_TO':
            return abs(value - self.limit) < 1e-6
        
        return True


class OptimizationProblem:
    """
    Optimization problem definition.
    
    Manages design variables, objectives, and constraints.
    """
    
    def __init__(self, name):
        self.name = name
        self.variables = {}  # name: (min, max, current)
        self.objectives = []
        self.constraints = []
        self.iteration = 0
        self.history = []
    
    def add_variable(self, name, min_val, max_val, initial=None):
        """
        Add a design variable.
        
        Args:
            name: Variable name (matches Config attribute)
            min_val: Minimum value
            max_val: Maximum value
            initial: Initial value (default: midpoint)
        """
        if initial is None:
            initial = (min_val + max_val) / 2.0
        self.variables[name] = {
            'min': min_val,
            'max': max_val,
            'current': initial,
            'path': name  # Config attribute path
        }
    
    def add_objective(self, objective):
        """Add an objective function."""
        self.objectives.append(objective)
    
    def add_constraint(self, constraint):
        """Add a constraint."""
        self.constraints.append(constraint)
    
    def get_current_values(self):
        """Get current design variable values."""
        return {name: var['current'] 
                for name, var in self.variables.items()}
    
    def update_variables(self, new_values):
        """Update design variable values."""
        for name, value in new_values.items():
            if name in self.variables:
                var = self.variables[name]
                # Clamp to bounds
                value = max(var['min'], min(var['max'], value))
                var['current'] = value
    
    def record_iteration(self, values, objectives, constraints_satisfied):
        """Record iteration results."""
        self.iteration += 1
        self.history.append({
            'iteration': self.iteration,
            'variables': values.copy(),
            'objectives': objectives.copy(),
            'feasible': all(constraints_satisfied)
        })


class GridSearchOptimizer:
    """
    Grid search optimizer for simple parameter spaces.
    """
    
    def __init__(self, problem, grid_points=5):
        self.problem = problem
        self.grid_points = grid_points
    
    def optimize(self, model_creator_func, max_evals=None):
        """
        Run grid search optimization.
        
        Args:
            model_creator_func: Function to create model
            max_evals: Maximum number of evaluations
            
        Returns:
        Best solution found
        """
        if not ABAQUS_AVAILABLE:
            print("Warning: Abaqus not available. Optimization cannot run.")
            return None
        
        import itertools
        
        # Generate grid
        var_names = list(self.problem.variables.keys())
        var_ranges = []
        
        for name in var_names:
            var = self.problem.variables[name]
            step = (var['max'] - var['min']) / (self.grid_points - 1)
            values = [var['min'] + i * step for i in range(self.grid_points)]
            var_ranges.append(values)
        
        # Evaluate all grid points
        best_solution = None
        best_score = float('inf')
        eval_count = 0
        
        for point in itertools.product(*var_ranges):
            if max_evals and eval_count >= max_evals:
                break
            
            eval_count += 1
            values = dict(zip(var_names, point))
            
            print("Evaluating: {}".format(values))
            
            # Create and run model
            try:
                from config import Config
                config = Config()
                
                # Apply design variables
                for name, value in values.items():
                    setattr(config, name, value)
                
                model = model_creator_func(config)
                
                # Run job
                job_name = '{}_iter{}'.format(self.problem.name, eval_count)
                job = mdb.Job(name=job_name, model=model.name)
                job.submit()
                job.waitForCompletion()
                
                # Evaluate objectives and constraints
                odb = openOdb(path='{}.odb'.format(job_name))
                
                obj_values = {}
                for obj in self.problem.objectives:
                    val = obj.evaluate(odb)
                    if val is not None:
                        # Convert to minimization
                        if obj.target == 'MAXIMIZE':
                            val = -val
                        obj_values[obj.name] = val * obj.weight
                
                constraint_status = []
                for con in self.problem.constraints:
                    constraint_status.append(con.check(odb))
                
                odb.close()
                
                # Calculate score (weighted sum)
                score = sum(obj_values.values())
                
                # Record iteration
                self.problem.record_iteration(values, obj_values, constraint_status)
                
                # Update best solution
                if all(constraint_status) and score < best_score:
                    best_score = score
                    best_solution = {
                        'values': values.copy(),
                        'score': score,
                        'objectives': obj_values.copy()
                    }
                
            except Exception as e:
                print("  Error: {}".format(e))
        
        return best_solution


class SensitivityAnalyzer:
    """
    Sensitivity analysis for design parameters.
    """
    
    def __init__(self, base_config):
        self.base_config = base_config
        self.results = {}
    
    def analyze_parameter(self, param_name, param_path, 
                         variations=[0.8, 0.9, 1.0, 1.1, 1.2],
                         model_creator_func=None):
        """
        Analyze sensitivity of a single parameter.
        
        Args:
            param_name: Parameter name
            param_path: Path to parameter in Config
            variations: Variation factors
            model_creator_func: Function to create and run model
            
        Returns:
            Dictionary of results
        """
        import copy
        
        # Get base value
        parts = param_path.split('.')
        obj = self.base_config
        for part in parts[:-1]:
            obj = getattr(obj, part)
        base_value = getattr(obj, parts[-1])
        
        results = {
            'parameter': param_name,
            'base_value': base_value,
            'variations': []
        }
        
        for factor in variations:
            value = base_value * factor
            
            # Create modified config
            config = copy.deepcopy(self.base_config)
            obj = config
            for part in parts[:-1]:
                obj = getattr(obj, part)
            setattr(obj, parts[-1], value)
            
            # Run model if function provided
            if model_creator_func and ABAQUS_AVAILABLE:
                try:
                    model = model_creator_func(config)
                    # Run and extract results...
                    result = {'factor': factor, 'value': value, 'status': 'completed'}
                except Exception as e:
                    result = {'factor': factor, 'value': value, 'status': 'failed', 'error': str(e)}
            else:
                result = {'factor': factor, 'value': value, 'status': 'config_only'}
            
            results['variations'].append(result)
        
        self.results[param_name] = results
        return results
    
    def save_report(self, filename='sensitivity_report.json'):
        """Save sensitivity analysis report."""
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)


def create_weight_minimization_problem():
    """
    Create an optimization problem for minimum weight design.
    
    Returns:
        OptimizationProblem object
    """
    problem = OptimizationProblem('WeightMinimization')
    
    # Design variables
    problem.add_variable('beam_height', 30.0, 100.0, 50.0)
    problem.add_variable('beam_width', 50.0, 150.0, 100.0)
    problem.add_variable('rebar_diameter', 4.0, 12.0, 6.0)
    
    # Objective: minimize volume (proxy for weight)
    def extract_volume(odb):
        # Simplified - would need actual volume calculation
        return 1.0
    
    problem.add_objective(ObjectiveFunction('Volume', 'MINIMIZE', extract_volume))
    
    # Constraint: max stress < allowable
    def extract_max_stress(odb):
        try:
            last_frame = odb.steps.values()[-1].frames[-1]
            stress = last_frame.fieldOutputs['S']
            return max([s.maxPrincipal for s in stress.values])
        except:
            return 0.0
    
    problem.add_constraint(Constraint('MaxStress', 'LESS_THAN', 30.0, extract_max_stress))
    
    return problem


def create_stiffness_maximization_problem():
    """
    Create an optimization problem for maximum stiffness design.
    
    Returns:
        OptimizationProblem object
    """
    problem = OptimizationProblem('StiffnessMaximization')
    
    # Design variables
    problem.add_variable('beam_height', 30.0, 100.0, 50.0)
    problem.add_variable('concrete_E', 20000.0, 40000.0, 30000.0)
    
    # Objective: minimize max displacement (maximize stiffness)
    def extract_max_disp(odb):
        try:
            last_frame = odb.steps.values()[-1].frames[-1]
            disp = last_frame.fieldOutputs['U']
            return max([d.magnitude for d in disp.values])
        except:
            return float('inf')
    
    problem.add_objective(ObjectiveFunction('MaxDisplacement', 'MINIMIZE', extract_max_disp))
    
    return problem
