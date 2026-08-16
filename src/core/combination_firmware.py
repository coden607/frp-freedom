#!/usr/bin/env python3
"""
Samsung combination firmware lookup helpers for legitimate device recovery.
"""

from __future__ import annotations

import logging
import re
from typing import Any, Dict, List, Optional
from urllib.request import Request, urlopen

logger = logging.getLogger(__name__)

MODEL_RE = re.compile(r'\b(SM-[A-Z0-9]+|GT-[A-Z0-9]+|SCH-[A-Z0-9]+|SGH-[A-Z0-9]+)\b', re.I)

# Common marketing-name hints used when USB only reports generic download mode
NAME_HINTS = {
    's10e': ['SM-G970U', 'SM-G970F', 'SM-G970W', 'SM-G970U1'],
    'galaxy s10e': ['SM-G970U', 'SM-G970F', 'SM-G970W', 'SM-G970U1'],
    's10': ['SM-G973U', 'SM-G973F', 'SM-G973W', 'SM-G973U1'],
    'galaxy s10': ['SM-G973U', 'SM-G973F', 'SM-G973W', 'SM-G973U1'],
    's10+': ['SM-G975U', 'SM-G975F', 'SM-G975W', 'SM-G975U1'],
    's20': ['SM-G981U', 'SM-G981B', 'SM-G981U1', 'SM-G981W'],
    's20+': ['SM-G986U', 'SM-G986B', 'SM-G986U1'],
    's20 ultra': ['SM-G988U', 'SM-G988B', 'SM-G988U1'],
    's21': ['SM-G991U', 'SM-G991B', 'SM-G991U1'],
    's21+': ['SM-G996U', 'SM-G996B', 'SM-G996U1'],
    's21 ultra': ['SM-G998U', 'SM-G998B', 'SM-G998U1'],
    's22': ['SM-S901U', 'SM-S901B', 'SM-S901U1'],
    's22+': ['SM-S906U', 'SM-S906B', 'SM-S906U1'],
    's22 ultra': ['SM-S908U', 'SM-S908B', 'SM-S908U1'],
    's23': ['SM-S911U', 'SM-S911B', 'SM-S911U1'],
    's23+': ['SM-S916U', 'SM-S916B', 'SM-S916U1'],
    's23 ultra': ['SM-S918U', 'SM-S918B', 'SM-S918U1'],
    's24': ['SM-S921U', 'SM-S921B', 'SM-S921U1'],
    's24+': ['SM-S926U', 'SM-S926B', 'SM-S926U1'],
    's24 ultra': ['SM-S928U', 'SM-S928B', 'SM-S928U1'],
    'a15': ['SM-A156U', 'SM-A155F', 'SM-A156E', 'SM-A156B'],
    'a14': ['SM-A145U', 'SM-A145F', 'SM-A145E', 'SM-A145B'],
    'a13': ['SM-A135U', 'SM-A135F', 'SM-A135E', 'SM-A135B'],
    'a12': ['SM-A125U', 'SM-A125F', 'SM-A125E', 'SM-A125B'],
    'a54': ['SM-A546U', 'SM-A546E', 'SM-A546B'],
    'a53': ['SM-A536U', 'SM-A536E', 'SM-A536B'],
    'a52': ['SM-A526U', 'SM-A526E', 'SM-A526B'],
    'a51': ['SM-A515U', 'SM-A515F', 'SM-A515E'],
    'a50': ['SM-A505U', 'SM-A505F', 'SM-A505E'],
    'a33': ['SM-A336U', 'SM-A336E', 'SM-A336B'],
    'a32': ['SM-A325U', 'SM-A325E', 'SM-A325B'],
    'a24': ['SM-A245U', 'SM-A245E', 'SM-A245B'],
    'note 20': ['SM-N980U', 'SM-N980F', 'SM-N981U', 'SM-N986U'],
    'note 20 ultra': ['SM-N986U', 'SM-N986B', 'SM-N986U1'],
    'note 10': ['SM-N960U', 'SM-N960F', 'SM-N960U1'],
    'note 10+': ['SM-N975U', 'SM-N975F', 'SM-N975U1'],
    'note 9': ['SM-N960U', 'SM-N960F', 'SM-N960U1'],
    'note 8': ['SM-N950U', 'SM-N950F', 'SM-N950U1'],
    'z fold 3': ['SM-F926U', 'SM-F926B', 'SM-F926U1'],
    'z fold 4': ['SM-F936U', 'SM-F936B', 'SM-F936U1'],
    'z fold 5': ['SM-F946U', 'SM-F946B', 'SM-F946U1'],
    'z flip 3': ['SM-F711U', 'SM-F711B', 'SM-F711U1'],
    'z flip 4': ['SM-F721U', 'SM-F721B', 'SM-F721U1'],
    'z flip 5': ['SM-F731U', 'SM-F731B', 'SM-F731U1'],
}


