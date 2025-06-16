import numpy as np
import math

class VolumetricTessellator:
    """
    An engine for the structural analysis and compression of a string
    based on the principles of Volumetric Tessellation.
    """

    def __init__(self, text: str, update_callback=None):
        self.original_text = text
        self.length = len(text)
        self.claimed_positions = np.zeros(self.length, dtype=bool)
        # A simple callback for logging progress in a non-GUI environment
        self.log = update_callback or print

    def _get_volume_permutations(self):
        """
        Generates plausible 3D matrix dimensions (pages, rows, cols).
        This is a complex factorization problem; we simplify by iterating
        through plausible page counts and factoring the remainder in 2D.
        """
        permutations = set()
        # Iterate through potential number of pages
        for pages in range(1, int(self.length**0.5) + 1):
            if self.length % pages == 0:
                area = self.length // pages
                # Find 2D factors for the remaining area
                for rows in range(1, int(area**0.5) + 1):
                    if area % rows == 0:
                        cols = area // rows
                        permutations.add(tuple(sorted((pages, rows, cols))))
        # To avoid excessive computation, we'll limit the number of permutations.
        # A more sophisticated approach would prune this list intelligently.
        return sorted(list(permutations), key=lambda x: x[0]*x[1]*x[2])[:50] # Limit permutations for performance


    def _find_line_candidates_in_volume(self, volume: np.ndarray, char_to_find: str):
        """
        Performs a brute-force search for 3D lines in a single volume projection.
        This is computationally intensive and the heart of the "All-Skies Survey".
        """
        candidates = []
        pages, rows, cols = volume.shape
        char_locations = np.argwhere(volume == char_to_find)

        if len(char_locations) < 2:
            return []

        # Check lines between every pair of points
        for i in range(len(char_locations)):
            for j in range(i + 1, len(char_locations)):
                p1, p2 = char_locations[i], char_locations[j]
                dp, dr, dc = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
                
                line_points = [tuple(p1), tuple(p2)]
                
                # Extend forward
                curr_p = p2.copy()
                while True:
                    curr_p[0] += dp; curr_p[1] += dr; curr_p[2] += dc
                    if (0 <= curr_p[0] < pages and 0 <= curr_p[1] < rows and 0 <= curr_p[2] < cols
                        and volume[tuple(curr_p)] == char_to_find):
                        line_points.append(tuple(curr_p))
                    else: break
                
                # Extend backward
                curr_p = p1.copy()
                while True:
                    curr_p[0] -= dp; curr_p[1] -= dr; curr_p[2] -= dc
                    if (0 <= curr_p[0] < pages and 0 <= curr_p[1] < rows and 0 <= curr_p[2] < cols
                        and volume[tuple(curr_p)] == char_to_find):
                        line_points.append(tuple(curr_p))
                    else: break

                if len(line_points) > 2:
                    line_points = sorted(list(set(line_points)))
                    start, end = line_points[0], line_points[-1]
                    
                    # Vector description: (char,pages,rows,cols,z1,y1,x1,z2,y2,x2)
                    desc = f"({char_to_find},{pages},{rows},{cols},{start[0]},{start[1]},{start[2]},{end[0]},{end[1]},{end[2]})"
                    savings = len(line_points) - len(desc)
                    
                    if savings > 0:
                        candidates.append({'savings': savings, 'points': line_points, 'desc': desc})
        return candidates

    def generate_all_candidates(self):
        """Performs the 'All-Skies Survey' to find all filament candidates."""
        self.log("Phase 1: Candidate Generation (All-Skies Survey)")
        all_candidates, unique_chars = [], set(self.original_text)
        permutations = self._get_volume_permutations()

        for i, char_to_find in enumerate(unique_chars):
            self.log(f"  Surveying for '{char_to_find}' structures ({i+1}/{len(unique_chars)})...")
            for dims in permutations:
                pages, rows, cols = dims
                # Ensure the dimensions match the length
                if pages * rows * cols != self.length: continue
                
                volume = np.array(list(self.original_text)).reshape(dims)
                all_candidates.extend(self._find_line_candidates_in_volume(volume, char_to_find))
        
        # Remove duplicate candidates
        unique_candidates, seen_descs = [], set()
        for cand in all_candidates:
            if cand['desc'] not in seen_descs:
                unique_candidates.append(cand)
                seen_descs.add(cand['desc'])
        return unique_candidates

    def select_optimal_vectors(self, candidates):
        """Performs the 'Cosmological Principle' selection process."""
        self.log("\nPhase 2: Optimal Selection (The Cosmological Principle)")
        candidates.sort(key=lambda x: x['savings'], reverse=True)
        
        cosmological_key = []
        for cand in candidates:
            dims = tuple(map(int, cand['desc'].strip('()').split(',')[1:4]))
            pages, rows, cols = dims
            
            # Convert matrix coordinates back to linear string indices
            indices_to_claim = [p*rows*cols + r*cols + c for p, r, c in cand['points']]
            
            can_be_claimed = all(not self.claimed_positions[idx] for idx in indices_to_claim)
            
            if can_be_claimed:
                cosmological_key.append(cand['desc'])
                for idx in indices_to_claim: self.claimed_positions[idx] = True
        
        return cosmological_key

    def generate_blueprint(self):
        """Generates the final Cosmological Key and Aperiodic Remnant."""
        candidates = self.generate_all_candidates()
        cosmological_key = self.select_optimal_vectors(candidates)
        
        self.log("\nPhase 3: Blueprint Generation")
        remnant_stream = "".join([char for i, char in enumerate(self.original_text) if not self.claimed_positions[i]])
        
        key_string = "§".join(cosmological_key)
        self.log("\nCosmology Engine analysis complete.")
        return f"{self.length}¬{key_string}‡{remnant_stream}"
        
    @staticmethod
    def reconstruct(compiled_string):
        """Re-runs the Big Bang from the blueprint."""
        try:
            length_part, main_part = compiled_string.split('¬', 1)
            original_length = int(length_part)
            key_string, remnant_stream = main_part.split('‡', 1)
        except ValueError:
            raise ValueError("Invalid blueprint format. Expected 'length¬key‡remnant'.")

        cosmological_key = key_string.split('§') if key_string else []
        canvas = ['\0'] * original_length
        
        for vector_desc in cosmological_key:
            parts = vector_desc.strip('()').split(',')
            char, p, r, c, z1, y1, x1, z2, y2, x2 = [parts[0]] + [int(n) for n in parts[1:]]
            
            # Simple 3D DDA (Digital Differential Analyzer) for line drawing
            dp, dr, dc = z2 - z1, y2 - y1, x2 - x1
            steps = max(abs(dp), abs(dr), abs(dc))
            
            zp, rp, cp = z1, y1, x1
            for _ in range(steps + 1):
                pz, py, px = round(zp), round(rp), round(cp)
                linear_index = pz * r * c + py * c + px
                if linear_index < original_length:
                    canvas[linear_index] = char
                zp += dp / steps if steps != 0 else 0
                rp += dr / steps if steps != 0 else 0
                cp += dc / steps if steps != 0 else 0

        remnant_iter = iter(remnant_stream)
        for i in range(original_length):
            if canvas[i] == '\0':
                try: canvas[i] = next(remnant_iter)
                except StopIteration: pass
                    
        return "".join(canvas).replace('\0', '')

def run_cli(input_string):
    """A command-line interface for the engine."""
    print(f"Original String ({len(input_string)} chars):")
    print(input_string)
    print("-" * 30)

    tessellator = VolumetricTessellator(input_string)
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
        
    print("\nReconstructing from blueprint...")
    reconstructed_string = VolumetricTessellator.reconstruct(compiled_blueprint)
    
    print("\nVerification:")
    print(f"  - Reconstructed String: \"{reconstructed_string}\"")
    print(f"  - Lossless: {reconstructed_string == input_string}")

if __name__ == "__main__":
    # This example requires a string whose length has convenient 3D factors
    # 60 = 3 * 4 * 5
    # 'a' forms a major space diagonal. 'z' is noise.
    test_string = "azzzazzzzzazzzzzzzazzzzzzzzzazzzzzzzzzzzazzzzzzzzzzzzzazzz"
    test_string = test_string.ljust(60, 'z')

    run_cli(test_string)

