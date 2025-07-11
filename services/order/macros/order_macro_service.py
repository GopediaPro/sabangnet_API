from utils.macros.ERP.etc_site_macro import ECTSiteMacro
from utils.macros.ERP.zigzag_erp_macro import ZigzagMacro
from utils.macros.ERP.ali_erp_macro import AliMacro
from utils.macros.ERP.brandi_erp_macro import BrandiMacro
from utils.macros.happojang.etc_site_merge_packaging import etc_site_merge_packaging
from utils.macros.happojang.zigzag_merge_packaging import zigzag_merge_packaging
from utils.macros.happojang.ali_merge_packaging import ali_merge_packaging
from utils.macros.happojang.brandy_merge_packaging import brandy_merge_packaging
from utils.macros.happojang.gok_merge_packaging import gok_merge_packaging
from repository.template_config_repository import TemplateConfigRepository
from utils.macros.ERP.Gmarket_auction_erp_macro import GmarketAuctionMacro
from sqlalchemy.ext.asyncio import AsyncSession
from utils.sabangnet_logger import get_logger

logger = get_logger(__name__)

def run_ect_site_macro(file):
    macro = ECTSiteMacro(file)
    return macro.step_1_to_14()

def run_zigzag_macro(file):
    macro = ZigzagMacro(file)
    return macro.step_1_to_9()

def run_ali_macro(file):
    macro = AliMacro(file)
    return macro.step_1_to_10()

def run_brandi_macro(file):
    macro = BrandiMacro(file)
    return macro.step_1_to_11()

def run_gmarket_auction_macro(file_path):
    macro = GmarketAuctionMacro(file_path)
    result = macro.step_1_to_11()
    return result

# macro_name과 실제 실행 함수를 매핑
MACRO_MAP = {
    "ECTSiteMacro": run_ect_site_macro,
    "ZigzagMacro": run_zigzag_macro,
    "AliMacro": run_ali_macro,
    "BrandiMacro": run_brandi_macro,
    "etc_site_merge_packaging": etc_site_merge_packaging,
    "zigzag_merge_packaging": zigzag_merge_packaging,
    "ali_merge_packaging": ali_merge_packaging,
    "brandy_merge_packaging": brandy_merge_packaging,
    "gok_merge_packaging": gok_merge_packaging,
    "GmarketAuctionMacro": run_gmarket_auction_macro,
}

async def run_macro(session: AsyncSession, template_code: str, file_path: str):
    template_config_repository = TemplateConfigRepository(session)
    logger.info(f"run_macro called with template_code={template_code}, file_path={file_path}")
    macro_name = await template_config_repository.get_template_config_by_template_code(template_code)
    logger.info(f"macro_name from DB: {macro_name}")
    if macro_name:
        macro_func = MACRO_MAP.get(macro_name)
        if macro_func is None:
            logger.error(f"Macro '{macro_name}' not found in MACRO_MAP.")
            raise ValueError(f"Macro '{macro_name}' not found in MACRO_MAP.")
        try:
            result = macro_func(file_path)
            logger.info(f"Macro '{macro_name}' executed successfully. file_path={result}")
            return result
        except Exception as e:
            logger.error(f"Error running macro '{macro_name}': {e}")
            raise
    else:
        logger.error(f"Macro not found for template code: {template_code}")
        raise ValueError(f"Macro not found for template code: {template_code}")
