# Add project root to path
import sys
import os
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from patent_suite.controller import PatentController
from patent_suite.tools.syntax_check import check_antecedent_basis

def run_toaster_test():
    print("=== End-to-End 'Toaster' Test ===")
    input_text = "A toaster that uses lasers instead of heating coils to toast bread patterns."
    
    controller = PatentController("toaster_test_session")
    
    # Run with bypass_novelty=True to see the full drafting chain as per success metric
    results = controller.run_full_workflow(input_text, bypass_novelty=True)
    
    print("\n[VERIFICATION RESULTS]")
    
    # 1. Search Report Check
    if "examination" in results:
        print("✅ Success: Search and Examination report generated.")
    else:
        print("❌ Failure: Search report missing.")
        
    # 2. Claims Check
    claims = results.get("claims", "")
    if claims:
        print("✅ Success: Set of claims generated.")
        print("-" * 20)
        print(claims[:200] + "...")
        print("-" * 20)
    else:
        print("❌ Failure: Claims missing.")

    # 3. Antecedent Basis Check
    syntax = check_antecedent_basis(claims)
    if syntax["errors_count"] == 0:
        print(f"✅ Success: AntecedentChecker returns 0 errors.")
    else:
        print(f"❌ Failure: {syntax['errors_count']} antecedent errors found.")
        print(syntax["errors"])

if __name__ == "__main__":
    run_toaster_test()
