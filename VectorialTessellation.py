import tkinter as tk
from tkinter import scrolledtext, messagebox, font, filedialog
import numpy as np
import math
import threading
import os
import sys

class VectorialTessellator:
    """
    An engine for the structural analysis and compression of a string
    based on the principles of Vectorial Tessellation.
    """

    def __init__(self, text: str, update_callback=None):
        self.original_text = text
        self.length = len(text)
        self.claimed_positions = np.zeros(self.length, dtype=bool)
        self.update_callback = update_callback or print

    def _get_matrix_widths(self):
        """Find all factors of the length to use as matrix widths."""
        factors = {1}
        for i in range(2, int(math.sqrt(self.length)) + 1):
            if self.length % i == 0:
                factors.add(i)
                factors.add(self.length // i)
        common_widths = {8, 10, 12, 16, 20, 30, 40, 50, 60, 80}
        return sorted(list(factors.union(common_widths)))

    def _find_line_candidates_in_matrix(self, matrix: np.ndarray, char_to_find: str):
        """Performs a brute-force search for lines in a single matrix projection."""
        candidates = []
        height, width = matrix.shape
        char_locations = np.argwhere(matrix == char_to_find)

        if len(char_locations) < 2:
            return []

        for i in range(len(char_locations)):
            for j in range(i + 1, len(char_locations)):
                p1, p2 = char_locations[i], char_locations[j]
                dy, dx = p2[0] - p1[0], p2[1] - p1[1]
                
                line_points = [tuple(p1), tuple(p2)]
                
                # Extend forward
                curr_p = p2.copy()
                while True:
                    curr_p[0] += dy; curr_p[1] += dx
                    if 0 <= curr_p[0] < height and 0 <= curr_p[1] < width and matrix[curr_p[0], curr_p[1]] == char_to_find:
                        line_points.append(tuple(curr_p))
                    else: break

                # Extend backward
                curr_p = p1.copy()
                while True:
                    curr_p[0] -= dy; curr_p[1] -= dx
                    if 0 <= curr_p[0] < height and 0 <= curr_p[1] < width and matrix[curr_p[0], curr_p[1]] == char_to_find:
                        line_points.append(tuple(curr_p))
                    else: break

                if len(line_points) > 2:
                    line_points = sorted(list(set(line_points)))
                    start_point, end_point = line_points[0], line_points[-1]
                    vector_desc = f"({char_to_find},{width},{start_point[0]},{start_point[1]},{end_point[0]},{end_point[1]})"
                    savings = len(line_points) - len(vector_desc)
                    if savings > 0:
                        candidates.append({'savings': savings, 'width': width, 'points': line_points, 'desc': vector_desc})
        return candidates

    def generate_all_candidates(self):
        """Performs the 'All-Angles Scan' to find all vector candidates."""
        self.update_callback("Phase 1: Candidate Generation (All-Angles Scan)")
        all_candidates, unique_chars = [], set(self.original_text)
        widths = self._get_matrix_widths()

        for i, char_to_find in enumerate(unique_chars):
            self.update_callback(f"  Scanning for constellations of '{char_to_find}' ({i+1}/{len(unique_chars)})...")
            for width in widths:
                if width > self.length: continue
                height = math.ceil(self.length / width)
                padded_text = self.original_text.ljust(width * height, '\0')
                matrix = np.array(list(padded_text)).reshape((height, width))
                all_candidates.extend(self._find_line_candidates_in_matrix(matrix, char_to_find))
        
        unique_candidates, seen_descs = [], set()
        for cand in all_candidates:
            if cand['desc'] not in seen_descs:
                unique_candidates.append(cand)
                seen_descs.add(cand['desc'])
        return unique_candidates

    def select_optimal_vectors(self, candidates):
        """Performs the 'Constellation Prize' selection process."""
        self.update_callback("\nPhase 2: Optimal Selection (The Constellation Prize)")
        candidates.sort(key=lambda x: x['savings'], reverse=True)
        vector_key = []
        for cand in candidates:
            indices_to_claim = [y * cand['width'] + x for y, x in cand['points']]
            can_be_claimed = all(idx < self.length and not self.claimed_positions[idx] for idx in indices_to_claim)
            if can_be_claimed:
                vector_key.append(cand['desc'])
                for idx in indices_to_claim: self.claimed_positions[idx] = True
        return vector_key

    def generate_blueprint(self):
        """Generates the final Vector Key and Remnant Stream as a single compiled string."""
        candidates = self.generate_all_candidates()
        vector_key = self.select_optimal_vectors(candidates)
        self.update_callback("\nPhase 3: Blueprint Generation")
        remnant_stream = "".join([char for i, char in enumerate(self.original_text) if not self.claimed_positions[i]])
        vector_key_string = "§".join(vector_key)
        self.update_callback("\nProcess Complete.")
        return f"{self.length}¬{vector_key_string}‡{remnant_stream}"
        
    @staticmethod
    def reconstruct(compiled_string):
        """Re-paints the starfield from the compiled string blueprint."""
        # Decompile the blueprint string
        try:
            length_part, main_part = compiled_string.split('¬', 1)
            original_length = int(length_part)
            key_string, remnant_stream = main_part.split('‡', 1)
        except ValueError:
            raise ValueError("Invalid blueprint format. Expected 'length¬key‡remnant'.")

        vector_key = key_string.split('§') if key_string else []
        
        canvas = ['\0'] * original_length
        for vector_desc in vector_key:
            try:
                parts = vector_desc.strip('()').split(',')
                char, width, y1, x1, y2, x2 = parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])
            except (ValueError, IndexError):
                raise ValueError(f"Malformed vector in key: {vector_desc}")

            dx, dy = abs(x2 - x1), -abs(y2 - y1)
            sx, sy = 1 if x1 < x2 else -1, 1 if y1 < y2 else -1
            err, cx, cy = dx + dy, x1, y1
            while True:
                linear_index = cy * width + cx
                if linear_index < original_length: canvas[linear_index] = char
                if cx == x2 and cy == y2: break
                e2 = 2 * err
                if e2 >= dy: err += dy; cx += sx
                if e2 <= dx: err += dx; cy += sy

        remnant_iter = iter(remnant_stream)
        for i in range(original_length):
            if canvas[i] == '\0':
                try: canvas[i] = next(remnant_iter)
                except StopIteration: pass
                    
        return "".join(canvas).replace('\0', '')

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Vectorial Tessellation Engine")
        self.geometry("800x600")
        self.configure(bg="#f0f0f0")
        
        # --- UI Elements ---
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="Helvetica", size=10)
        mono_font = font.Font(family="Courier New", size=10)

        # Input Frame
        input_frame = tk.Frame(self, padx=10, pady=10, bg="#f0f0f0")
        input_frame.pack(fill=tk.X)
        
        input_label_frame = tk.Frame(input_frame, bg="#f0f0f0")
        input_label_frame.pack(fill=tk.X)
        tk.Label(input_label_frame, text="Original String:", bg="#f0f0f0", font=default_font).pack(side=tk.LEFT)
        tk.Button(input_label_frame, text="Load from File...", command=self.load_file).pack(side=tk.RIGHT)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, height=8, font=mono_font, wrap=tk.WORD)
        self.input_text.pack(fill=tk.X, expand=True)

        # Control Frame
        control_frame = tk.Frame(self, padx=10, pady=5, bg="#f0f0f0")
        control_frame.pack(fill=tk.X)
        self.compress_button = tk.Button(control_frame, text="Generate Blueprint", command=self.run_compression)
        self.compress_button.pack(side=tk.LEFT)
        self.decompress_button = tk.Button(control_frame, text="Reconstruct from Blueprint", command=self.run_reconstruction)
        self.decompress_button.pack(side=tk.LEFT, padx=5)
        
        # Results Frame
        results_frame = tk.Frame(self, padx=10, pady=10, bg="#f0f0f0")
        results_frame.pack(fill=tk.BOTH, expand=True)
        tk.Label(results_frame, text="Compiled Blueprint:", bg="#f0f0f0", font=default_font).pack(anchor=tk.W)
        self.blueprint_text = scrolledtext.ScrolledText(results_frame, height=8, font=mono_font, wrap=tk.WORD)
        self.blueprint_text.pack(fill=tk.X, expand=True)
        
        tk.Label(results_frame, text="Reconstructed String:", bg="#f0f0f0", font=default_font).pack(anchor=tk.W, pady=(10, 0))
        self.reconstructed_text = scrolledtext.ScrolledText(results_frame, height=8, font=mono_font, wrap=tk.WORD, state=tk.DISABLED)
        self.reconstructed_text.pack(fill=tk.X, expand=True)
        
        # Status/Log
        status_frame = tk.Frame(self, padx=10, pady=5, bg="#f0f0f0")
        status_frame.pack(fill=tk.X)
        self.status_label = tk.Label(status_frame, text="Status: Idle", bg="#f0f0f0", anchor=tk.W)
        self.status_label.pack(fill=tk.X)
        
    def log_message(self, message):
        self.status_label.config(text=f"Status: {message.strip()}")
        self.update_idletasks() # Force UI update

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=(("Text Files", "*.txt"), ("All files", "*.*"))
        )
        if not filepath:
            return
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                self.input_text.delete("1.0", tk.END)
                self.input_text.insert("1.0", content)
                self.log_message(f"Loaded file: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("File Error", f"Failed to read file:\n{e}")

    def run_compression(self):
        original_string = self.input_text.get("1.0", tk.END).strip()
        if not original_string:
            messagebox.showerror("Error", "Input string is empty.")
            return

        self.compress_button.config(state=tk.DISABLED)
        self.decompress_button.config(state=tk.DISABLED)
        self.blueprint_text.delete("1.0", tk.END)
        self.reconstructed_text.config(state=tk.NORMAL)
        self.reconstructed_text.delete("1.0", tk.END)
        self.reconstructed_text.config(state=tk.DISABLED)

        # Run tessellation in a separate thread to keep the GUI responsive
        threading.Thread(target=self.compression_thread, args=(original_string,)).start()

    def compression_thread(self, original_string):
        try:
            tessellator = VectorialTessellator(original_string, update_callback=self.log_message)
            compiled_blueprint = tessellator.generate_blueprint()
            
            self.blueprint_text.insert("1.0", compiled_blueprint)
            
            original_size = len(original_string)
            compressed_size = len(compiled_blueprint)
            reduction = (1 - compressed_size / original_size) * 100 if original_size > 0 else 0
            
            self.log_message(f"Analysis Complete. Reduction: {reduction:.2f}%")
        except Exception as e:
            self.log_message(f"Error during compression: {e}")
        finally:
            self.compress_button.config(state=tk.NORMAL)
            self.decompress_button.config(state=tk.NORMAL)


    def run_reconstruction(self):
        compiled_string = self.blueprint_text.get("1.0", tk.END).strip()
        if not compiled_string or '¬' not in compiled_string:
            messagebox.showerror("Error", "Compiled blueprint is empty or invalid.")
            return
            
        try:
            reconstructed_string = VectorialTessellator.reconstruct(compiled_string)
            self.reconstructed_text.config(state=tk.NORMAL)
            self.reconstructed_text.delete("1.0", tk.END)
            self.reconstructed_text.insert("1.0", reconstructed_string)
            self.reconstructed_text.config(state=tk.DISABLED)
            
            # Verification
            original_string = self.input_text.get("1.0", tk.END).strip()
            if original_string == reconstructed_string:
                messagebox.showinfo("Verification", "Success: Reconstructed string matches the original.")
            else:
                messagebox.showwarning("Verification", "Failure: Reconstructed string does not match the original.")
        except Exception as e:
            messagebox.showerror("Reconstruction Error", f"An error occurred: {e}")

def run_cli(input_string):
    """Runs the engine in command-line mode."""
    print(f"Original String ({len(input_string)} chars):")
    print(input_string)
    print("-" * 30)

    tessellator = VectorialTessellator(input_string, update_callback=print)
    compiled_blueprint = tessellator.generate_blueprint()

    print("\n--- COMPILED BLUEPRINT ---")
    print(f"\"{compiled_blueprint}\"")
    print("-" * 30)
    
    original_size = len(input_string)
    compressed_size = len(compiled_blueprint)
    
    print("\nSize Analysis:")
    print(f"  - Original: {original_size} characters")
    print(f"  - Compressed: {compressed_size} characters")
    if original_size > 0:
        ratio = (1 - compressed_size / original_size) * 100
        print(f"  - Reduction: {ratio:.2f}%")
        
    reconstructed_string = VectorialTessellator.reconstruct(compiled_blueprint)
    print("\nReconstructed String:")
    print(reconstructed_string)
    
    print("\nVerification:")
    print(f"  - Lossless: {reconstructed_string == input_string}")

if __name__ == "__main__":
    # Check if a display is available to determine execution mode
    display_available = bool(os.environ.get('DISPLAY', None))
    
    # If arguments are passed, always run in CLI mode
    if len(sys.argv) > 1:
        input_data = " ".join(sys.argv[1:])
        run_cli(input_data)
    elif display_available:
        app = App()
        app.mainloop()
    else:
        print("No display found. Running in command-line mode.")
        # Ask for user input instead of using a default test string.
        try:
            input_string = input("Please enter the string to analyze: ")
            if input_string:
                print("-" * 30)
                run_cli(input_string)
            else:
                print("No input provided. Exiting.")
        except (EOFError, KeyboardInterrupt):
            print("\nOperation cancelled by user. Exiting.")
