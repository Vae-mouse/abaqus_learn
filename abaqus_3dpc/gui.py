# -*- coding: utf-8 -*-
"""
Simple GUI for 3D printed concrete Abaqus model generator.
Provides a user-friendly interface for parameter input and model creation.
"""

import sys
import os

# Try to import tkinter
try:
    if sys.version_info[0] >= 3:
        import tkinter as tk
        from tkinter import ttk
        from tkinter import messagebox
    else:
        import Tkinter as tk
        import ttk
        import tkMessageBox as messagebox
    TKINTER_AVAILABLE = True
except ImportError:
    TKINTER_AVAILABLE = False

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False


if TKINTER_AVAILABLE:
    class ModelConfigFrame(ttk.LabelFrame):
        """Frame for model configuration parameters."""
        
        def __init__(self, parent, title="Model Configuration"):
            ttk.LabelFrame.__init__(self, parent, text=title, padding=10)
            
            # Geometry parameters
            ttk.Label(self, text="Beam Length (mm):").grid(row=0, column=0, sticky='w', pady=2)
            self.beam_length = ttk.Entry(self, width=10)
            self.beam_length.insert(0, "300")
            self.beam_length.grid(row=0, column=1, pady=2)
            
            ttk.Label(self, text="Beam Width (mm):").grid(row=1, column=0, sticky='w', pady=2)
            self.beam_width = ttk.Entry(self, width=10)
            self.beam_width.insert(0, "100")
            self.beam_width.grid(row=1, column=1, pady=2)
            
            ttk.Label(self, text="Beam Height (mm):").grid(row=2, column=0, sticky='w', pady=2)
            self.beam_height = ttk.Entry(self, width=10)
            self.beam_height.insert(0, "50")
            self.beam_height.grid(row=2, column=1, pady=2)
            
            ttk.Label(self, text="Layer Height (mm):").grid(row=3, column=0, sticky='w', pady=2)
            self.layer_height = ttk.Entry(self, width=10)
            self.layer_height.insert(0, "10")
            self.layer_height.grid(row=3, column=1, pady=2)
            
            # Separator
            ttk.Separator(self, orient='horizontal').grid(row=4, column=0, columnspan=2, sticky='ew', pady=10)
            
            # Rebar parameters
            ttk.Label(self, text="Rebar Diameter (mm):").grid(row=5, column=0, sticky='w', pady=2)
            self.rebar_diameter = ttk.Entry(self, width=10)
            self.rebar_diameter.insert(0, "6")
            self.rebar_diameter.grid(row=5, column=1, pady=2)
            
            ttk.Label(self, text="Rebar Spacing (mm):").grid(row=6, column=0, sticky='w', pady=2)
            self.rebar_spacing = ttk.Entry(self, width=10)
            self.rebar_spacing.insert(0, "50")
            self.rebar_spacing.grid(row=6, column=1, pady=2)
            
            ttk.Label(self, text="Cover Thickness (mm):").grid(row=7, column=0, sticky='w', pady=2)
            self.rebar_cover = ttk.Entry(self, width=10)
            self.rebar_cover.insert(0, "15")
            self.rebar_cover.grid(row=7, column=1, pady=2)


    class MaterialConfigFrame(ttk.LabelFrame):
        """Frame for material configuration."""
        
        def __init__(self, parent, title="Material Properties"):
            ttk.LabelFrame.__init__(self, parent, text=title, padding=10)
            
            # Concrete properties
            ttk.Label(self, text="Concrete Grade:").grid(row=0, column=0, sticky='w', pady=2)
            self.concrete_grade = ttk.Combobox(self, values=["C20", "C30", "C40", "C50"], width=8)
            self.concrete_grade.set("C30")
            self.concrete_grade.grid(row=0, column=1, pady=2)
            
            ttk.Label(self, text="Elastic Modulus (MPa):").grid(row=1, column=0, sticky='w', pady=2)
            self.concrete_E = ttk.Entry(self, width=10)
            self.concrete_E.insert(0, "30000")
            self.concrete_E.grid(row=1, column=1, pady=2)
            
            ttk.Label(self, text="Compressive Strength (MPa):").grid(row=2, column=0, sticky='w', pady=2)
            self.concrete_strength = ttk.Entry(self, width=10)
            self.concrete_strength.insert(0, "30")
            self.concrete_strength.grid(row=2, column=1, pady=2)
            
            # Separator
            ttk.Separator(self, orient='horizontal').grid(row=3, column=0, columnspan=2, sticky='ew', pady=10)
            
            # Steel properties
            ttk.Label(self, text="Steel Grade:").grid(row=4, column=0, sticky='w', pady=2)
            self.steel_grade = ttk.Combobox(self, values=["Q235", "Q345", "HRB400"], width=8)
            self.steel_grade.set("Q235")
            self.steel_grade.grid(row=4, column=1, pady=2)
            
            ttk.Label(self, text="Elastic Modulus (MPa):").grid(row=5, column=0, sticky='w', pady=2)
            self.steel_E = ttk.Entry(self, width=10)
            self.steel_E.insert(0, "200000")
            self.steel_E.grid(row=5, column=1, pady=2)


    class AnalysisOptionsFrame(ttk.LabelFrame):
        """Frame for analysis options."""
        
        def __init__(self, parent, title="Analysis Options"):
            ttk.LabelFrame.__init__(self, parent, text=title, padding=10)
            
            # Analysis type
            self.analysis_type = tk.StringVar(value="static")
            ttk.Radiobutton(self, text="Static Analysis", variable=self.analysis_type, 
                           value="static").grid(row=0, column=0, sticky='w', pady=2)
            ttk.Radiobutton(self, text="Thermal-Mechanical", variable=self.analysis_type,
                           value="thermal").grid(row=1, column=0, sticky='w', pady=2)
            ttk.Radiobutton(self, text="Damage Analysis", variable=self.analysis_type,
                           value="damage").grid(row=2, column=0, sticky='w', pady=2)
            
            # Separator
            ttk.Separator(self, orient='horizontal').grid(row=3, column=0, sticky='ew', pady=10)
            
            # Checkboxes
            self.include_rebar = tk.BooleanVar(value=True)
            ttk.Checkbutton(self, text="Include Rebar", variable=self.include_rebar).grid(row=4, column=0, sticky='w', pady=2)
            
            self.include_cohesive = tk.BooleanVar(value=False)
            ttk.Checkbutton(self, text="Include Cohesive Contact", variable=self.include_cohesive).grid(row=5, column=0, sticky='w', pady=2)
            
            self.include_element_birth = tk.BooleanVar(value=False)
            ttk.Checkbutton(self, text="Simulate Printing Process", variable=self.include_element_birth).grid(row=6, column=0, sticky='w', pady=2)
            
            # Mesh size
            ttk.Label(self, text="Mesh Size (mm):").grid(row=7, column=0, sticky='w', pady=5)
            self.mesh_size = ttk.Entry(self, width=8)
            self.mesh_size.insert(0, "5")
            self.mesh_size.grid(row=7, column=1, pady=5)


    class OutputFrame(ttk.LabelFrame):
        """Frame for output configuration."""
        
        def __init__(self, parent, title="Output Settings"):
            ttk.LabelFrame.__init__(self, parent, text=title, padding=10)
            
            ttk.Label(self, text="Model Name:").grid(row=0, column=0, sticky='w', pady=2)
            self.model_name = ttk.Entry(self, width=20)
            self.model_name.insert(0, "3DPC_Model")
            self.model_name.grid(row=0, column=1, pady=2)
            
            ttk.Label(self, text="Save Directory:").grid(row=1, column=0, sticky='w', pady=2)
            self.save_dir = ttk.Entry(self, width=20)
            self.save_dir.insert(0, "./models")
            self.save_dir.grid(row=1, column=1, pady=2)
            
            self.create_job = tk.BooleanVar(value=True)
            ttk.Checkbutton(self, text="Create Analysis Job", variable=self.create_job).grid(row=2, column=0, columnspan=2, sticky='w', pady=5)


    class TDPCGui:
        """Main GUI application for 3DPC model generator."""
        
        def __init__(self, root):
            self.root = root
            self.root.title("3D Printed Concrete Abaqus Model Generator")
            self.root.geometry("600x700")
            
            # Main container
            main_frame = ttk.Frame(root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Title
            title_label = ttk.Label(main_frame, text="3DPC Model Generator", 
                                   font=('Helvetica', 16, 'bold'))
            title_label.grid(row=0, column=0, columnspan=2, pady=10)
            
            # Left column - Model and Material config
            left_frame = ttk.Frame(main_frame)
            left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
            
            self.model_frame = ModelConfigFrame(left_frame)
            self.model_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
            
            self.material_frame = MaterialConfigFrame(left_frame)
            self.material_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
            
            # Right column - Analysis and Output
            right_frame = ttk.Frame(main_frame)
            right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=5)
            
            self.analysis_frame = AnalysisOptionsFrame(right_frame)
            self.analysis_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)
            
            self.output_frame = OutputFrame(right_frame)
            self.output_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
            
            # Status text
            self.status_text = tk.Text(main_frame, height=8, width=70, wrap=tk.WORD)
            self.status_text.grid(row=2, column=0, columnspan=2, pady=10)
            self.status_text.insert('1.0', "Ready to generate model.\n")
            self.status_text.config(state='disabled')
            
            # Buttons
            button_frame = ttk.Frame(main_frame)
            button_frame.grid(row=3, column=0, columnspan=2, pady=10)
            
            ttk.Button(button_frame, text="Generate Model", 
                      command=self.generate_model).grid(row=0, column=0, padx=5)
            ttk.Button(button_frame, text="Validate Config",
                      command=self.validate_config).grid(row=0, column=1, padx=5)
            ttk.Button(button_frame, text="Clear Status",
                      command=self.clear_status).grid(row=0, column=2, padx=5)
            ttk.Button(button_frame, text="Exit",
                      command=root.quit).grid(row=0, column=3, padx=5)
            
            # Configure grid weights
            root.columnconfigure(0, weight=1)
            root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
            main_frame.rowconfigure(1, weight=1)
        
        def log(self, message):
            """Add message to status text."""
            self.status_text.config(state='normal')
            self.status_text.insert('end', message + '\n')
            self.status_text.see('end')
            self.status_text.config(state='disabled')
        
        def clear_status(self):
            """Clear status text."""
            self.status_text.config(state='normal')
            self.status_text.delete('1.0', 'end')
            self.status_text.config(state='disabled')
        
        def get_config_from_gui(self):
            """Extract configuration from GUI inputs."""
            config = {}
            
            # Geometry
            try:
                config['beam_length'] = float(self.model_frame.beam_length.get())
                config['beam_width'] = float(self.model_frame.beam_width.get())
                config['beam_height'] = float(self.model_frame.beam_height.get())
                config['layer_height'] = float(self.model_frame.layer_height.get())
                config['rebar_diameter'] = float(self.model_frame.rebar_diameter.get())
                config['rebar_spacing'] = float(self.model_frame.rebar_spacing.get())
                config['rebar_cover'] = float(self.model_frame.rebar_cover.get())
            except ValueError as e:
                raise ValueError("Invalid geometry parameter: {}".format(e))
            
            # Materials
            try:
                config['concrete_E'] = float(self.material_frame.concrete_E.get())
                config['concrete_strength'] = float(self.material_frame.concrete_strength.get())
                config['steel_E'] = float(self.material_frame.steel_E.get())
            except ValueError as e:
                raise ValueError("Invalid material parameter: {}".format(e))
            
            # Analysis options
            config['analysis_type'] = self.analysis_frame.analysis_type.get()
            config['include_rebar'] = self.analysis_frame.include_rebar.get()
            config['include_cohesive'] = self.analysis_frame.include_cohesive.get()
            config['include_element_birth'] = self.analysis_frame.include_element_birth.get()
            config['mesh_size'] = float(self.analysis_frame.mesh_size.get())
            
            # Output
            config['model_name'] = self.output_frame.model_name.get()
            config['save_dir'] = self.output_frame.save_dir.get()
            config['create_job'] = self.output_frame.create_job.get()
            
            return config
        
        def validate_config(self):
            """Validate current configuration."""
            try:
                config = self.get_config_from_gui()
                
                # Check geometry validity
                if config['beam_height'] % config['layer_height'] != 0:
                    raise ValueError("Beam height must be divisible by layer height")
                
                if config['rebar_diameter'] >= config['beam_height'] - 2 * config['rebar_cover']:
                    raise ValueError("Rebar diameter too large for beam height and cover")
                
                # Check positive values
                for key, value in config.items():
                    if isinstance(value, (int, float)) and value <= 0:
                        raise ValueError("{} must be positive".format(key))
                
                self.log("✓ Configuration is valid")
                return True
                
            except ValueError as e:
                messagebox.showerror("Validation Error", str(e))
                self.log("✗ Validation failed: {}".format(e))
                return False
        
        def generate_model(self):
            """Generate the Abaqus model."""
            if not self.validate_config():
                return
            
            if not ABAQUS_AVAILABLE:
                messagebox.showwarning("Warning", 
                    "Abaqus not available. This GUI must be run within Abaqus CAE.")
                self.log("⚠ Abaqus not available - running in demo mode")
                return
            
            try:
                config = self.get_config_from_gui()
                self.log("Generating model: {}".format(config['model_name']))
                
                # Import and run model creation
                sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
                from main_complete import create_complete_3dpc_model
                
                # Create model
                model = create_complete_3dpc_model()
                
                self.log("✓ Model generated successfully")
                self.log("  Model name: {}".format(config['model_name']))
                self.log("  Analysis type: {}".format(config['analysis_type']))
                
                # Save model
                import os
                save_path = os.path.join(config['save_dir'], config['model_name'] + '.cae')
                if not os.path.exists(config['save_dir']):
                    os.makedirs(config['save_dir'])
                mdb.saveAs(pathName=save_path)
                self.log("✓ Model saved to: {}".format(save_path))
                
                # Create job if requested
                if config['create_job']:
                    job = mdb.Job(name=config['model_name'], model=model.name)
                    self.log("✓ Analysis job created: {}".format(config['model_name']))
                
                messagebox.showinfo("Success", "Model generated successfully!")
                
            except Exception as e:
                messagebox.showerror("Error", "Failed to generate model:\n{}".format(str(e)))
                self.log("✗ Error: {}".format(e))


    def launch_gui():
        """Launch the GUI application."""
        root = tk.Tk()
        app = TDPCGui(root)
        root.mainloop()

else:
    # When tkinter is not available
    def launch_gui():
        print("Error: tkinter not available. GUI cannot be launched.")
        print("Please install tkinter or use the command-line interface.")