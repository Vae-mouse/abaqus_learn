# -*- coding: utf-8 -*-
"""
Configuration module for 3D printed concrete Abaqus model.
All parameters are centralized here for easy modification.
"""

class Config:
    """
    Configuration container for 3DPC model.
    
    Attributes:
        # Geometry parameters
        beam_length: Length of concrete beam (mm)
        beam_width: Width of concrete beam (mm)
        beam_height: Height of concrete beam (mm)
        layer_height: Height of each printed layer (mm)
        
        # Rebar parameters
        rebar_diameter: Diameter of steel rebar (mm)
        rebar_spacing: Spacing between rebars (mm)
        rebar_cover: Concrete cover thickness (mm)
        
        # Material parameters - Concrete
        concrete_E: Young's modulus of concrete (MPa)
        concrete_nu: Poisson's ratio of concrete
        concrete_rho: Density of concrete (tonne/mm3)
        concrete_comp_strength: Compressive strength (MPa)
        
        # Material parameters - Steel
        steel_E: Young's modulus of steel (MPa)
        steel_nu: Poisson's ratio of steel
        steel_rho: Density of steel (tonne/mm3)
        steel_yield: Yield strength of steel (MPa)
        
        # Printing parameters
        print_speed: Printing speed (mm/s)
        layer_wait_time: Waiting time between layers (s)
        
        # Analysis parameters
        mesh_size: Global mesh seed size (mm)
    """
    
    def __init__(self):
        # Geometry
        self.beam_length = 300.0
        self.beam_width = 100.0
        self.beam_height = 50.0
        self.layer_height = 10.0
        
        # Rebar
        self.rebar_diameter = 6.0
        self.rebar_spacing = 50.0
        self.rebar_cover = 15.0
        
        # Concrete material
        self.concrete_E = 30000.0
        self.concrete_nu = 0.2
        self.concrete_rho = 2.4e-09
        self.concrete_comp_strength = 40.0
        
        # Steel material
        self.steel_E = 200000.0
        self.steel_nu = 0.3
        self.steel_rho = 7.8e-09
        self.steel_yield = 400.0
        
        # Printing
        self.print_speed = 50.0
        self.layer_wait_time = 60.0
        
        # Mesh
        self.mesh_size = 5.0
    
    def get_layer_count(self):
        """Calculate number of printed layers."""
        return int(self.beam_height / self.layer_height)
    
    def validate(self):
        """Validate configuration parameters."""
        assert self.beam_height > 0, "Beam height must be positive"
        assert self.layer_height > 0, "Layer height must be positive"
        assert self.beam_height % self.layer_height == 0, \
            "Beam height must be divisible by layer height"
        assert self.rebar_diameter < self.beam_height - 2 * self.rebar_cover, \
            "Rebar diameter too large for beam height"
        return True
