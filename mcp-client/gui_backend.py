"""
GUI Backend Module
Automatic detection and management of GUI backends for plot display
Supports: Tkinter, PyQt5, Jupyter, VS Code
"""
import os
import sys
import platform
import subprocess
import logging
import tempfile
from typing import Optional

logger = logging.getLogger(__name__)

# Windows-specific flag to prevent console window
if platform.system() == 'Windows':
    CREATE_NO_WINDOW = 0x08000000
else:
    CREATE_NO_WINDOW = 0


class GUIBackend:
    """Detect and use available GUI backend for displaying plots"""
    
    def __init__(self):
        """Initialize GUI backend with auto-detection"""
        self.backend = self._detect_backend()
        self.current_process = None  # Track current subprocess
        logger.info(f"GUI Backend detected: {self.backend or 'None'}")
    
    def _detect_backend(self) -> Optional[str]:
        """
        Auto-detect which GUI backend is available
        
        Priority order:
        1. Tkinter (usually available)
        2. PyQt5 (if installed)
        3. Jupyter (if in notebook)
        4. VS Code (if in integrated terminal)
        
        Returns:
            Backend name or None
        """
        # Check Tkinter first (most common)
        try:
            import tkinter
            # Test if display is available
            if self._has_display():
                logger.debug("Tkinter backend available")
                return "tkinter"
        except (ImportError, RuntimeError):
            logger.debug("Tkinter not available")
        
        # Check PyQt5
        try:
            from PyQt5 import QtWidgets
            if self._has_display():
                logger.debug("PyQt5 backend available")
                return "pyqt5"
        except ImportError:
            logger.debug("PyQt5 not available")
        
        # Check if running in Jupyter
        if self._is_jupyter():
            logger.debug("Jupyter environment detected")
            return "jupyter"
        
        # Check if running in VS Code
        if self._is_vscode():
            logger.debug("VS Code environment detected")
            return "vscode"
        
        logger.warning("No GUI backend available")
        return None
    
    def _has_display(self) -> bool:
        """Check if display/GUI is available"""
        # Windows always has GUI
        if platform.system() == 'Windows':
            return True
        
        # macOS always has GUI
        if platform.system() == 'Darwin':
            return True
        
        # Linux: Check DISPLAY variable
        if os.environ.get('DISPLAY'):
            return True
        
        # Check if in SSH without X forwarding
        if os.environ.get('SSH_CONNECTION') and not os.environ.get('DISPLAY'):
            return False
        
        # WSL2 check
        if 'microsoft' in platform.uname().release.lower():
            if not os.environ.get('DISPLAY'):
                return False
        
        return False
    
    def _is_jupyter(self) -> bool:
        """Check if running in Jupyter notebook"""
        try:
            from IPython import get_ipython
            ipython = get_ipython()
            if ipython is not None:
                return 'IPKernelApp' in ipython.config
        except ImportError:
            pass
        return False
    
    def _is_vscode(self) -> bool:
        """Check if running in VS Code terminal"""
        return os.getenv('TERM_PROGRAM') == 'vscode'
    
    def can_display_gui(self) -> bool:
        """Check if GUI display is possible"""
        return self.backend is not None
    
    def open_image(self, image_path: str, title: Optional[str] = None) -> bool:
        """
        Open image in GUI window using detected backend
        
        Args:
            image_path: Path to PNG file
            title: Window title (optional)
            
        Returns:
            True if successfully opened, False otherwise
        """
        if not os.path.exists(image_path):
            logger.error(f"Image file not found: {image_path}")
            return False
        
        if not self.backend:
            logger.warning("No GUI backend available")
            return False
        
        # Close previous window if exists
        self._close_current_window()
        
        # Route to appropriate backend
        try:
            if self.backend == "tkinter":
                return self._open_with_tkinter_subprocess(image_path, title)
            elif self.backend == "pyqt5":
                return self._open_with_pyqt(image_path, title)
            elif self.backend == "jupyter":
                return self._display_in_jupyter(image_path)
            elif self.backend == "vscode":
                return self._open_with_vscode(image_path)
        except Exception as e:
            logger.error(f"Error opening image with {self.backend}: {e}")
            return False
        
        return False
    
    def _close_current_window(self):
        """Close currently open window if exists"""
        if self.current_process and self.current_process.poll() is None:
            try:
                self.current_process.terminate()
                self.current_process.wait(timeout=1)
            except Exception as e:
                logger.debug(f"Error closing window: {e}")
            finally:
                self.current_process = None
    
    def _open_with_tkinter_subprocess(self, image_path: str, title: Optional[str] = None) -> bool:
        """
        Open image using Tkinter in completely detached subprocess
        
        Args:
            image_path: Path to image
            title: Window title
            
        Returns:
            True if successful
        """
        try:
            # ==================== SUBPROCESS SCRIPT ====================
            # Script runs in completely isolated process
            script = f'''
import sys
import os

# CRITICAL: Redirect ALL output immediately
sys.stdout = open(os.devnull, 'w')
sys.stderr = open(os.devnull, 'w')

# Now import GUI libraries (no output possible)
try:
    import tkinter as tk
    from PIL import Image, ImageTk
except ImportError:
    sys.exit(1)

try:
    root = tk.Tk()
    root.title({repr(title or f"Plot Preview - {os.path.basename(image_path)}")})
    
    img = Image.open({repr(image_path)})
    
    max_width, max_height = 1200, 800
    if img.width > max_width or img.height > max_height:
        ratio = min(max_width / img.width, max_height / img.height)
        new_size = (int(img.width * ratio), int(img.height * ratio))
        img = img.resize(new_size, Image.Resampling.LANCZOS)
    
    photo = ImageTk.PhotoImage(img)
    
    label = tk.Label(root, image=photo)
    label.image = photo
    label.pack()
    
    btn_frame = tk.Frame(root)
    btn_frame.pack(pady=5)
    
    close_btn = tk.Button(btn_frame, text="Close (ESC)", command=root.destroy, padx=20, pady=5)
    close_btn.pack()
    
    root.bind('<Escape>', lambda e: root.destroy())
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{{width}}x{{height}}+{{x}}+{{y}}')
    
    root.mainloop()
    
except Exception:
    sys.exit(1)
'''
            # ==================== END SCRIPT ====================
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                f.write(script)
                temp_script = f.name
            
            logger.debug(f"Created temp script: {temp_script}")
            
            # ==================== COMPLETE ISOLATION ====================
            if platform.system() == 'Windows':
                # Windows: Use pythonw.exe + CREATE_NO_WINDOW
                python_exe = sys.executable.replace('python.exe', 'pythonw.exe')
                if not os.path.exists(python_exe):
                    python_exe = sys.executable
                
                # STARTUPINFO to hide window
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                
                self.current_process = subprocess.Popen(
                    [python_exe, temp_script],
                    stdout=subprocess.DEVNULL,       # No stdout inheritance
                    stderr=subprocess.DEVNULL,       # No stderr inheritance
                    stdin=subprocess.DEVNULL,        # No stdin inheritance
                    creationflags=CREATE_NO_WINDOW | subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS,
                    startupinfo=startupinfo,
                    close_fds=True,
                    shell=False
                )
            else:
                # Linux/macOS: Use setsid for complete detachment
                self.current_process = subprocess.Popen(
                    [sys.executable, temp_script],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True,
                    close_fds=True,
                    preexec_fn=os.setsid if hasattr(os, 'setsid') else None,
                    shell=False
                )
            # ==================== END ISOLATION ====================
            
            logger.info(f"✅ GUI window launched safely (detached from TUI): {os.path.basename(image_path)}")
            logger.debug(f"Process PID: {self.current_process.pid}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to launch GUI window: {e}", exc_info=True)
            return False
    
    def _open_with_pyqt(self, image_path: str, title: Optional[str] = None) -> bool:
        """Open image using PyQt5 (not implemented yet)"""
        logger.warning("PyQt5 backend not implemented yet")
        return False
    
    def _display_in_jupyter(self, image_path: str) -> bool:
        """Display image inline in Jupyter notebook"""
        try:
            from IPython.display import Image, display
            display(Image(filename=image_path))
            
            logger.info(f"Displayed image in Jupyter: {os.path.basename(image_path)}")
            return True
        except Exception as e:
            logger.error(f"Jupyter error: {e}")
            return False
    
    def _open_with_vscode(self, image_path: str) -> bool:
        """Open image in VS Code image viewer"""
        try:
            subprocess.run(['code', '--goto', image_path], check=True)
            
            logger.info(f"Opened image in VS Code: {os.path.basename(image_path)}")
            return True
        except Exception as e:
            logger.error(f"VS Code error: {e}")
            return False
    
    def get_backend_info(self) -> dict:
        """Get information about current backend"""
        return {
            "backend": self.backend,
            "available": self.can_display_gui(),
            "has_display": self._has_display(),
            "is_jupyter": self._is_jupyter(),
            "is_vscode": self._is_vscode(),
            "process_active": self.current_process is not None and self.current_process.poll() is None,
            "process_pid": self.current_process.pid if self.current_process else None,
            "platform": platform.system(),
        }

_gui_backend = None

# Singleton instance
_gui_backend = None

def get_gui_backend() -> GUIBackend:
    """Get or create singleton GUI backend instance"""
    global _gui_backend
    if _gui_backend is None:
        _gui_backend = GUIBackend()
    return _gui_backend

# Convenience function
def can_display_gui() -> bool:
    """Quick check if GUI display is available"""
    backend = get_gui_backend()
    return backend.can_display_gui()