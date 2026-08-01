import { readFileSync } from "node:fs";
import { parseHTML } from "linkedom";


function installDomGlobals() {
  const { window } = parseHTML("<!doctype html><html><body></body></html>");
  const names = [
    "Document",
    "DocumentFragment",
    "Element",
    "HTMLElement",
    "HTMLUnknownElement",
    "Node",
    "NodeFilter",
    "SVGElement",
    "Text",
    "DOMParser",
    "Event",
    "EventTarget",
    "MutationObserver",
    "XMLSerializer",
  ];

  globalThis.window = window;
  globalThis.document = window.document;
  Object.defineProperty(globalThis, "navigator", {
    value: window.navigator,
    configurable: true,
    writable: true,
  });
  for (const name of names) {
    if (window[name] !== undefined) {
      globalThis[name] = window[name];
    }
  }
  if (typeof globalThis.getComputedStyle !== "function") {
    globalThis.getComputedStyle = () => ({
      getPropertyValue: () => "",
      fontSize: "16px",
    });
  }
}

function diagnosticLine(error) {
  const hashLine = Number(error?.hash?.loc?.first_line);
  if (Number.isInteger(hashLine) && hashLine > 0) {
    return hashLine;
  }
  const message = String(error?.message ?? "");
  const match = message.match(/(?:Parse error on line|line)\s+(\d+)/i);
  return match ? Number(match[1]) : 1;
}

function write(payload, status) {
  process.stdout.write(`${JSON.stringify(payload)}\n`);
  process.exitCode = status;
}

if (
  process.argv.length !== 5 ||
  process.argv[2] !== "--stdin" ||
  process.argv[3] !== "--format" ||
  process.argv[4] !== "json"
) {
  write(
    {
      valid: false,
      diagnostics: [
        {
          line: 1,
          code: "SPEC_MERMAID_USAGE",
          message: "Usage: --stdin --format json",
        },
      ],
    },
    2,
  );
} else {
  installDomGlobals();
  const source = readFileSync(0, "utf8");
  try {
    const module = await import("mermaid");
    const mermaid = module.default;
    mermaid.initialize({
      startOnLoad: false,
      securityLevel: "strict",
      logLevel: "fatal",
    });
    await mermaid.parse(source);
    write({ valid: true, diagnostics: [] }, 0);
  } catch (error) {
    write(
      {
        valid: false,
        diagnostics: [
          {
            line: diagnosticLine(error),
            code: "SPEC_MERMAID_SYNTAX",
            message: "Mermaid syntax is invalid.",
          },
        ],
      },
      1,
    );
  }
}
