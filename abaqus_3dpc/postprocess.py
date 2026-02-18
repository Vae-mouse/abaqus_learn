# -*- coding: utf-8 -*-
"""
Post-processing module for 3D printed concrete simulation results.
Extracts and visualizes key results from ODB files.
"""

from abaqus import *
from abaqusConstants import *
from odbAccess import *
import os


def open_odb_file(odb_path):
    """
    Open ODB file for post-processing.
    
    Args:
        odb_path: Path to .odb file
        
    Returns:
        Odb object
    """
    if not os.path.exists(odb_path):
        raise FileNotFoundError("ODB file not found: %s" % odb_path)
    
    odb = openOdb(path=odb_path)
    print("Opened ODB: %s" % odb_path)
    print("  Analysis title: %s" % odb.analysisTitle)
    print("  Number of steps: %d" % len(odb.steps))
    
    return odb


def extract_step_results(odb, step_name):
    """
    Extract results from a specific analysis step.
    
    Args:
        odb: Odb object
        step_name: Name of the step
        
    Returns:
        Dictionary with step results
    """
    if step_name not in odb.steps.keys():
        raise ValueError("Step '%s' not found in ODB" % step_name)
    
    step = odb.steps[step_name]
    results = {
        'name': step_name,
        'description': step.description,
        'frames': []
    }
    
    print("\nExtracting results for step: %s" % step_name)
    print("  Number of frames: %d" % len(step.frames))
    
    # Extract data from each frame
    for i, frame in enumerate(step.frames):
        frame_data = {
            'frame_id': i,
            'time': frame.frameValue,
            'increment': frame.incrementNumber
        }
        results['frames'].append(frame_data)
    
    return results


def extract_stress_strain(odb, instance_name='BEAM-1', step_name=None):
    """
    Extract stress and strain data from the model.
    
    Args:
        odb: Odb object
        instance_name: Name of the part instance
        step_name: Specific step (None for all steps)
        
    Returns:
        Dictionary with stress-strain data
    """
    data = {
        'steps': {},
        'max_stress': 0.0,
        'max_strain': 0.0
    }
    
    steps_to_process = [step_name] if step_name else odb.steps.keys()
    
    for step_name in steps_to_process:
        step = odb.steps[step_name]
        step_data = []
        
        for frame in step.frames:
            # Get stress field
            if frame.fieldOutputs.has_key('S'):
                stress_field = frame.fieldOutputs['S']
                stress_values = [value.mises for value in stress_field.values]
                max_stress = max(stress_values) if stress_values else 0.0
            else:
                max_stress = 0.0
            
            # Get strain field
            if frame.fieldOutputs.has_key('E'):
                strain_field = frame.fieldOutputs['E']
                strain_values = [value.maxPrincipal for value in strain_field.values]
                max_strain = max(strain_values) if strain_values else 0.0
            else:
                max_strain = 0.0
            
            step_data.append({
                'time': frame.frameValue,
                'max_stress': max_stress,
                'max_strain': max_strain
            })
            
            # Update global maxima
            data['max_stress'] = max(data['max_stress'], max_stress)
            data['max_strain'] = max(data['max_strain'], max_strain)
        
        data['steps'][step_name] = step_data
    
    return data


def extract_displacement(odb, instance_name='BEAM-1', node_set_name=None):
    """
    Extract displacement data.
    
    Args:
        odb: Odb object
        instance_name: Name of the part instance
        node_set_name: Optional node set to extract from
        
    Returns:
        Dictionary with displacement data
    """
    data = {
        'max_displacement': 0.0,
        'displacements': []
    }
    
    # Get last step and last frame
    last_step_name = list(odb.steps.keys())[-1]
    last_step = odb.steps[last_step_name]
    last_frame = last_step.frames[-1]
    
    if last_frame.fieldOutputs.has_key('U'):
        disp_field = last_frame.fieldOutputs['U']
        
        for value in disp_field.values:
            magnitude = value.magnitude
            data['displacements'].append({
                'node': value.nodeLabel,
                'magnitude': magnitude,
                'components': (value.data[0], value.data[1], value.data[2])
            })
            data['max_displacement'] = max(data['max_displacement'], magnitude)
    
    return data


def extract_rebar_stress(odb, instance_name='REBAR-1'):
    """
    Extract stress in rebar elements.
    
    Args:
        odb: Odb object
        instance_name: Name of the rebar instance
        
    Returns:
        Dictionary with rebar stress data
    """
    data = {
        'max_stress': 0.0,
        'min_stress': float('inf'),
        'avg_stress': 0.0,
        'stresses': []
    }
    
    # Get last step and last frame
    last_step_name = list(odb.steps.keys())[-1]
    last_step = odb.steps[last_step_name]
    last_frame = last_step.frames[-1]
    
    if last_frame.fieldOutputs.has_key('S'):
        stress_field = last_frame.fieldOutputs['S']
        
        stresses = []
        for value in stress_field.values:
            if hasattr(value, 'mises'):
                stress = value.mises
            else:
                stress = value.data[0]  # Axial stress for truss
            
            stresses.append(stress)
            data['max_stress'] = max(data['max_stress'], stress)
            data['min_stress'] = min(data['min_stress'], stress)
        
        if stresses:
            data['avg_stress'] = sum(stresses) / len(stresses)
            data['stresses'] = stresses
    
    return data


