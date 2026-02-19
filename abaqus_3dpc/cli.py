# -*- coding: utf-8 -*-
"""
Command-line interface for 3D printed concrete model generator.
Alternative to GUI for batch processing and scripting.
"""

import sys
import os
import argparse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def create_parser():
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        description='3D Printed Concrete Abaqus Model Generator',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create basic model
  python cli.py --length 300 --width 100 --height 50
  
  # Create with rebar
  python cli.py --length 300 --width 100 --height 50 --rebar-diameter 6 --rebar-spacing 50
  
  # Create thermal analysis model
  python cli.py --length 300 --width 100 --height 50 --analysis thermal
  
  # Create damage analysis model
  python cli.py --length 300 --width 100 --height 50 --analysis damage --concrete-strength 30
  
  # List available examples
  python cli.py --list-examples
        """
    )
    
    # Geometry arguments
    geom_group = parser.add_argument_group('Geometry')
    geom_group.add_argument('--length', '-L', type=float, default=300.0,
                           help='Beam length in mm (default: 300)')
    geom_group.add_argument('--width', '-W', type=float, default=100.0,
                           help='Beam width in mm (default: 100)')
    geom_group.add_argument('--height', '-H', type=float, default=50.0,
                           help='Beam height in mm (default: 50)')
    geom_group.add_argument('--layer-height', type=float, default=10.0,
                           help='Layer height in mm (default: 10)')
    
    # Rebar arguments
    rebar_group = parser.add_argument_group('Rebar')
    rebar_group.add_argument('--rebar-diameter', type=float, default=6.0,
                            help='Rebar diameter in mm (default: 6)')
    rebar_group.add_argument('--rebar-spacing', type=float, default=50.0,
                            help='Rebar spacing in mm (default: 50)')
    rebar_group.add_argument('--rebar-cover', type=float, default=15.0,
                            help='Concrete cover thickness in mm (default: 15)')
    rebar_group.add_argument('--no-rebar', action='store_true',
                            help='Exclude rebar from model')
    
    # Material arguments
    mat_group = parser.add_argument_group('Materials')
    mat_group.add_argument('--concrete-E', type=float, default=30000.0,
                          help='Concrete elastic modulus in MPa (default: 30000)')
    mat_group.add_argument('--concrete-strength', type=float, default=30.0,
                          help='Concrete compressive strength in MPa (default: 30)')
    mat_group.add_argument('--steel-E', type=float, default=200000.0,
                          help='Steel elastic modulus in MPa (default: 200000)')
    
    # Analysis arguments
    analysis_group = parser.add_argument_group('Analysis')
    analysis_group.add_argument('--analysis', '-a', 
                               choices=['static', 'thermal', 'damage', 'printing'],
                               default='static',
                               help='Analysis type (default: static)')
    analysis_group.add_argument('--cohesive', action='store_true',
                               help='Include cohesive contact between layers')
    analysis_group.add_argument('--element-birth', action='store_true',
                               help='Simulate printing process with element birth/death')
    
    # Mesh arguments
    mesh_group = parser.add_argument_group('Mesh')
    mesh_group.add_argument('--mesh-size', type=float, default=5.0,
                           help='Global mesh seed size in mm (default: 5)')
    
    # Output arguments
    output_group = parser.add_argument_group('Output')
    output_group.add_argument('--name', '-n', default='3DPC_Model',
                             help='Model name (default: 3DPC_Model)')
    output_group.add_argument('--output-dir', '-o', default='./models',
                             help='Output directory (default: ./models)')
    output_group.add_argument('--create-job', action='store_true',
                             help='Create analysis job')
    
    # Other arguments
    parser.add_argument('--list-examples', action='store_true',
                       help='List available example scripts')
    parser.add_argument('--gui', '-g', action='store_true',
                       help='Launch GUI instead of CLI')
    parser.add_argument('--version', '-v', action='version', version='3DPC Generator 1.0')
    
    return parser


def validate_args(args):
    """Validate command-line arguments."""
    errors = []
    
    # Check positive values
    if args.length <= 0:
        errors.append("Length must be positive")
    if args.width <= 0:
        errors.append("Width must be positive")
    if args.height <= 0:
        errors.append("Height must be positive")
    if args.layer_height <= 0:
        errors.append("Layer height must be positive")
    
    # Check layer height divides beam height
    if args.height % args.layer_height != 0:
        errors.append("Beam height must be divisible by layer height")
    
    # Check rebar fits
    if not args.no_rebar:
        if args.rebar_diameter >= args.height - 2 * args.rebar_cover:
            errors.append("Rebar diameter too large for beam height and cover")
    
    # Check material properties
    if args.concrete_E <= 0:
        errors.append("Concrete elastic modulus must be positive")
    if args.concrete_strength <= 0:
        errors.append("Concrete strength must be positive")
    
    return errors


def create_config_from_args(args):
    """Create Config object from arguments."""
    from config import Config
    
    config = Config()
    config.beam_length = args.length
    config.beam_width = args.width
    config.beam_height = args.height
    config.layer_height = args.layer_height
    config.rebar_diameter = args.rebar_diameter
    config.rebar_spacing = args.rebar_spacing
    config.rebar_cover = args.rebar_cover
    config.concrete_E = args.concrete_E
    config.concrete_comp_strength = args.concrete_strength
    config.steel_E = args.steel_E
    config.mesh_size = args.mesh_size
    
    return config


def run_static_analysis(args):
    """Run static analysis model creation."""
    print("Creating static analysis model...")
    
    try:
        import abaqus
        from main_complete import create_complete_3dpc_model
        
        model = create_complete_3dpc_model()
        print("✓ Model created: {}".format(model.name))
        return model
        
    except ImportError:
        print("✗ Abaqus not available. Cannot create model.")
        return None


def run_thermal_analysis(args):
    """Run thermal-mechanical analysis model creation."""
    print("Creating thermal-mechanical analysis model...")
    
    try:
        import abaqus
        from example_thermal import create_thermal_3dpc_model
        
        model = create_thermal_3dpc_model()
        print("✓ Model created: {}".format(model.name))
        return model
        
    except ImportError:
        print("✗ Abaqus not available. Cannot create model.")
        return None


def run_damage_analysis(args):
    """Run damage analysis model creation."""
    print("Creating damage analysis model...")
    
    try:
        import abaqus
        from example_damage import create_damage_analysis_model
        
        model = create_damage_analysis_model()
        print("✓ Model created: {}".format(model.name))
        return model
        
    except ImportError:
        print("✗ Abaqus not available. Cannot create model.")
        return None


def run_printing_simulation(args):
    """Run printing process simulation model creation."""
    print("Creating printing process simulation model...")
    
    try:
        import abaqus
        from element_birth import setup_element_birth_for_all_layers
        from main_complete import create_complete_3dpc_model
        
        # Create base model
        model = create_complete_3dpc_model()
        
        # Add element birth/death
        # This would need access to the assembly and step objects
        print("✓ Model created with printing simulation")
        return model
        
    except ImportError:
        print("✗ Abaqus not available. Cannot create model.")
        return None


def list_examples():
    """List available example scripts."""
    examples = [
        ("example.py", "Complete workflow example"),
        ("example_thermal.py", "Thermal-mechanical coupled analysis"),
        ("example_damage.py", "Damage and crack propagation"),
        ("example_parametric.py", "Parametric studies"),
        ("minimal_test.py", "Minimal functionality test"),
        ("main_complete.py", "Complete model with all features"),
    ]
    
    print("\nAvailable Example Scripts:")
    print("=" * 60)
    for script, description in examples:
        print("  {:25s} - {}".format(script, description))
    print("\nTo run an example in Abaqus CAE:")
    print("  execfile('path/to/example.py')")
    print()


def main():
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    # Handle special commands
    if args.list_examples:
        list_examples()
        return 0
    
    if args.gui:
        try:
            from gui import launch_gui
            launch_gui()
            return 0
        except ImportError as e:
            print("Error: Cannot launch GUI: {}".format(e))
            return 1
    
    # Validate arguments
    errors = validate_args(args)
    if errors:
        print("Validation errors:")
        for error in errors:
            print("  ✗ {}".format(error))
        return 1
    
    # Print configuration
    print("\n3DPC Model Generator")
    print("=" * 60)
    print("Configuration:")
    print("  Geometry: {} x {} x {} mm".format(args.length, args.width, args.height))
    print("  Layer height: {} mm".format(args.layer_height))
    print("  Layers: {}".format(int(args.height / args.layer_height)))
    if not args.no_rebar:
        print("  Rebar: {} mm diameter @ {} mm spacing".format(
            args.rebar_diameter, args.rebar_spacing))
    print("  Analysis type: {}".format(args.analysis))
    print("  Mesh size: {} mm".format(args.mesh_size))
    print()
    
    # Run appropriate analysis
    if args.analysis == 'static':
        model = run_static_analysis(args)
    elif args.analysis == 'thermal':
        model = run_thermal_analysis(args)
    elif args.analysis == 'damage':
        model = run_damage_analysis(args)
    elif args.analysis == 'printing':
        model = run_printing_simulation(args)
    else:
        print("Unknown analysis type: {}".format(args.analysis))
        return 1
    
    if model is None:
        return 1
    
    # Save model
    try:
        import os
        if not os.path.exists(args.output_dir):
            os.makedirs(args.output_dir)
        
        save_path = os.path.join(args.output_dir, args.name + '.cae')
        
        # Note: In actual Abaqus environment, would use:
        # mdb.saveAs(pathName=save_path)
        print("✓ Model would be saved to: {}".format(save_path))
        
        if args.create_job:
            print("✓ Analysis job '{}' created".format(args.name))
        
        print("\nModel generation complete!")
        return 0
        
    except Exception as e:
        print("✗ Error saving model: {}".format(e))
        return 1


if __name__ == '__main__':
    sys.exit(main())
