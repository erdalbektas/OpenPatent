import os

class SafeFileManager:
    """
    A restricted file manager that only allows reading/writing to the /drafts directory.
    Replaces dangerous shell tools.
    """
    def __init__(self, drafts_dir):
        self.drafts_dir = os.path.abspath(drafts_dir)
        if not os.path.exists(self.drafts_dir):
            os.makedirs(self.drafts_dir)

    def _is_safe(self, filepath):
        abs_path = os.path.abspath(filepath)
        return abs_path.startswith(self.drafts_dir)

    def write_draft(self, filename, content):
        target_path = os.path.join(self.drafts_dir, filename)
        if not self._is_safe(target_path):
            raise PermissionError(f"Access to {filename} is restricted. Only /drafts allowed.")
            
        with open(target_path, 'w') as f:
            f.write(content)
        print(f"Draft saved: {target_path}")
        return target_path

    def read_draft(self, filename):
        target_path = os.path.join(self.drafts_dir, filename)
        if not self._is_safe(target_path):
            raise PermissionError(f"Access to {filename} is restricted.")
            
        if not os.path.exists(target_path):
            return None
            
        with open(target_path, 'r') as f:
            return f.read()

if __name__ == "__main__":
    # Test
    manager = SafeFileManager("./test_drafts")
    manager.write_draft("claim_1.txt", "1. A device comprising...")
    print(manager.read_draft("claim_1.txt"))
    
    try:
        manager.write_draft("../dangerous.txt", "evil")
    except PermissionError as e:
        print("Caught expected error:", e)
