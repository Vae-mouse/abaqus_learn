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
        
        # Elastic properties (MUST be filled from paper)
        # TODO: These are placeholder values - replace with actual values from reference
        self.concrete_E = None  # MPa, Young's modulus - FILL FROM PAPER
        self.concrete_nu = None  # Poisson's ratio - FILL FROM PAPER
        
        # CDP parameters (to be filled from paper)
        # *Concrete Damaged Plasticity
        self.cdp_dilation_angle = 38.0       # degrees
        self.cdp_eccentricity = 0.1          # default
        self.cdp_fb0_fc0 = 1.16             # ratio
        self.cdp_k = 0.6667                  # default
        self.cdp_viscosity = 0.0             # default
        
        # Compression hardening table: (stress, strain)
        # *Concrete Compression Hardening
        # TODO: Must be extracted from paper - these are placeholder values
        self.concrete_comp_hardening = None
        
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
        
        # Common cohesive parameters (MUST be filled from paper)
        # *ELASTIC, TYPE=TRACTION
        # TODO: These are placeholder values
        self.cohesive_Enn = None   # Normal modulus (MPa) - FILL FROM PAPER
        self.cohesive_Ess = None   # Shear modulus 1 (MPa) - FILL FROM PAPER
        self.cohesive_Ett = None   # Shear modulus 2 (MPa) - FILL FROM PAPER
        
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

    def validate(self):
        """
        Validate that all required parameters are set.
        
        Raises:
            NotImplementedError: If any required parameter is not set
        """
        errors = []
        
        # Check concrete elastic properties
        if self.concrete_E is None:
            errors.append("concrete_E (Young's modulus)")
        if self.concrete_nu is None:
            errors.append("concrete_nu (Poisson's ratio)")
        
        # Check concrete hardening data
        if self.concrete_comp_hardening is None:
            errors.append("concrete_comp_hardening (compression hardening curve)")
        
        # Check cohesive properties
        if self.cohesive_Enn is None:
            errors.append("cohesive_Enn (normal modulus)")
        if self.cohesive_Ess is None:
            errors.append("cohesive_Ess (shear modulus 1)")
        if self.cohesive_Ett is None:
            errors.append("cohesive_Ett (shear modulus 2)")
        
        # Check loading parameters
        if not hasattr(self, 'loading_displacement') or self.loading_displacement is None:
            errors.append("loading_displacement (compression displacement)")
        
        if errors:
            raise NotImplementedError(
                "The following required parameters are not set:\n" +
                "\n".join("  - " + e for e in errors) +
                "\n\nPlease extract these values from the reference paper "
                "and set them on the config instance before calling validate()."
            )
        
        print("Config validation passed!")
        return True


# Create default config instance
# NOTE: This will raise NotImplementedError if required parameters are not set
# To use this project, you must either:
# 1. Fill in all required parameters in CubeCompressionConfig.__init__
# 2. Or create a subclass with your specific parameters
# 3. Or set environment variables before import
# 
# Example usage:
#   from config import CubeCompressionConfig
#   config = CubeCompressionConfig()
#   # Then set parameters:
#   config.concrete_E = 30000.0
#   config.concrete_nu = 0.2
#   config.validate()  # Call this after setting all parameters
#
# For now, we don't auto-create to avoid import-time errors:
config = None  # User must create and configure instance

if __name__ == "__main__":
    # Test the config
    config.print_summary()