def generate_report(odb_path, output_path=None):
    """
    Generate a comprehensive analysis report.
    
    Args:
        odb_path: Path to ODB file
        output_path: Optional path to save report
        
    Returns:
        Report string
    """
    odb = open_odb_file(odb_path)
    
    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("3D Printed Concrete Analysis Report")
    report_lines.append("=" * 70)
    report_lines.append("ODB File: %s" % odb_path)
    report_lines.append("")
    
    # Model information
    report_lines.append("Model Information:")
    report_lines.append("  Analysis title: %s" % odb.analysisTitle)
    report_lines.append("  Number of steps: %d" % len(odb.steps))
    report_lines.append("")
    
    # Step summaries
    report_lines.append("Analysis Steps:")
    for step_name in odb.steps.keys():
        step = odb.steps[step_name]
        report_lines.append("  %s:" % step_name)
        report_lines.append("    Description: %s" % step.description)
        report_lines.append("    Frames: %d" % len(step.frames))
        if step.frames:
            report_lines.append("    Total time: %.4f" % step.frames[-1].frameValue)
    report_lines.append("")
    
    # Extract stress-strain data
    try:
        stress_strain = extract_stress_strain(odb)
        report_lines.append("Stress Analysis:")
        report_lines.append("  Maximum Mises stress: %.2f MPa" % stress_strain['max_stress'])
        report_lines.append("  Maximum principal strain: %.6f" % stress_strain['max_strain'])
        report_lines.append("")
    except Exception as e:
        report_lines.append("Stress analysis failed: %s" % str(e))
        report_lines.append("")
    
    # Extract displacement
    try:
        disp = extract_displacement(odb)
        report_lines.append("Displacement Analysis:")
        report_lines.append("  Maximum displacement: %.4f mm" % disp['max_displacement'])
        report_lines.append("")
    except Exception as e:
        report_lines.append("Displacement analysis failed: %s" % str(e))
        report_lines.append("")
    
    # Extract rebar stress
    try:
        rebar = extract_rebar_stress(odb)
        report_lines.append("Rebar Stress Analysis:")
        report_lines.append("  Maximum stress: %.2f MPa" % rebar['max_stress'])
        report_lines.append("  Minimum stress: %.2f MPa" % rebar['min_stress'])
        report_lines.append("  Average stress: %.2f MPa" % rebar['avg_stress'])
        report_lines.append("")
    except Exception as e:
        report_lines.append("Rebar stress analysis failed: %s" % str(e))
        report_lines.append("")
    
    report_lines.append("=" * 70)
    
    # Close ODB
    odb.close()
    
    # Generate report string
    report = "\n".join(report_lines)
    
    # Save to file if requested
    if output_path:
        with open(output_path, 'w') as f:
            f.write(report)
        print("Report saved to: %s" % output_path)
    
    return report


def create_stress_contour_plot(odb_path, step_name, frame_idx=-1, output_path=None):
    """
    Create stress contour plot from ODB.
    
    Args:
        odb_path: Path to ODB file
        step_name: Step name to plot
        frame_idx: Frame index (-1 for last frame)
        output_path: Path to save image
    """
    import visualization
    
    # Open ODB
    odb = open_odb_file(odb_path)
    
    # Create viewport
    vp = session.Viewport(name='Stress Plot')
    vp.setValues(displayedObject=odb)
    
    # Set plot options
    vp.odbDisplay.setValues(step=step_name)
    vp.odbDisplay.setFrame(step=step_name, frame=frame_idx)
    vp.odbDisplay.display.setValues(plotState=(CONTOURS_ON_DEF,))
    vp.odbDisplay.setPrimaryVariable(
        variableLabel='S',
        outputPosition=INTEGRATION_POINT,
        refinement=(INVARIANT, 'Mises')
    )
    
    # Save image if path provided
    if output_path:
        session.printToFile(
            fileName=output_path,
            format=PNG,
            canvasObjects=(vp,)
        )
        print("Stress contour plot saved to: %s" % output_path)
    
    odb.close()


def main():
    """Example usage of post-processing functions."""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python postprocess.py <odb_file_path>")
        return
    
    odb_path = sys.argv[1]
    
    if not os.path.exists(odb_path):
        print("Error: ODB file not found: %s" % odb_path)
        return
    
    # Generate report
    report = generate_report(odb_path)
    print(report)
    
    # Save report to file
    report_path = odb_path.replace('.odb', '_report.txt')
    generate_report(odb_path, report_path)


if __name__ == "__main__":
    main()
