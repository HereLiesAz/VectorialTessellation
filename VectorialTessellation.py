import numpy as np
from collections import defaultdict
import math

class VectorialTessellator:
    """
    An engine for the structural analysis and compression of a string
    based on the principles of Vectorial Tessellation.
    """

    def __init__(self, text: str):
        self.original_text = text
        self.length = len(text)
        self.claimed_positions = np.zeros(self.length, dtype=bool)

    def _get_matrix_widths(self):
        """Find all factors of the length to use as matrix widths."""
        # For practicality, we won't use ALL possible widths, but factors
        # provide a good starting point for structured data. We'll also
        # add some common widths to catch near-periodic data.
        factors = {1}
        for i in range(2, int(math.sqrt(self.length)) + 1):
            if self.length % i == 0:
                factors.add(i)
                factors.add(self.length // i)
        # Add some common widths for non-perfectly factored data
        common_widths = {8, 10, 12, 16, 20, 30, 40, 50, 60, 80}
        return sorted(list(factors.union(common_widths)))

    def _find_line_candidates_in_matrix(self, matrix: np.ndarray, char_to_find: str):
        """
        Performs a brute-force search for lines in a single matrix projection.
        This is the core of the line-finding mechanism.
        """
        candidates = []
        height, width = matrix.shape
        char_locations = np.argwhere(matrix == char_to_find)

        if len(char_locations) < 2:
            return []

        # Check lines between every pair of points
        for i in range(len(char_locations)):
            for j in range(i + 1, len(char_locations)):
                p1 = char_locations[i]
                p2 = char_locations[j]
                
                dy, dx = p2[0] - p1[0], p2[1] - p1[1]
                
                # Find all points on this line
                line_points = [tuple(p1), tuple(p2)]
                
                # Extend forward from p2
                curr_p = p2.copy()
                while True:
                    curr_p[0] += dy
                    curr_p[1] += dx
                    if 0 <= curr_p[0] < height and 0 <= curr_p[1] < width:
                        if matrix[curr_p[0], curr_p[1]] == char_to_find:
                            line_points.append(tuple(curr_p))
                        else:
                            break # Line broken
                    else:
                        break # Out of bounds

                # Extend backward from p1
                curr_p = p1.copy()
                while True:
                    curr_p[0] -= dy
                    curr_p[1] -= dx
                    if 0 <= curr_p[0] < height and 0 <= curr_p[1] < width:
                        if matrix[curr_p[0], curr_p[1]] == char_to_find:
                            line_points.append(tuple(curr_p))
                        else:
                            break # Line broken
                    else:
                        break # Out of bounds

                if len(line_points) > 2:
                    # Sort points to get start/end for a canonical representation
                    line_points = sorted(list(set(line_points)))
                    start_point, end_point = line_points[0], line_points[-1]
                    
                    # Vector description: (char, matrix_width, y1, x1, y2, x2)
                    vector_desc = f"({char_to_find},{width},{start_point[0]},{start_point[1]},{end_point[0]},{end_point[1]})"
                    savings = len(line_points) - len(vector_desc)
                    
                    if savings > 0:
                        candidates.append({
                            'savings': savings,
                            'char': char_to_find,
                            'width': width,
                            'points': line_points,
                            'desc': vector_desc
                        })

        return candidates

    def generate_all_candidates(self):
        """
        Performs the 'All-Angles Scan' to find all vector candidates.
        """
        print("Phase 1: Candidate Generation (All-Angles Scan)")
        all_candidates = []
        unique_chars = set(self.original_text)
        widths = self._get_matrix_widths()

        for i, char_to_find in enumerate(unique_chars):
            print(f"  Scanning for constellations of '{char_to_find}' ({i+1}/{len(unique_chars)})...")
            for width in widths:
                if width > self.length: continue
                height = math.ceil(self.length / width)
                padded_length = width * height
                
                # Pad the string to fit the matrix
                padded_text = self.original_text.ljust(padded_length, '\0')
                matrix = np.array(list(padded_text)).reshape((height, width))
                
                # Find lines for the current character in this matrix projection
                char_candidates = self._find_line_candidates_in_matrix(matrix, char_to_find)
                all_candidates.extend(char_candidates)
        
        # Remove duplicate candidates
        unique_candidates = []
        seen_descs = set()
        for cand in all_candidates:
            if cand['desc'] not in seen_descs:
                unique_candidates.append(cand)
                seen_descs.add(cand['desc'])

        return unique_candidates

    def select_optimal_vectors(self, candidates):
        """
        Performs the 'Constellation Prize' selection process.
        """
        print("\nPhase 2: Optimal Selection (The Constellation Prize)")
        # Sort by savings, descending
        candidates.sort(key=lambda x: x['savings'], reverse=True)
        
        vector_key = []
        
        for cand in candidates:
            # Convert matrix coordinates back to linear string indices
            indices_to_claim = [y * cand['width'] + x for y, x in cand['points']]
            
            # Check if any required positions are already claimed
            can_be_claimed = all(
                idx < self.length and not self.claimed_positions[idx] 
                for idx in indices_to_claim
            )
            
            if can_be_claimed:
                vector_key.append(cand['desc'])
                # Mark positions as claimed
                for idx in indices_to_claim:
                    self.claimed_positions[idx] = True
        
        return vector_key

    def generate_blueprint(self):
        """
        Generates the final Vector Key and Remnant Stream.
        """
        candidates = self.generate_all_candidates()
        vector_key = self.select_optimal_vectors(candidates)
        
        print("\nPhase 3: Blueprint Generation")
        remnant_stream = ""
        for i, char in enumerate(self.original_text):
            if not self.claimed_positions[i]:
                remnant_stream += char
                
        return {
            "vector_key": vector_key,
            "remnant_stream": remnant_stream
        }
        
    @staticmethod
    def reconstruct(blueprint, original_length):
        """
        Re-paints the starfield from the blueprint.
        """
        print("\nReconstructing from blueprint...")
        # Prepare the canvas
        canvas = ['\0'] * original_length
        
        # Draw the constellations from the Vector Key
        for vector_desc in blueprint['vector_key']:
            # Parse the vector description
            parts = vector_desc.strip('()').split(',')
            char, width, y1, x1, y2, x2 = parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4]), int(parts[5])

            # Use Bresenham's line algorithm to find all integer points on the line
            dx, dy = abs(x2 - x1), -abs(y2 - y1)
            sx, sy = 1 if x1 < x2 else -1, 1 if y1 < y2 else -1
            err = dx + dy
            
            cx, cy = x1, y1
            while True:
                linear_index = cy * width + cx
                if linear_index < original_length:
                    canvas[linear_index] = char
                if cx == x2 and cy == y2:
                    break
                e2 = 2 * err
                if e2 >= dy:
                    err += dy
                    cx += sx
                if e2 <= dx:
                    err += dx
                    cy += sy

        # Fill in the stardust from the Remnant Stream
        remnant_iter = iter(blueprint['remnant_stream'])
        for i in range(original_length):
            if canvas[i] == '\0':
                try:
                    canvas[i] = next(remnant_iter)
                except StopIteration:
                    # This can happen if padding was involved; these are null chars
                    pass
                    
        return "".join(canvas).replace('\0', '')


