javascript:(async () => {
  const pickerOpts = {
    types: [{ description: "Programs", accept: { "text/plain": [".java"] } }],
    excludeAcceptAllOption: true,
    multiple: false,
  };

  const normalizeJava = (src) => {
    // package 行削除（先頭空白も許容）
    src = src.replace(/^\s*package\s+.*;\s*$/m, "");
    // public class XXX { を public class Main { に（class名は任意）
    // ただし "public class Main" が既にあるなら触らない
    if (!/public\s+class\s+Main\b/.test(src)) {
      src = src.replace(/public\s+class\s+[A-Za-z_]\w*\s*\{/m, "public class Main {");
    }
    return src;
  };

  const fireInputEvents = (el) => {
    // React/Vue系で value setter が必要になるケースもあるので両方やる
    const proto = Object.getPrototypeOf(el);
    const desc = Object.getOwnPropertyDescriptor(proto, "value");
    if (desc && desc.set) desc.set.call(el, el.value);

    el.dispatchEvent(new Event("input",  { bubbles: true }));
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
        editor.setValue(code, -1); // -1: カーソルを先頭/末尾に変に動かさない
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
    const code = normalizeJava(content);

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

// javascript:(async()=>{try{const[p]=await showOpenFilePicker({types:[{accept:{"text/plain":[".java"]}}],excludeAcceptAllOption:true});let c=await(await p.getFile()).text();c=c.replace(/^\s*package\s+.*;\s*$/m,"");if(!/public\s+class\s+Main\b/.test(c))c=c.replace(/public\s+class\s+[A-Za-z_]\w*\s*\{/m,"public class Main {");let ok=false;if(window.monaco?.editor?.getModels){let m=window.monaco.editor.getModels();if(m[0]){m[0].setValue(c);ok=true}}if(!ok&&window.ace?.edit){let e=document.querySelector(".ace_editor")||document.getElementById("editor");if(e){let ed=ace.edit(e);ed.setValue(c,-1);ed.clearSelection();ok=true}}let ta=document.querySelector('textarea[name="sourceCode"]');if(ta){ta.value=c;ta.dispatchEvent(new Event("input",{bubbles:true}));ta.dispatchEvent(new Event("change",{bubbles:true}));ok=true}if(!ok)return;window.scrollTo(0,document.documentElement.scrollHeight)}catch(e){}})();
