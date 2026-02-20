# -*- coding: utf-8 -*-
"""
Config module for 3D printed concrete cube compression test
Extracted from cube_compression.inp
Python 2.7 compatible for Abaqus 2021
"""

class CubeCompressionConfig(object):
    """
    Configuration for 3DPC cube compression simulation
    
    This class contains all parameters extracted from the .inp file
    to ensure the Python workflow produces identical results
    """
    
    def __init__(self):
        # ============================================================
        # 1. UNITS
        # ============================================================
        # SI(mm, MPa, N, s, mJ) as specified in *Heading
        self.unit_system = "SI(mm, MPa, N, s, mJ)"
        self.length_unit = "mm"
        self.stress_unit = "MPa"
        self.force_unit = "N"
        self.time_unit = "s"
        self.energy_unit = "mJ"
        
        # ============================================================
        # 2. GEOMETRY - Concrete Cube
        # ============================================================
        # From *Node coordinates in .inp file:
        # X: 0 ~ 360 mm
        # Y: 0 ~ 90 mm (6 layers, each 15mm thick)
        # Z: 0 ~ 60 mm
        
        self.cube_length_x = 360.0    # mm, X direction
        self.cube_length_y = 90.0     # mm, Y direction (height)
        self.cube_length_z = 60.0     # mm, Z direction
        
        # Layer information (6 layers, each 15mm)
        self.num_layers = 6
        self.layer_thickness = 15.0   # mm
        self.layer_names = [
            'concrete11', 'concrete12', 'concrete13',  # Layer 1 (0-15mm)
            'concrete21', 'concrete22', 'concrete23',  # Layer 2 (15-30mm)
            'concrete31', 'concrete32', 'concrete33',  # Layer 3 (30-45mm)
            'concrete41', 'concrete42', 'concrete43',  # Layer 4 (45-60mm)
            'concrete51', 'concrete52', 'concrete53',  # Layer 5 (60-75mm)
            'concrete61', 'concrete62', 'concrete63',  # Layer 6 (75-90mm)
        ]
        
        # ============================================================
        # 3. GEOMETRY - Support Plates (zhizuo)
        # ============================================================
        # 4 rigid plates for loading and constraint
        self.plate_names = ['zhizuos1', 'zhizuos2', 'zhizuox1', 'zhizuox2']
        # zhizuos1: top plate
        # zhizuos2: bottom plate
        # zhizuox1, zhizuox2: side plates
        
        # ============================================================
        # 4. MATERIAL - Concrete (CDP model)
        # ============================================================
        self.concrete_material_name = "concrete"
        
        # Density (tonne/mm3 for Abaqus)
        self.concrete_density = 2.4e-9   # 2400 kg/m3 = 2.4e-9 tonne/mm3
        
        # Elastic properties (to be filled from paper)
        self.concrete_E = 30000.0        # MPa, Young's modulus (example value)
        self.concrete_nu = 0.2           # Poisson's ratio (example value)
        
        # CDP parameters (to be filled from paper)
        # *Concrete Damaged Plasticity
        self.cdp_dilation_angle = 38.0       # degrees
        self.cdp_eccentricity = 0.1          # default
        self.cdp_fb0_fc0 = 1.16             # ratio
        self.cdp_k = 0.6667                  # default
        self.cdp_viscosity = 0.0             # default
        
        # Compression hardening table: (stress, strain)
        # *Concrete Compression Hardening
        self.concrete_comp_hardening = [
            (20.0, 0.0),      # Example values - to be updated from paper
            (30.0, 0.001),
            (35.0, 0.002),
        ]
        
        # Tension stiffening (displacement type): (stress, displacement)
        # *Concrete Tension Stiffening, type=DISPLACEMENT
        self.concrete_tension_stiffening = [
            (3.0, 0.0),       # Example values - to be updated from paper
            (0.0, 0.1),
        ]
        
        # Compression damage: (damage, strain)
        # *Concrete Compression Damage
        self.concrete_comp_damage = [
            (0.0, 0.0),
            (0.1, 0.001),
            (0.3, 0.002),
        ]
        
        # Tension damage (displacement type): (damage, displacement)
        # *Concrete Tension Damage, type=DISPLACEMENT
        self.concrete_tension_damage = [
            (0.0, 0.0),
            (0.9, 0.1),
        ]
        
        # ============================================================
        # 5. MATERIAL - Cohesive Adhesives (5 types)
        # ============================================================
        # Traction-separation cohesive behavior for interlayer bonding
        
        self.adhesive_names = [
            'ADHESIVE1',  # eset-cohesiveXY
            'ADHESIVE2',
            'ADHESIVE3',
            'ADHESIVE4',
            'ADHESIVE5',  # eset-cohesiveXZ, stack direction=2
        ]
        
        # Common cohesive parameters (to be filled from paper)
        # *ELASTIC, TYPE=TRACTION
        self.cohesive_Enn = 10000.0   # Normal modulus (MPa)
        self.cohesive_Ess = 10000.0   # Shear modulus 1 (MPa)
        self.cohesive_Ett = 10000.0   # Shear modulus 2 (MPa)
        
        # Density
        self.cohesive_density = 1.0e-9   # tonne/mm3
        
        # Damage initiation: QUADS criterion
        # *Damage Initiation, criterion=QUADS
        self.cohesive_damage_initiation = "QUADS"
        
        # Damage evolution: ENERGY + POWER LAW
        # *Damage Evolution, type=ENERGY, mixed mode behavior=POWER LAW, power=2
        self.cohesive_damage_evolution = "ENERGY"
        self.cohesive_mixed_mode = "POWER LAW"
        self.cohesive_power_law = 2.0
        
        # Fracture energies (to be filled from paper)
        self.cohesive_GIc = 0.1    # Mode I fracture energy (mJ/mm2 = N/mm)
        self.cohesive_GIIc = 0.5   # Mode II fracture energy
        self.cohesive_GIIIc = 0.5  # Mode III fracture energy
        
        # ============================================================
        # 6. MATERIAL - Steel (for supports)
        # ============================================================
        self.steel_material_name = "gang"
        self.steel_density = 7.85e-9   # tonne/mm3 (7850 kg/m3)
        self.steel_E = 210000.0         # MPa (210 GPa)
        self.steel_nu = 0.3             # Poisson's ratio
        
        # ============================================================
        # 7. ELEMENT TYPES
        # ============================================================
        self.concrete_element_type = "C3D8R"    # 8-node brick, reduced integration
        self.cohesive_element_type = "COH3D8"   # 8-node cohesive
        self.plate_element_type = "C3D8R"       # Same as concrete
        
        # ============================================================
        # 8. ANALYSIS STEP
        # ============================================================
        self.step_name = "Step-1"
        self.step_type = "Static"
        self.nlgeom = True              # Nonlinear geometry
        self.max_increments = 10000     # Maximum increments
        
        # Stabilization
        self.stabilize = True
        self.stabilize_factor = 0.0002
        self.allsdtol = 0.0
        self.continue_on_error = False
        
        # ============================================================
        # 9. OUTPUT REQUESTS
        # ============================================================
        # Field output
        self.field_output_variables = [
            'U',        # Displacement
            'RF',       # Reaction force
            'S',        # Stress
            'E',        # Strain
            'SDEG',     # Scalar stiffness degradation (damage)
            'STATUS',   # Element status
        ]
        
        # Contact output
        self.contact_output_variables = [
            'CSTRESS',  # Contact stress
            'CSTATUS',  # Contact status
        ]
        
        # History output (PRESELECT)
        self.history_output = True
        
        # Restart output
        self.restart_write = True
        self.restart_frequency = 0   # 0 means at end of step only
        
        # ============================================================
        # 10. WORK DIRECTORY
        # ============================================================
        self.work_dir = r"C:\Users\openclaw\cube_3DPC"
        self.model_name = "CubeCompression_3DPC"
        self.job_name = "CubeCompression_Job"
        
    def print_summary(self):
        """Print configuration summary"""
        print("=" * 60)
        print("3DPC Cube Compression Configuration")
        print("=" * 60)
        print("Unit System: %s" % self.unit_system)
        print("Cube Size: %.1f x %.1f x %.1f mm" % (
            self.cube_length_x, self.cube_length_y, self.cube_length_z))
        print("Number of Layers: %d" % self.num_layers)
        print("Layer Thickness: %.1f mm" % self.layer_thickness)
        print("Concrete Material: %s (CDP)" % self.concrete_material_name)
        print("Cohesive Materials: %d types" % len(self.adhesive_names))
        print("Work Directory: %s" % self.work_dir)
        print("=" * 60)


# Create default config instance
config = CubeCompressionConfig()

if __name__ == "__main__":
    # Test the config
    config.print_summary()
