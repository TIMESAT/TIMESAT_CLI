from __future__ import annotations
import os
from typing import Tuple

__all__ = ["create_output_folders"]


def create_output_folders(outfolder: str) -> Tuple[str, str]:
    vpp_folder = os.path.join(outfolder, "VPP")
    st_folder  = os.path.join(outfolder, "ST")
    os.makedirs(vpp_folder, exist_ok=True)
    os.makedirs(st_folder,  exist_ok=True)
    return st_folder, vpp_folder
