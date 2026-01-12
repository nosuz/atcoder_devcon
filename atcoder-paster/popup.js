document.getElementById("paste").addEventListener("click", async () => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab?.id) return;

  const url = tab.url || "";
  const isSubmitPage =
    url.startsWith("https://atcoder.jp/contests/") &&
    (url.includes("/tasks/") || url.includes("/submit"));

  if (!isSubmitPage) {
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      world: "MAIN",
      func: () => {
        alert("AtCoder の各問題または提出ページで実行してください。");
      },
    });
    window.close();
    return;
  }

  await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: async () => {
      const pickerOpts = {
        types: [{ description: "Programs", accept: { "text/plain": [".java"] } }],
        excludeAcceptAllOption: true,
        multiple: false,
      };

      const normalizeJava = (src) => {
        src = src.replace(/^\s*package\s+.*;\s*$/m, "");
        if (!/public\s+class\s+Main\b/.test(src)) {
          src = src.replace(
            /public\s+class\s+[A-Za-z_]\w*\s*\{/m,
            "public class Main {"
          );
        }
        return src;
      };

      const fireInputEvents = (el) => {
        try {
          const proto = Object.getPrototypeOf(el);
          const desc = Object.getOwnPropertyDescriptor(proto, "value");
          if (desc?.set) desc.set.call(el, el.value);
        } catch (_) {}
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
      };

      const setToEditor = (code) => {
        // Monaco
        if (window.monaco?.editor?.getModels) {
          const models = window.monaco.editor.getModels();
          if (models?.[0]) {
            models[0].setValue(code);
            return true;
          }
        }
        // Ace
        if (window.ace?.edit) {
          const aceEl =
            document.querySelector(".ace_editor") || document.getElementById("editor");
          if (aceEl) {
            const editor = window.ace.edit(aceEl);
            editor.setValue(code, -1);
            editor.clearSelection();
            return true;
          }
        }
        return false;
      };

      const ta = document.querySelector('textarea[name="sourceCode"]');

      const [handle] = await showOpenFilePicker(pickerOpts);
      const file = await handle.getFile();
      const content = await file.text();
      const code = normalizeJava(content);

      let ok = setToEditor(code);
      if (ta) {
        ta.value = code;
        fireInputEvents(ta);
        ok = true;
      }

      if (!ok) {
        alert("貼り付け先の editor/textarea が見つかりません。");
      }

      // ページの最後にジャンプ
      // window.scrollTo(0, document.documentElement.scrollHeight);

      const isVisible = (el) => {
        const r = el.getBoundingClientRect();
        return (
          r.top >= 0 &&
          r.left >= 0 &&
          r.bottom <= (window.innerHeight || document.documentElement.clientHeight)
        );
      };

      const findSubmitButton = () =>
        document.querySelector('form.form-code-submit button[type="submit"]');

      const step = () => {
        const btn = findSubmitButton();
        if (!btn) return false;

        if (isVisible(btn)) {
          return true; // 完了
        }

        // 少しずつ下へ
        window.scrollBy(0, 200);
        return false;
      };

      const timer = setInterval(() => {
        if (step()) {
          clearInterval(timer);
        }
      }, 30);

    },
  });

  window.close();
});
