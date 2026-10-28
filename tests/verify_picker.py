"""Optional real-browser regression: pip install playwright; Chrome must be installed.

python tests/verify_picker.py [--base-url http://127.0.0.1:8766/compare.html]
Default is the repository's actual file:// page (no HTTP server needed).
Use --screenshots DIR to save desktop and mobile evidence.
No benchmarks, outputs or metrics are modified.
"""
import argparse
import json
from pathlib import Path
from urllib.parse import urlencode
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def verify(url, screenshots=None):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="chrome", headless=True)
        page = browser.new_page(viewport={"width": 1440, "height": 900})
        page.add_init_script("""if(window===window.top){window.arenaErrors=[];
          window.addEventListener('error',e=>window.arenaErrors.push(e.message));}""")
        page.goto(url, wait_until="domcontentloaded")
        page.wait_for_selector("#aPick")
        models = page.evaluate("window.ARENA.models")
        ids = sorted(model["provider"] + "/" + model["model"] for model in models)
        local = [model for model in models if model["provider"] == "local"]
        local_count = len(local)
        assert local_count >= 25
        assert page.locator("#testSel option").count() == 3
        assert f"{len(models)} models" in page.locator("#countPill").inner_text()
        checks = []
        if screenshots:
            screenshots.mkdir(parents=True, exist_ok=True)
            page.screenshot(path=str(screenshots / "arena-compare-desktop.png"))
        # Both pickers expose every manifest submission exactly once, under every filter.
        for side in ("a", "b"):
            page.locator(f"#{side}Pick").click()
            page.locator("#resetFilters").click()
            assert sorted(page.locator(".model-option").evaluate_all("els=>els.map(el=>el.dataset.model)")) == ids
            providers = page.evaluate("[...document.querySelector('#providerFilter').options].map(o=>o.value).filter(Boolean)")
            for provider in providers:
                page.select_option("#providerFilter", provider)
                expected = sorted(model["provider"] + "/" + model["model"] for model in models if model["provider"] == provider)
                actual = sorted(page.locator(".model-option").evaluate_all("els=>els.map(el=>el.dataset.model)"))
                assert actual == expected, (side, provider)
            page.select_option("#providerFilter", "local")
            assert page.locator(".model-option").count() == local_count
            assert page.locator("#pickerSummary").inner_text().startswith(f"{local_count} of {local_count}")
            assert page.locator("#modelResults").evaluate("el=>el.scrollHeight>el.clientHeight")
            if screenshots and side == "b":
                page.screenshot(path=str(screenshots / "arena-picker-desktop.png"))
                page.locator(".model-option").last.scroll_into_view_if_needed()
                page.screenshot(path=str(screenshots / "arena-picker-desktop-last.png"))
            page.locator("#modelSearch").fill("ORCA q4_k_s")
            assert page.locator(".model-option").count() == 1
            assert "Orca" in page.locator(".model-option").inner_text()
            page.locator("#modelSearch").fill("nonexistent-submission-xyz")
            assert page.locator(".model-option").count() == 0
            assert "No models match" in page.locator("#modelResults").inner_text()
            page.locator("#resetFilters").click()
            assert page.locator(".model-option").count() == len(models)
            page.keyboard.press("Escape")
            assert not page.locator("#modelPicker").evaluate("el=>el.open")
            assert page.locator(f"#{side}Pick").evaluate("el=>el===document.activeElement")
            # Exercise selecting all 25 local submissions, including every formerly hidden variant.
            for model in local:
                page.locator(f"#{side}Pick").click()
                page.select_option("#providerFilter", "local")
                identity = model["provider"] + "/" + model["model"]
                page.locator(f'button[data-model="{identity}"]').click()
                assert page.locator(f"#{side}SelectionName").inner_text() == model["model_display"]
                assert page.locator(f"#{side}Frame").get_attribute("src") == model["outputs"]["01-car-parallax"]
                assert page.locator(f"#{side}Open").get_attribute("href") == model["outputs"]["01-car-parallax"]
            checks.append(f"{side.upper()}: all {len(models)} models reachable; all {local_count} local models selected")
        # Keyboard selection, Enter, Escape and exact deep-link state.
        page.locator("#aPick").click()
        page.select_option("#providerFilter", "local")
        page.locator("#modelSearch").fill("ORCA q4_k_s")
        page.locator("#modelSearch").evaluate("el=>el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',isComposing:true,bubbles:true}))")
        assert page.locator("#modelPicker").evaluate("el=>el.open"), "IME Enter must not select"
        page.locator("#modelSearch").evaluate("el=>el.dispatchEvent(new KeyboardEvent('keydown',{key:'Enter',keyCode:229,bubbles:true}))")
        assert page.locator("#modelPicker").evaluate("el=>el.open"), "Legacy IME Enter must not select"
        page.keyboard.press("ArrowDown")
        assert page.locator(".model-option").first.evaluate("el=>el===document.activeElement")
        page.keyboard.press("Enter")
        assert "Orca" in page.locator("#aSelectionName").inner_text()
        before = page.evaluate("Object.fromEntries(new URLSearchParams(location.hash.slice(1)))")
        page.locator("#swapBtn").click()
        after = page.evaluate("Object.fromEntries(new URLSearchParams(location.hash.slice(1)))")
        assert (after["a"], after["b"]) == (before["b"], before["a"])
        page.reload(wait_until="domcontentloaded")
        assert page.evaluate("Object.fromEntries(new URLSearchParams(location.hash.slice(1)))") == after
        page.select_option("#testSel", "02-plants-vs-zombies")
        assert "02-plants-vs-zombies/output.html" in page.locator("#aFrame").get_attribute("src")
        assert "02-plants-vs-zombies/output.html" in page.locator("#bFrame").get_attribute("src")
        page.locator("#reloadBtn").click()
        assert "arenaReload=" in page.locator("#aFrame").get_attribute("src")
        assert "arenaReload=" in page.locator("#bFrame").get_attribute("src")
        assert page.evaluate("Object.fromEntries(new URLSearchParams(location.hash.slice(1)))")["a"] == after["a"]
        checks.append("keyboard/IME input, swap, browser reload, test switching and output reload")
        # Historical bare-slug links and Laguna's previous typo remain usable.
        base = url.split("#")[0].split("?")[0]
        legacy = {"test": "01-car-parallax", "a": "laguna-s-2.1 i3XSS", "b": "gpt-5.5"}
        page.goto(base + "#" + urlencode(legacy), wait_until="domcontentloaded")
        assert "Laguna" in page.locator("#aSelectionName").inner_text()
        assert page.locator("#bSelectionName").inner_text() == "GPT-5.5"
        assert page.evaluate("new URLSearchParams(location.hash.slice(1)).get('a')") == "local/laguna-s-2.1"
        # A previous bare DeepSeek link retains the originally published run;
        # the newer separate run is addressable by its provider-qualified ID.
        repeated = "deepseek-v4.1-flash-1017-uncensored-gsq-rco-iq2-xxs"
        page.goto(base + "#" + urlencode({"test":"01-car-parallax","a":repeated}), wait_until="domcontentloaded")
        assert page.evaluate("new URLSearchParams(location.hash.slice(1)).get('a')") == "llamacpp/" + repeated
        page.goto(base + "#" + urlencode({"test":"01-car-parallax","a":"local/" + repeated}), wait_until="domcontentloaded")
        assert page.evaluate("new URLSearchParams(location.hash.slice(1)).get('a')") == "local/" + repeated
        assert page.locator("#aFrame").get_attribute("src").startswith("providers/local/" + repeated + "/")
        checks.append("existing bare DeepSeek link and both provider-qualified run identities")
        # Short landscape + narrow mobile + desktop at enlarged effective scale.
        for width, height in [(390,844),(320,568),(844,390),(768,600),(320,240)]:
            page.set_viewport_size({"width":width,"height":height})
            assert page.evaluate("document.documentElement.scrollWidth<=innerWidth"), (width,height,"page overflow")
            page.locator("#aPick").click()
            page.select_option("#providerFilter","local")
            assert page.locator(".model-option").count() == local_count
            assert page.locator("#modelPicker").evaluate("el=>{const r=el.getBoundingClientRect();return r.left>=0 && r.right<=innerWidth && r.top>=0 && r.bottom<=innerHeight}")
            assert page.locator("#modelResults").evaluate("el=>el.clientHeight>50 && el.scrollWidth<=el.clientWidth")
            last_name = page.locator(".model-option").last.locator(".option-name").inner_text()
            page.locator(".model-option").last.scroll_into_view_if_needed()
            page.locator(".model-option").last.click()
            assert page.locator("#aSelectionName").inner_text() == last_name
            page.locator("#aPick").click()
            if screenshots and width == 390:
                page.screenshot(path=str(screenshots / "arena-picker-mobile.png"))
                page.locator("#closePicker").click()
                page.screenshot(path=str(screenshots / "arena-compare-mobile.png"),full_page=True)
            else:
                page.locator("#closePicker").click()
            checks.append(f"{width}x{height}: no overflow; all {local_count} entries; last entry selectable")
        assert page.evaluate("window.arenaErrors") == [], page.evaluate("window.arenaErrors")
        checks.append("no comparison-page JavaScript errors")
        browser.close()
        return {"url":url,"models":len(models),"local_models":len(local),"checks":checks}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url",default=(ROOT / "compare.html").as_uri())
    parser.add_argument("--screenshots",type=Path)
    args = parser.parse_args()
    print(json.dumps(verify(args.base_url,args.screenshots),indent=2))
