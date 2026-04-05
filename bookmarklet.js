javascript:(async () => {
  const pickerOpts = {
    types: [
      {
        description: "Programs",
        accept: { "text/plain": [".java", ".py"] },
      },
    ],
    excludeAcceptAllOption: true,
    multiple: false,
  };

  const normalizeJava = (src) => {
    // package 行削除（先頭空白も許容）
    src = src.replace(/^\s*package\s+.*;\s*$/m, "");
    // public class XXX { を public class Main { に（class名は任意）
    // ただし "public class Main" が既にあるなら触らない
    if (!/public\s+class\s+Main\b/.test(src)) {
      src = src.replace(
        /public\s+class\s+[A-Za-z_]\w*\s*\{/m,
        "public class Main {"
      );
    }
    return src;
  };

  const normalizePython = (src) => {
    const lines = src.split(/\r?\n/);
    const out = [];

    for (const line of lines) {
      const indent = line.match(/^\s*/)?.[0] ?? "";
      const trimmed = line.trim();

      // debug(...) 単体 → コメントアウト
      if (/^debug\s*\(.*\)\s*$/.test(trimmed)) {
        out.push(`${indent}# ${trimmed}`);
        continue;
      }

      // debug(...) + コメント → コメントアウト
      if (/^debug\s*\(.*\)\s*#.*$/.test(trimmed)) {
        out.push(`${indent}# ${trimmed}`);
        continue;
      }

      // if ...: debug(...) → pass + コメント
      const inlineIf = line.match(/^(\s*if\b.*:\s*)debug\s*\((.*)\)\s*(#.*)?$/);
      if (inlineIf) {
        const condition = inlineIf[1];
        const args = inlineIf[2];
        const comment = inlineIf[3] ? ` ${inlineIf[3]}` : "";
        out.push(`${condition}pass # debug(${args})${comment}`);
        continue;
      }

      out.push(line);
    }

    return out.join("\n");
  };

  const normalizeCode = (src, filename) => {
    const lower = (filename || "").toLowerCase();
    if (lower.endsWith(".java")) return normalizeJava(src);
    if (lower.endsWith(".py")) return normalizePython(src);
    return src;
  };

  const fireInputEvents = (el) => {
    try {
    const proto = Object.getPrototypeOf(el);
    const desc = Object.getOwnPropertyDescriptor(proto, "value");
    if (desc && desc.set) desc.set.call(el, el.value);
    } catch (_) {}
    el.dispatchEvent(new Event("input", { bubbles: true }));
    el.dispatchEvent(new Event("change", { bubbles: true }));
  };

  const setToEditor = (code) => {
    // 1) Monaco（ユーザスクリプト等で差し替えられてる場合）
    if (window.monaco?.editor?.getModels) {
      const models = window.monaco.editor.getModels();
      if (models && models[0]) {
        models[0].setValue(code);
        return true;
      }
    }

    // 2) Ace（AtCoder標準で使われることが多い）
    if (window.ace?.edit) {
      // ace editor要素を探す（id="editor" とは限らないため class も見る）
      const aceEl =
        document.querySelector(".ace_editor") ||
        document.getElementById("editor");

      if (aceEl) {
        const editor = window.ace.edit(aceEl);
        editor.setValue(code, -1);
        editor.clearSelection();
        return true;
      }
    }

    return false;
  };

  try {
    // 提出ページか軽く確認（厳密でなくてOK）
    // textarea が無いページでは反映できない（tasksページなど）
    const ta = document.querySelector('textarea[name="sourceCode"]');

    const [handle] = await showOpenFilePicker(pickerOpts);
    const file = await handle.getFile();
    const content = await file.text();
    const code = normalizeCode(content, file.name);

    let ok = false;

    // まず editor 本体へ（見た目に反映される）
    ok = setToEditor(code);

    // 念のため textarea にも同期（送信時に参照される場合がある）
    if (ta) {
      ta.value = code;
      fireInputEvents(ta);
      ok = true;
    }

    if (!ok) {
      alert("貼り付け先の editor/textarea が見つかりません。");
      return;
    }

    // ページの最後にジャンプ
    window.scrollTo(0, document.documentElement.scrollHeight);

    console.log("pasted");
  } catch (e) {
    console.log(e);
  }
})();

// javascript:(async()=>{const pickerOpts={types:[{description:"Programs",accept:{"text/plain":[".java",".py"]}}],excludeAcceptAllOption:true,multiple:false};const normalizeJava=(src)=>{src=src.replace(/^\s*package\s+.*;\s*$/m,"");if(!/public\s+class\s+Main\b/.test(src)){src=src.replace(/public\s+class\s+[A-Za-z_]\w*\s*\{/m,"public class Main {")}return src};const normalizePython=(src)=>{const lines=src.split(/\r?\n/);const out=[];for(const line of lines){const indent=line.match(/^\s*/)?.[0]??"";const trimmed=line.trim();if(/^debug\s*\(.*\)\s*$/.test(trimmed)){out.push(`${indent}# ${trimmed}`);continue}if(/^debug\s*\(.*\)\s*#.*$/.test(trimmed)){out.push(`${indent}# ${trimmed}`);continue}const m=line.match(/^(\s*if\b.*:\s*)debug\s*\((.*)\)\s*(#.*)?$/);if(m){const cond=m[1];const args=m[2];const c=m[3]?` ${m[3]}`:"";out.push(`${cond}pass # debug(${args})${c}`);continue}out.push(line)}return out.join("\n")};const normalizeCode=(src,f)=>{const l=(f||"").toLowerCase();if(l.endsWith(".java"))return normalizeJava(src);if(l.endsWith(".py"))return normalizePython(src);return src};const fireInputEvents=(el)=>{try{const proto=Object.getPrototypeOf(el);const desc=Object.getOwnPropertyDescriptor(proto,"value");if(desc&&desc.set)desc.set.call(el,el.value)}catch(_){}el.dispatchEvent(new Event("input",{bubbles:true}));el.dispatchEvent(new Event("change",{bubbles:true}))};const setToEditor=(code)=>{if(window.monaco?.editor?.getModels){const m=window.monaco.editor.getModels();if(m&&m[0]){m[0].setValue(code);return true}}if(window.ace?.edit){const e=document.querySelector(".ace_editor")||document.getElementById("editor");if(e){const ed=window.ace.edit(e);ed.setValue(code,-1);ed.clearSelection();return true}}return false};try{const ta=document.querySelector('textarea[name="sourceCode"]');const[h]=await showOpenFilePicker(pickerOpts);const f=await h.getFile();const content=await f.text();const code=normalizeCode(content,f.name);let ok=setToEditor(code);if(ta){ta.value=code;fireInputEvents(ta);ok=true}if(!ok){alert("貼り付け先の editor/textarea が見つかりません。");return}window.scrollTo(0,document.documentElement.scrollHeight)}catch(e){console.log(e)}})();
