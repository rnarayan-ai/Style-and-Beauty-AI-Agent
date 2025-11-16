from typing import Dict, List


async def compute_product_recommendations(stylist_out: Dict, refs: List[Dict]) -> Dict:
    products = {
        "foundation": {"recommended": "BudgetBrand Foundation 30ml", "qty_range": "2-4 ml"},
        "developer": {"recommended": "Local 10 vol developer", "qty_range": "5-10 ml", "note": "Use patch test"},
    }
    return products