def extract_model_code(*text_parts: Optional[str]) -> Optional[str]:
    """Pull a Samsung model code from free-form device text."""
    for part in text_parts:
        if not part:
            continue
        match = MODEL_RE.search(str(part))
        if match:
            return match.group(1).upper()
    return None


def guess_models_from_text(*text_parts: Optional[str]) -> List[str]:
    """Guess likely model codes from marketing names in device text."""
    blob = ' '.join(str(p).lower() for p in text_parts if p)
    found: List[str] = []
    for hint, models in NAME_HINTS.items():
        if hint in blob:
            for model in models:
                if model not in found:
                    found.append(model)
    return found


def combination_urls(model: str) -> Dict[str, str]:
    model = model.upper()
    return {
        'samfw_combination': f'https://samfw.com/combination/{model}',
        'samfw_firmware': f'https://samfw.com/firmware/{model}',
        'search': f'https://samfw.com/firmware/{model}',
    }


def lookup_combination_firmware(
    model: Optional[str] = None,
    *,
    device_text: Optional[str] = None,
    timeout: float = 8.0,
) -> Dict[str, Any]:
    """
    Resolve combination firmware links for a Samsung model.

    Returns structured guidance even when the exact model is unknown.
    """
    resolved = (model or '').upper().strip() or None
    candidates: List[str] = []

    if not resolved and device_text:
        resolved = extract_model_code(device_text)
        candidates = guess_models_from_text(device_text)

    if not resolved and candidates:
        resolved = candidates[0]

    # Filter out generic USB labels that aren't real model codes
    if resolved in {'GT-I9100', 'GT-I9100G'}:
        resolved = None

    result: Dict[str, Any] = {
        'needed': True,
        'model': resolved,
        'candidates': candidates,
        'urls': combination_urls(resolved) if resolved else {},
        'builds': [],
        'message': '',
        'status': 'unknown',
    }

    if not resolved:
        result['status'] = 'model_required'
        result['message'] = (
            'Samsung is in Download mode, but the exact model code is unknown '
            '(USB often shows a generic GT-I9100 label). Read the model from the '
            'Download mode screen and re-run analysis. No firmware or bypass method '
            'should be selected until the exact model is known.'
        )
        result['urls'] = {
            'howto': 'Enter Download mode and note the exact model line, such as SM-G970U.',
        }
        return result

    urls = combination_urls(resolved)
    result['urls'] = urls
    builds = _fetch_samfw_combination_builds(resolved, timeout=timeout)
    result['builds'] = builds

    if builds:
        result['status'] = 'found'
        result['message'] = (
            f'Found {len(builds)} combination build(s) for {resolved}. '
            f'Download from {urls["samfw_combination"]} and flash with Odin/Heimdall.'
        )
    else:
        result['status'] = 'links_ready'
        result['message'] = (
            f'Open {urls["samfw_combination"]} to download combination firmware for {resolved}. '
            'Match the binary (U1/U2/…) to your current bootloader bit.'
        )

    return result


def _fetch_samfw_combination_builds(model: str, timeout: float = 8.0) -> List[Dict[str, str]]:
    """Best-effort scrape of SamFw combination listing.
    
    Note: SamFw may block automated requests (403). This function gracefully
    handles that and returns an empty list, allowing the main lookup to still
    provide URLs for manual download.
    """
    url = f'https://samfw.com/combination/{model.upper()}'
    builds: List[Dict[str, str]] = []
    try:
        req = Request(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})
        with urlopen(req, timeout=timeout) as resp:
            html = resp.read().decode('utf-8', errors='ignore')
        
        logger.debug(f'Fetched {len(html)} characters from SamFw for {model}')
        
        # Try multiple patterns to find build information
        patterns = [
            # Pattern 1: href="/combination/MODEL/BUILD"
            rf'href="(/combination/{re.escape(model.upper())}/([A-Z0-9]+))"',
            # Pattern 2: Look for build-like patterns in the HTML
            r'\b([A-Z][0-9][A-Z0-9]{6,10})\b',
        ]
        
        seen_builds = set()
        for pattern in patterns:
            for match in re.finditer(pattern, html, re.I):
                if len(match.groups()) >= 1:
                    build = match.group(1) if len(match.groups()) == 1 else match.group(2)
                    build = build.upper()
                    # Filter: must start with letter, be 8-12 chars, alphanumeric
                    if (len(build) >= 8 and len(build) <= 12 and 
                        build.isalnum() and build[0].isalpha() and
                        build not in seen_builds and
                        not build.lower().startswith(('http', 'www', 'com', 'div', 'span'))):
                        seen_builds.add(build)
                        path = f'/combination/{model.upper()}/{build}'
                        entry = {
                            'build': build,
                            'url': f'https://samfw.com{path}',
                        }
                        builds.append(entry)
                if len(builds) >= 10:
                    break
            if len(builds) >= 10:
                break
                
    except Exception as exc:
        # SamFw may return 403 Forbidden - this is expected and handled gracefully
        logger.debug(f'Could not fetch SamFw combination list for {model}: {exc}')
    return builds
