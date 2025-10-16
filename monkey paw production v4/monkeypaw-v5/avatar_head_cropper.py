#!/usr/bin/env python3
"""
Avatar Head Cropping Utility for Full-Body Avatar Processing
Automatically crops head region from full-body avatars for AI animation.
"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, Optional
import subprocess

class AvatarHeadCropper:
    """Handles cropping head regions from full-body avatar images."""
    
    def __init__(self, temp_dir: str = "/tmp"):
        self.temp_dir = Path(temp_dir)
        self.temp_dir.mkdir(exist_ok=True)
        
    def detect_head_region(self, image_path: str) -> Tuple[int, int, int, int]:
        """
        Detect optimal head cropping region from full-body avatar.
        Returns (x, y, width, height) for crop region.
        """
        try:
            # Use ImageMagick to analyze image dimensions
            result = subprocess.run([
                'identify', '-format', '%wx%h', image_path
            ], capture_output=True, text=True, check=True)
            
            dimensions = result.stdout.strip().split('x')
            width, height = int(dimensions[0]), int(dimensions[1])
            
            print(f"📐 Image dimensions: {width}x{height}")
            
            # Calculate head region (top portion of image)
            # Assume head is in upper 1/3 of image, centered horizontally
            head_height = min(height // 3, 512)  # Max 512px height
            head_width = min(width // 2, 512)   # Max 512px width
            
            # Center horizontally
            x = (width - head_width) // 2
            y = 0  # Start from top
            
            print(f"🎯 Detected head region: {x},{y},{head_width},{head_height}")
            return x, y, head_width, head_height
            
        except subprocess.CalledProcessError as e:
            print(f"⚠️ ImageMagick not available, using default crop: {e}")
            # Fallback to default crop
            return 0, 0, 512, 512
        except Exception as e:
            print(f"⚠️ Error detecting head region: {e}")
            return 0, 0, 512, 512
    
    def crop_head(self, avatar_path: str, output_path: str, 
                  crop_region: Optional[Tuple[int, int, int, int]] = None) -> bool:
        """
        Crop head region from full-body avatar.
        
        Args:
            avatar_path: Path to full-body avatar image
            output_path: Path for cropped head image
            crop_region: Optional (x, y, width, height) tuple
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not os.path.exists(avatar_path):
                print(f"❌ Avatar file not found: {avatar_path}")
                return False
            
            # Detect head region if not provided
            if crop_region is None:
                crop_region = self.detect_head_region(avatar_path)
            
            x, y, width, height = crop_region
            
            # Use ImageMagick to crop
            cmd = [
                'convert', avatar_path,
                '-crop', f'{width}x{height}+{x}+{y}',
                '-resize', '512x512^',  # Resize to 512x512, maintaining aspect ratio
                '-gravity', 'center',
                '-extent', '512x512',   # Extend to exact 512x512
                output_path
            ]
            
            print(f"✂️ Cropping head: {avatar_path} -> {output_path}")
            print(f"📐 Crop region: {width}x{height} at ({x},{y})")
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                print(f"✅ Head cropped successfully: {output_path}")
                return True
            else:
                print(f"❌ Cropped file is empty or missing: {output_path}")
                return False
                
        except subprocess.CalledProcessError as e:
            print(f"❌ ImageMagick crop failed: {e}")
            print(f"stderr: {e.stderr}")
            return False
        except Exception as e:
            print(f"❌ Unexpected error during crop: {e}")
            return False
    
    def validate_crop(self, cropped_path: str) -> bool:
        """Validate that cropped head image is suitable for AI animation."""
        try:
            if not os.path.exists(cropped_path):
                return False
            
            # Check file size (should be reasonable)
            size = os.path.getsize(cropped_path)
            if size < 1000:  # Less than 1KB is suspicious
                print(f"⚠️ Cropped image very small: {size} bytes")
                return False
            
            # Use ImageMagick to verify dimensions
            result = subprocess.run([
                'identify', '-format', '%wx%h', cropped_path
            ], capture_output=True, text=True, check=True)
            
            dimensions = result.stdout.strip()
            if dimensions == "512x512":
                print(f"✅ Valid crop: {dimensions}")
                return True
            else:
                print(f"⚠️ Unexpected crop dimensions: {dimensions}")
                return False
                
        except Exception as e:
            print(f"⚠️ Error validating crop: {e}")
            return False

def main():
    """Command line interface for head cropping."""
    if len(sys.argv) < 3:
        print("Usage: python avatar_head_cropper.py <avatar_path> <output_path> [x,y,width,height]")
        print("Example: python avatar_head_cropper.py ~/Downloads/woman.png ~/tmp/head.png")
        print("Optional: python avatar_head_cropper.py ~/Downloads/woman.png ~/tmp/head.png 100,50,400,400")
        sys.exit(1)
    
    avatar_path = sys.argv[1]
    output_path = sys.argv[2]
    
    # Parse optional crop region
    crop_region = None
    if len(sys.argv) > 3:
        try:
            coords = sys.argv[3].split(',')
            if len(coords) == 4:
                crop_region = tuple(int(x) for x in coords)
                print(f"🎯 Using custom crop region: {crop_region}")
        except ValueError:
            print("⚠️ Invalid crop region format, using auto-detection")
    
    # Create cropper and process
    cropper = AvatarHeadCropper()
    
    success = cropper.crop_head(avatar_path, output_path, crop_region)
    
    if success:
        # Validate the result
        if cropper.validate_crop(output_path):
            print("🎉 Head cropping completed successfully!")
            sys.exit(0)
        else:
            print("⚠️ Cropping completed but validation failed")
            sys.exit(1)
    else:
        print("❌ Head cropping failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
