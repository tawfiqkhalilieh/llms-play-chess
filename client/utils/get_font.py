import pygame

class MockFont:
    def __init__(self, size):
        self.size_val = size
        self.height = size

    def render(self, text, antialias, color):
        # Create a surface representing the text
        # Since we can't render text, we'll return a colored rectangle
        # or a transparent one.
        # Let's try to estimate width based on char count to keep layout somewhat sane
        width = len(text) * (self.size_val // 2)
        if width == 0: width = 1
        s = pygame.Surface((width, self.height), pygame.SRCALPHA)
        # Fill with a color close to the requested one, or just white for visibility
        # But wait, color is passed in.
        s.fill(color) 
        return s

    def size(self, text):
        width = len(text) * (self.size_val // 2)
        return (width, self.height)

    def get_linesize(self):
        return self.height

import pygame
import os

try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

_font_warning_printed = False

class PILFont:
    def __init__(self, size):
        self.size_val = size
        self.font = self._load_font(size)
        
        # Calculate height for get_linesize using a dummy character
        dummy_bbox = self.get_bbox("Ag")
        self.height = dummy_bbox[3] - dummy_bbox[1] + 4 # Add a little padding

    def _load_font(self, size):
        # List of common font paths to try
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/TTF/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
            "/usr/share/fonts/TTF/LiberationSans-Regular.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
            "/usr/share/fonts/TTF/FreeSans.ttf",
            "/usr/share/fonts/noto/NotoSans-Regular.ttf",
            "/usr/share/fonts/TTF/NotoSans-Regular.ttf",
        ]
        
        # Try to find a system font
        for path in font_paths:
            if os.path.exists(path):
                try:
                    return ImageFont.truetype(path, size)
                except Exception:
                    continue
        
        # Search recursively in common dirs if exact paths failed
        common_dirs = ["/usr/share/fonts", "/usr/local/share/fonts", os.path.expanduser("~/.local/share/fonts")]
        for font_dir in common_dirs:
            if not os.path.exists(font_dir): continue
            for root, dirs, files in os.walk(font_dir):
                for file in files:
                    if file.lower().endswith(".ttf") and "sans" in file.lower() and "mono" not in file.lower():
                         try:
                             return ImageFont.truetype(os.path.join(root, file), size)
                         except Exception:
                             pass

        # Fallback to default (might be ugly/small but works)
        try:
            return ImageFont.load_default()
        except Exception:
            return None

    def get_bbox(self, text):
        if not self.font: return (0,0,1,1)
        # Create a dummy image to get a drawing context
        img = Image.new('RGBA', (1, 1))
        draw = ImageDraw.Draw(img)
        try:
            return draw.textbbox((0, 0), text, font=self.font)
        except AttributeError:
             # Older PIL versions
             return draw.textsize(text, font=self.font)

    def render(self, text, antialias, color):
        if not self.font:
             # Absolute fallback if PIL font failed to load completely
             s = pygame.Surface((len(text)*10, self.size_val), pygame.SRCALPHA)
             s.fill(color)
             return s

        bbox = self.get_bbox(text)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        
        # Ensure positive dimensions
        width = max(1, width)
        height = max(1, height)

        # Create PIL image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # PIL colors can be tuple or string. Pygame Color is tuple-like.
        # Ensure alpha
        if len(color) == 3:
            fill_color = color + (255,)
        else:
            fill_color = color

        # Draw text. Offset by -bbox[0], -bbox[1] to align to top-left of tight bounding box
        draw.text((-bbox[0], -bbox[1]), text, font=self.font, fill=fill_color)
        
        # Convert to pygame surface
        mode = img.mode
        size = img.size
        data = img.tobytes()
        return pygame.image.fromstring(data, size, mode)

    def size(self, text):
        bbox = self.get_bbox(text)
        return (bbox[2] - bbox[0], bbox[3] - bbox[1])

    def get_linesize(self):
        return self.height

def get_font(size):
    global _font_warning_printed
    try:
        # Try native pygame font first
        if not pygame.font.get_init():
            pygame.font.init()
        font_path = pygame.font.match_font('helvetica')
        if font_path:
            return pygame.font.Font(font_path, size)
        return pygame.font.Font(None, size)
    except Exception as e:
        if not _font_warning_printed:
            print(f"Warning: Pygame font module unavailable ({e}). Using PIL fallback.")
            _font_warning_printed = True
        
        if HAS_PIL:
            return PILFont(size)
        else:
            print("Error: PIL not available for font fallback.")
            # Absolute minimal dummy
            class DummyFont:
                def render(self, text, *args):
                    return pygame.Surface((1,1))
                def size(self, text): return (1,1)
                def get_linesize(self): return 1
            return DummyFont()