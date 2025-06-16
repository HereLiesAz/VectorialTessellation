from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import math
import json

# --- Analysis Engines ---
# (Adapted from the previous Python implementations)

class VolumetricTessellator:
    def __init__(self, text: str, update_callback=None):
        self.original_text = text
        self.length = len(text)
        self.claimed_positions = np.zeros(self.length, dtype=bool)
        self.log = update_callback or print

    def _get_volume_permutations(self):
        permutations = set()
        for pages in range(1, int(self.length**0.5) + 1):
            if self.length % pages == 0:
                area = self.length // pages
                for rows in range(1, int(area**0.5) + 1):
                    if area % rows == 0:
                        cols = area // rows
                        permutations.add(tuple(sorted((pages, rows, cols))))
        if not permutations: permutations.add((1, 1, self.length))
        return sorted(list(permutations), key=lambda x: x[0]*x[1]*x[2])[:50]

    def _find_line_candidates_in_volume(self, volume, char_to_find):
        candidates = []
        pages, rows, cols = volume.shape
        char_locations = np.argwhere(volume == char_to_find)
        if len(char_locations) < 2: return []

        checked_pairs = set()
        for i in range(len(char_locations)):
            for j in range(i + 1, len(char_locations)):
                p1, p2 = char_locations[i], char_locations[j]
                pair_key = tuple(sorted((tuple(p1), tuple(p2))))
                if pair_key in checked_pairs: continue
                checked_pairs.add(pair_key)

                dp, dr, dc = p2[0] - p1[0], p2[1] - p1[1], p2[2] - p1[2]
                line_points = [p_other for p_other in char_locations if (p_other[0] - p1[0]) * dr == (p_other[1] - p1[1]) * dp and (p_other[0] - p1[0]) * dc == (p_other[2] - p1[2]) * dp]
                
                if len(line_points) > 2:
                    line_points = sorted([tuple(p) for p in line_points])
                    start, end = line_points[0], line_points[-1]
                    desc = f"({char_to_find},{pages},{rows},{cols},{','.join(map(str, start))},{','.join(map(str, end))})"
                    savings = len(line_points) - len(desc)
                    if savings > 0:
                        candidates.append({'savings': savings, 'points': line_points, 'desc': desc})
        return candidates

    def generate_blueprint(self):
        all_candidates, unique_chars = [], set(self.original_text)
        permutations = self._get_volume_permutations()

        for char_to_find in unique_chars:
            for dims in permutations:
                pages, rows, cols = dims
                if pages * rows * cols != self.length: continue
                volume = np.array(list(self.original_text)).reshape(dims)
                all_candidates.extend(self._find_line_candidates_in_volume(volume, char_to_find))

        unique_candidates = {cand['desc']: cand for cand in all_candidates}.values()
        unique_candidates = sorted(list(unique_candidates), key=lambda x: x['savings'], reverse=True)
        
        cosmological_key = []
        for cand in unique_candidates:
            dims = tuple(map(int, cand['desc'].strip('()').split(',')[1:4]))
            pages, rows, cols = dims
            indices_to_claim = [p*rows*cols + r*cols + c for p, r, c in cand['points']]
            if all(not self.claimed_positions[idx] for idx in indices_to_claim):
                cosmological_key.append(cand['desc'])
                for idx in indices_to_claim: self.claimed_positions[idx] = True
        
        remnant_stream = "".join([char for i, char in enumerate(self.original_text) if not self.claimed_positions[i]])
        key_string = "§".join(cosmological_key)
        compiled_blueprint = f"{self.length}¬{key_string}‡{remnant_stream}"
        
        return {
            'engine': 'volumetric', 'compiledBlueprint': compiled_blueprint,
            'key': cosmological_key, 'remnant': remnant_stream, 'originalText': self.original_text
        }

class HolographicEngine:
    # A simplified placeholder for the holographic engine logic.
    # In a real application, this would contain the full three-stage analysis.
    def generate_blueprint(self, text):
        return {
            'engine': 'holographic',
            'originalText': text,
            'resonances': [],
            'motifs': {},
            'numericals': {},
            'huffmanDict': {},
            'encodedRemnant': text,
            'error': 'Holographic engine analysis not fully implemented in this backend.'
        }


# --- Flask Server ---
app = Flask(__name__)
CORS(app) # Allow cross-origin requests

@app.route('/analyze', methods=['POST'])
def analyze():
    data = request.get_json()
    if not data or 'text' not in data or 'engine' not in data:
        return jsonify({'error': 'Invalid request. Missing text or engine type.'}), 400
    
    text = data['text']
    engine_type = data['engine']

    try:
        if engine_type == 'volumetric':
            engine = VolumetricTessellator(text)
            result = engine.generate_blueprint()
        elif engine_type == 'holographic':
            engine = HolographicEngine()
            result = engine.generate_blueprint(text)
        else:
            return jsonify({'error': 'Unknown engine type.'}), 400
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': f'An error occurred during analysis: {str(e)}'}), 500

if __name__ == '__main__':
    print("Starting Structural Compression Engine server at http://localhost:5000")
    print("Press CTRL+C to stop the server.")
    app.run(host='0.0.0.0', port=5000)
