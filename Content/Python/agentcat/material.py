import unreal
from . import editor

def inject_custom_hlsl_node(material_or_function, hlsl_code, node_name="CustomNode", inputs=None, 
                            output_type=unreal.CustomMaterialOutputType.CMOT_FLOAT4, 
                            node_pos=(-400, -100), auto_reopen=True):
    """
    Inject a custom HLSL expression node into a Material or MaterialFunction.
    
    Args:
        material_or_function (unreal.Material or unreal.MaterialFunction): The target material asset.
        hlsl_code (str): The raw HLSL shader code.
        node_name (str): The name/description for the custom node.
        inputs (list): List of input pin names.
        output_type (unreal.CustomMaterialOutputType): The output type of the node.
        node_pos (tuple): X, Y editor node positions.
        auto_reopen (bool): If True, programmatically closes and reopens the editor to repaint UI.
        
    Returns:
        unreal.MaterialExpressionCustom: The created custom node.
    """
    if not material_or_function:
        raise ValueError("material_or_function is required")
        
    is_material = isinstance(material_or_function, unreal.Material)
    is_function = isinstance(material_or_function, unreal.MaterialFunction)
    
    if not (is_material or is_function):
        raise TypeError("Target asset must be unreal.Material or unreal.MaterialFunction")
        
    # Create the custom node expression
    if is_material:
        custom_node = unreal.MaterialEditingLibrary.create_material_expression(
            material_or_function, unreal.MaterialExpressionCustom, node_pos[0], node_pos[1]
        )
    else:
        custom_node = unreal.MaterialEditingLibrary.create_material_expression_in_function(
            material_or_function, unreal.MaterialExpressionCustom, node_pos[0], node_pos[1]
        )
        
    # Set properties
    custom_node.set_editor_property('code', hlsl_code)
    custom_node.set_editor_property('output_type', output_type)
    custom_node.set_editor_property('description', node_name)
    custom_node.set_editor_property('desc', f"{node_name} injected by AgentCat")
    
    # Configure input pins
    if inputs:
        custom_inputs = []
        for input_name in inputs:
            ci = unreal.CustomInput()
            ci.set_editor_property('input_name', input_name)
            custom_inputs.append(ci)
        custom_node.set_editor_property('inputs', custom_inputs)
        
    # Layout and update
    if is_material:
        unreal.MaterialEditingLibrary.layout_material_expressions(material_or_function)
    else:
        unreal.MaterialEditingLibrary.update_material_function(material_or_function)
        
    # Force UI refresh if requested
    if auto_reopen:
        editor.reopen_editor(material_or_function)
        
    return custom_node
