# -*- coding: utf-8 -*-
"""
Thermal-mechanical coupled analysis for 3D printed concrete.
Simulates temperature field during printing process and thermal stress.
"""

try:
    from abaqus import *
    from abaqusConstants import *
    ABAQUS_AVAILABLE = True
except ImportError:
    ABAQUS_AVAILABLE = False
    # Mock constants for local testing
    ISOTROPIC = 'ISOTROPIC'
    EMBEDDED_COEFF = 'EMBEDDED_COEFF'
    UNIFORM = 'UNIFORM'
    AMBIENT = 'AMBIENT'
    CONSTANT_THROUGH_THICKNESS = 'CONSTANT_THROUGH_THICKNESS'


def add_thermal_properties(model, config):
    """
    Add thermal properties to concrete material for coupled analysis.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        Updated material object
    """
    # Get existing concrete material
    material = model.materials['Concrete']
    
    # Thermal conductivity (W/m/K) - typical for concrete
    material.Conductivity(
        table=((1.5, ), ),  # W/m/K
        type=ISOTROPIC
    )
    
    # Specific heat (J/kg/K)
    material.SpecificHeat(
        table=((880.0, ), )  # J/kg/K
    )
    
    # Thermal expansion coefficient (1/K)
    material.Expansion(
        table=((1.0e-05, ), ),  # 1/K
        type=ISOTROPIC
    )
    
    return material


def add_steel_thermal_properties(model, config):
    """
    Add thermal properties to steel material.
    
    Args:
        model: Abaqus model object
        config: Config object
        
    Returns:
        Updated material object
    """
    material = model.materials['Steel']
    
    # Thermal conductivity (W/m/K)
    material.Conductivity(
        table=((50.0, ), ),  # W/m/K
        type=ISOTROPIC
    )
    
    # Specific heat (J/kg/K)
    material.SpecificHeat(
        table=((460.0, ), )  # J/kg/K
    )
    
    # Thermal expansion coefficient (1/K)
    material.Expansion(
        table=((1.2e-05, ), ),  # 1/K
        type=ISOTROPIC
    )
    
    return material


def create_thermal_step(model, step_name, previous_step, time_period=60.0):
    """
    Create a coupled thermal-mechanical analysis step.
    
    Args:
        model: Abaqus model object
        step_name: Name of the step
        previous_step: Name of the previous step
        time_period: Time period for the step (s)
        
    Returns:
        Step object
    """
    step = model.CoupledTempDisplacementStep(
        name=step_name,
        previous=previous_step,
        timePeriod=time_period,
        maxNumInc=1000,
        initialInc=0.1,
        minInc=1e-05,
        maxInc=1.0,
        deltmx=10.0,  # Maximum temperature change per increment
        cetol=0.001   # Creep/swelling tolerance
    )
    return step


def create_heat_flux_load(model, step_name, surface, magnitude=1000.0):
    """
    Create surface heat flux load (simulating printing heat source).
    
    Args:
        model: Abaqus model object
        step_name: Name of the step to apply load
        surface: Surface region to apply heat flux
        magnitude: Heat flux magnitude (W/m^2)
        
    Returns:
        Load object
    """
    load = model.SurfaceHeatFlux(
        name='PrintHeat_' + step_name,
        createStepName=step_name,
        region=surface,
        magnitude=magnitude
    )
    return load


def create_convective_film(model, step_name, surface, film_coef=10.0, 
                           sink_temp=25.0):
    """
    Create convective film condition (ambient cooling).
    
    Args:
        model: Abaqus model object
        step_name: Name of the step to apply condition
        surface: Surface region
        film_coef: Film coefficient (W/m^2/K)
        sink_temp: Sink temperature (ambient, Celsius)
        
    Returns:
        Interaction object
    """
    interaction = model.FilmCondition(
        name='Convection_' + step_name,
        createStepName=step_name,
        surface=surface,
        definition=EMBEDDED_COEFF,
        filmCoeff=film_coef,
        filmCoeffAmplitude='',
        sinkTemperature=sink_temp,
        sinkAmplitude='',
        sinkDistributionType=UNIFORM
    )
    return interaction


def create_radiation(model, step_name, surface, emissivity=0.9, 
                     ambient_temp=25.0):
    """
    Create surface radiation condition.
    
    Args:
        model: Abaqus model object
        step_name: Name of the step to apply condition
        surface: Surface region
        emissivity: Surface emissivity (0-1)
        ambient_temp: Ambient temperature (Celsius)
        
    Returns:
        Interaction object
    """
    interaction = model.RadiationToAmbient(
        name='Radiation_' + step_name,
        createStepName=step_name,
        surface=surface,
        radiationType=AMBIENT,
        distributionType=UNIFORM,
        field='',
        emissivity=emissivity,
        ambientTemperature=ambient_temp,
        ambientTemperatureAmp=''
    )
    return interaction


def set_initial_temperature(model, region, temp=25.0):
    """
    Set initial temperature for the model.
    
    Args:
        model: Abaqus model object
        region: Region to set initial temperature
        temp: Initial temperature (Celsius)
        
    Returns:
        Predefined field object
    """
    field = model.Temperature(
        name='InitialTemp',
        createStepName='Initial',
        region=region,
        distributionType=UNIFORM,
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS,
        magnitudes=(temp, )
    )
    return field


def create_print_temperature_field(model, step_name, region, 
                                   print_temp=150.0):
    """
    Create temperature field for newly printed layer.
    
    Args:
        model: Abaqus model object
        step_name: Name of the step
        region: Region of the new layer
        print_temp: Printing temperature (Celsius)
        
    Returns:
        Predefined field object
    """
    field = model.Temperature(
        name='PrintTemp_' + step_name,
        createStepName=step_name,
        region=region,
        distributionType=UNIFORM,
        crossSectionDistribution=CONSTANT_THROUGH_THICKNESS,
        magnitudes=(print_temp, )
    )
    return field


def setup_thermal_analysis(model, assembly, config):
    """
    Setup complete thermal-mechanical coupled analysis.
    
    Args:
        model: Abaqus model object
        assembly: Assembly object
        config: Config object
        
    Returns:
        Dictionary containing created objects
    """
    results = {}
    
    # Add thermal properties to materials
    results['concrete_thermal'] = add_thermal_properties(model, config)
    results['steel_thermal'] = add_steel_thermal_properties(model, config)
    
    # Get all external surfaces for convection/radiation
    # This would need to be customized based on actual geometry
    
    return results


def create_layer_activation_with_temperature(model, step_name, previous_step,
                                             layer_region, config,
                                             print_temp=150.0):
    """
    Create a coupled step that activates a layer with initial temperature.
    
    This combines Model Change with thermal initialization.
    
    Args:
        model: Abaqus model object
        step_name: Name of the step
        previous_step: Name of the previous step
        layer_region: Region of the layer to activate
        config: Config object
        print_temp: Initial temperature of the printed layer
        
    Returns:
        Dictionary with created objects
    """
    results = {}
    
    # Create coupled thermal-mechanical step
    step = create_thermal_step(
        model, step_name, previous_step, 
        time_period=config.layer_wait_time
    )
    results['step'] = step
    
    # Set initial temperature for the new layer
    temp_field = create_print_temperature_field(
        model, step_name, layer_region, print_temp
    )
    results['temperature_field'] = temp_field
    
    return results
