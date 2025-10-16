#!/usr/bin/env python3
"""
Blender Production Script for Full-Body Avatar Compositing
Integrates animated head with full-body avatar using professional compositing workflow.
"""

import bpy
import os
import sys
import json

print("--- Starting Blender Production Script ---")

def get_file_paths():
    """Extract file paths from command line arguments."""
    argv = sys.argv
    argv = argv[argv.index("--") + 1:]
    
    try:
        background_path = argv[argv.index("--background") + 1]
        avatar_path = argv[argv.index("--avatar") + 1]
        head_path = argv[argv.index("--head") + 1]
        output_path = argv[argv.index("--output") + 1]
        
        # Optional head positioning parameters
        head_x = float(argv[argv.index("--head-x") + 1]) if "--head-x" in argv else 0.0
        head_y = float(argv[argv.index("--head-y") + 1]) if "--head-y" in argv else 150.0
        head_scale = float(argv[argv.index("--head-scale") + 1]) if "--head-scale" in argv else 1.0
        
        return {
            'background': background_path,
            'avatar': avatar_path,
            'head': head_path,
            'output': output_path,
            'head_x': head_x,
            'head_y': head_y,
            'head_scale': head_scale
        }
    except (ValueError, IndexError) as e:
        print(f"❌ Error parsing arguments: {e}")
        print("Required: --background, --avatar, --head, --output")
        print("Optional: --head-x, --head-y, --head-scale")
        sys.exit(1)

def setup_scene():
    """Configure Blender scene for video rendering."""
    scene = bpy.context.scene
    
    # Video output settings
    scene.render.image_settings.file_format = 'FFMPEG'
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'H264'
    scene.render.ffmpeg.constant_rate_factor = 'HIGH'
    
    # Resolution (1080p)
    scene.render.resolution_x = 1920
    scene.render.resolution_y = 1080
    scene.render.resolution_percentage = 100
    
    # Enable compositing
    scene.use_nodes = True
    tree = scene.node_tree
    
    # Clear existing nodes
    for node in tree.nodes:
        tree.nodes.remove(node)
    
    return scene, tree

def create_compositing_nodes(tree, paths):
    """Create and configure compositing nodes for multi-layer scene."""
    
    # Background layer
    bg_node = tree.nodes.new(type='CompositorNodeImage')
    bg_node.name = "Background"
    bg_node.location = (0, 400)
    try:
        bg_node.image = bpy.data.images.load(paths['background'])
        print(f"✅ Loaded background: {paths['background']}")
    except Exception as e:
        print(f"❌ Failed to load background: {e}")
        return None
    
    # Full-body avatar layer
    avatar_node = tree.nodes.new(type='CompositorNodeImage')
    avatar_node.name = "Avatar"
    avatar_node.location = (0, 0)
    try:
        avatar_node.image = bpy.data.images.load(paths['avatar'])
        print(f"✅ Loaded avatar: {paths['avatar']}")
    except Exception as e:
        print(f"❌ Failed to load avatar: {e}")
        return None
    
    # Animated head layer
    head_node = tree.nodes.new(type='CompositorNodeMovieClip')
    head_node.name = "AnimatedHead"
    head_node.location = (0, -400)
    try:
        head_node.clip = bpy.data.movieclips.load(paths['head'])
        print(f"✅ Loaded animated head: {paths['head']}")
    except Exception as e:
        print(f"❌ Failed to load animated head: {e}")
        return None
    
    # Set frame range based on head video
    scene = bpy.context.scene
    scene.frame_start = 1
    scene.frame_end = head_node.clip.frame_duration
    print(f"📹 Frame range: {scene.frame_start} to {scene.frame_end}")
    
    # Head positioning and scaling
    transform_node = tree.nodes.new(type='CompositorNodeTransform')
    transform_node.name = "HeadTransform"
    transform_node.location = (200, -400)
    transform_node.inputs['X'].default_value = paths['head_x']
    transform_node.inputs['Y'].default_value = paths['head_y']
    transform_node.inputs['X Scale'].default_value = paths['head_scale']
    transform_node.inputs['Y Scale'].default_value = paths['head_scale']
    
    # Composite head onto avatar body
    head_on_body_node = tree.nodes.new(type='CompositorNodeAlphaOver')
    head_on_body_node.name = "HeadOnBody"
    head_on_body_node.location = (400, 0)
    head_on_body_node.use_premultiply = True
    
    # Final composite (avatar on background)
    final_composite_node = tree.nodes.new(type='CompositorNodeAlphaOver')
    final_composite_node.name = "FinalComposite"
    final_composite_node.location = (600, 200)
    final_composite_node.use_premultiply = True
    
    # Output node
    composite_node = tree.nodes.new(type='CompositorNodeComposite')
    composite_node.name = "Output"
    composite_node.location = (800, 200)
    
    return {
        'bg': bg_node,
        'avatar': avatar_node,
        'head': head_node,
        'transform': transform_node,
        'head_on_body': head_on_body_node,
        'final': final_composite_node,
        'output': composite_node
    }

def link_nodes(tree, nodes):
    """Connect compositing nodes in the correct order."""
    # Head -> Transform
    tree.links.new(nodes['head'].outputs['Image'], nodes['transform'].inputs['Image'])
    
    # Avatar + Transformed Head -> HeadOnBody
    tree.links.new(nodes['avatar'].outputs['Image'], nodes['head_on_body'].inputs[1])
    tree.links.new(nodes['transform'].outputs['Image'], nodes['head_on_body'].inputs[2])
    
    # Background + HeadOnBody -> Final
    tree.links.new(nodes['bg'].outputs['Image'], nodes['final'].inputs[1])
    tree.links.new(nodes['head_on_body'].outputs['Image'], nodes['final'].inputs[2])
    
    # Final -> Output
    tree.links.new(nodes['final'].outputs['Image'], nodes['output'].inputs['Image'])
    
    print("✅ Node connections established")

def render_video(output_path):
    """Render the final composite video."""
    scene = bpy.context.scene
    scene.render.filepath = output_path
    
    print(f"🎬 Rendering video to: {output_path}")
    print(f"📊 Resolution: {scene.render.resolution_x}x{scene.render.resolution_y}")
    print(f"🎞️ Frames: {scene.frame_start}-{scene.frame_end}")
    
    try:
        bpy.ops.render.render(animation=True)
        print(f"✅ Video saved successfully: {output_path}")
        return True
    except Exception as e:
        print(f"❌ Render failed: {e}")
        return False

def main():
    """Main execution function."""
    try:
        # Get file paths from command line
        paths = get_file_paths()
        print(f"📁 Input files: {json.dumps(paths, indent=2)}")
        
        # Setup Blender scene
        scene, tree = setup_scene()
        
        # Create compositing nodes
        nodes = create_compositing_nodes(tree, paths)
        if not nodes:
            print("❌ Failed to create compositing nodes")
            sys.exit(1)
        
        # Link nodes together
        link_nodes(tree, nodes)
        
        # Render final video
        success = render_video(paths['output'])
        
        if success:
            print("🎉 Blender production script completed successfully!")
            sys.exit(0)
        else:
            print("❌ Blender production script failed")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
