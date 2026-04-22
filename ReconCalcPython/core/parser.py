import os

class ControlFile:
    def __init__(self, filepath):
        self.filepath = filepath
        self.format = None
        self.features = []
        self.testcases = []
        self.mapping = []  # List of lists, mapping[i] is test cases for features[i]
        self._parse()

    def _parse(self):
        with open(self.filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]
        
        if not lines:
            return

        self.format = lines[0]
        if self.format not in ['rci', 'ppf']:
            # Default to rci if unknown, or handle error
            pass

        if len(lines) > 1:
            self.features = [f for f in lines[1].split(';') if f]
        
        if len(lines) > 2:
            self.testcases = [t for t in lines[2].split(';') if t]

        if len(lines) > 3:
            for i in range(len(self.features)):
                if i + 3 < len(lines):
                    mapping_line = lines[i + 3]
                    self.mapping.append([t for t in mapping_line.split(';') if t])
                else:
                    self.mapping.append([])

def load_profile(filepath):
    """
    Loads a profile file. 
    If it's a simple list (one procedure per line), it just reads it.
    If it needs conversion (like ppf), it should handle it.
    For now, we'll assume it's already in the 'pro' format or we'll detect ppf.
    """
    procedures = set()
    with open(filepath, 'r') as f:
        content = f.read()
        
    # Detection logic for 'ppf' or similar bloated format if needed
    # For now, let's just read line by line and strip
    for line in content.splitlines():
        line = line.strip()
        if line:
            procedures.add(line)
    return procedures

def convert_ppf_to_pro(filepath):
    """
    Python implementation of convpro logic.
    """
    output = []
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # convpro starts from line 3 (index 2)
    for i in range(2, len(lines)):
        line = lines[i]
        if line.startswith('.'):
            break
        
        # extract content between quotes
        start_quote = line.find('"')
        end_quote = line.find('"', start_quote + 1)
        if start_quote != -1 and end_quote != -1:
            element = line[start_quote + 1 : end_quote]
            
            space_idx = element.find(' ')
            if space_idx == -1:
                output.append(element)
            else:
                # swap: part after space + "," + part before space
                # wait, convpro does: (substr($element, $where+1)).",".(substr($element, 0, $where))
                new_elem = element[space_idx + 1:] + "," + element[:space_idx]
                output.append(new_elem)
    return set(output)