if __name__ == "__main__":
    # Example string with clear geometric patterns
    # 'a' forms a diagonal, 'b' forms a vertical line, 'c' is noise
    test_string = "axcxbxcxaxcxbxcxaxcxbxcxaxcxbxcx"

    print(f"Original String ({len(test_string)} chars):")
    print(test_string)
    print("-" * 30)

    # Initialize and run the tessellation process
    tessellator = VectorialTessellator(test_string)
    blueprint = tessellator.generate_blueprint()

    print("\n--- BLUEPRINT ---")
    print("Vector Key (The Constellations):")
    for vector in blueprint['vector_key']:
        print(f"  - {vector}")

    print("\nRemnant Stream (The Stardust):")
    print(f"  \"{blueprint['remnant_stream']}\"")
    print("-" * 30)
    
    # Calculate sizes for comparison
    original_size = len(test_string)
    vector_key_size = sum(len(v) for v in blueprint['vector_key'])
    remnant_size = len(blueprint['remnant_stream'])
    compressed_size = vector_key_size + remnant_size
    
    print("\nSize Analysis:")
    print(f"  - Original: {original_size} characters")
    print(f"  - Compressed: {compressed_size} characters (Key: {vector_key_size}, Remnant: {remnant_size})")
    if original_size > 0:
        ratio = (1 - compressed_size / original_size) * 100
        print(f"  - Reduction: {ratio:.2f}%")
        
    # Reconstruct and verify
    reconstructed_string = VectorialTessellator.reconstruct(blueprint, original_size)
    print("\nReconstructed String:")
    print(reconstructed_string)
    
    print("\nVerification:")
    print(f"  - Lossless: {reconstructed_string == test_string}")

