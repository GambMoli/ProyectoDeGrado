import katex from "katex";
import type { ReactNode } from "react";

interface MathContentProps {
  content: string;
}

interface MathFormulaProps {
  expression: string;
  displayMode?: boolean;
  source?: "latex" | "plain";
  className?: string;
  style?: React.CSSProperties;
}

const blockMathPattern = /\\\[([\s\S]*?)\\\]/g;
const inlineMathPattern = /\\\(([\s\S]*?)\\\)/g;

export function MathContent({ content }: MathContentProps) {
  const segments = splitBlockMath(content);

  return (
    <div className="math-content">
      {segments.map((segment, index) =>
        segment.kind === "block" ? (
          <MathFormula
            key={`block-${index}`}
            expression={segment.content}
            displayMode
            source="latex"
            className="math-content__block"
          />
        ) : (
          <div key={`text-${index}`}>{renderTextSegment(segment.content, index)}</div>
        ),
      )}
    </div>
  );
}

export function MathFormula({
  expression,
  displayMode = false,
  source = "latex",
  className,
  style,
}: MathFormulaProps) {
  const latexExpression = source === "plain" ? plainMathToLatex(expression) : expression.trim();
  const html = katex.renderToString(latexExpression || "\\,", {
    displayMode,
    throwOnError: false,
    strict: "ignore",
  });
  const Tag = displayMode ? "div" : "span";

  return <Tag className={className} style={style} dangerouslySetInnerHTML={{ __html: html }} />;
}

export function extractMathCandidateForPreview(content: string): string | null {
  const lines = content
    .split(/\n+/)
    .map((line) => line.trim())
    .filter(Boolean);

  for (let index = lines.length - 1; index >= 0; index -= 1) {
    const line = lines[index];
    if (/[=^+\-/*()∫√π]|\\(?:int|frac|sqrt|sin|cos|tan|lim)/.test(line)) {
      return line;
    }
  }

  return null;
}

export function plainMathToLatex(input: string): string {
  let value = input.trim();
  if (!value) {
    return "";
  }

  if (value.includes("\\int") || value.includes("\\frac") || value.includes("\\lim")) {
    return value;
  }

  const integralMatch = value.match(/^(?:integral|∫)\s+(.+?)\s+d([a-zA-Z])$/i);
  if (integralMatch) {
    const [, integrand, variable] = integralMatch;
    return `\\int ${normalizePlainExpression(integrand)}\\, d${variable}`;
  }

  const derivativeMatch = value.match(/^d\/d([a-zA-Z])\s*\((.+)\)$/i);
  if (derivativeMatch) {
    const [, variable, expression] = derivativeMatch;
    return `\\frac{d}{d${variable}}\\left(${normalizePlainExpression(expression)}\\right)`;
  }

  const limitMatch = value.match(/^lim\s+([a-zA-Z])\s*->\s*([^\s]+)\s+(.+)$/i);
  if (limitMatch) {
    const [, variable, point, expression] = limitMatch;
    return `\\lim_{${variable} \\to ${point}} ${normalizePlainExpression(expression)}`;
  }

  return normalizePlainExpression(value);
}

const _SUP_MAP: Record<string, string> = {
  "0": "⁰", "1": "¹", "2": "²", "3": "³", "4": "⁴",
  "5": "⁵", "6": "⁶", "7": "⁷", "8": "⁸", "9": "⁹",
};

export function latexToReadable(latex: string): string {
  let s = latex;

  // Strip block math delimiters — each block becomes its own line
  s = s.replace(/\\\[([\s\S]*?)\\\]/g, (_, c: string) => c.trim() + "\n");
  // Strip inline math delimiters
  s = s.replace(/\\\(([\s\S]*?)\\\)/g, (_, c: string) => c.trim());

  // \frac{a}{b} → (a)/(b)  — two passes for one level of nesting
  s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "($1)/($2)");
  s = s.replace(/\\frac\{([^{}]+)\}\{([^{}]+)\}/g, "($1)/($2)");

  // \sqrt{x} → √(x), \sqrt x → √x
  s = s.replace(/\\sqrt\{([^{}]+)\}/g, "√($1)");
  s = s.replace(/\\sqrt(?=\s)/g, "√");

  // \left( \right) → ( )
  s = s.replace(/\\left\(/g, "(").replace(/\\right\)/g, ")");
  s = s.replace(/\\left\[/g, "[").replace(/\\right\]/g, "]");
  s = s.replace(/\\left\|/g, "|").replace(/\\right\|/g, "|");
  s = s.replace(/\\left\./g, "").replace(/\\right\./g, "");

  // Function names: strip backslash
  s = s.replace(/\\(sin|cos|tan|cot|sec|csc|sinh|cosh|tanh|arcsin|arccos|arctan)\b/g, "$1");
  s = s.replace(/\\(lim|log|ln|exp|max|min|sup|inf|det|deg|gcd)\b/g, "$1");

  // Greek letters and common symbols
  s = s
    .replace(/\\int\b/g, "∫")
    .replace(/\\partial\b/g, "∂")
    .replace(/\\sum\b/g, "∑")
    .replace(/\\prod\b/g, "∏")
    .replace(/\\pi\b/g, "π")
    .replace(/\\infty\b/g, "∞")
    .replace(/\\to\b/g, "→")
    .replace(/\\times\b/g, "×")
    .replace(/\\div\b/g, "÷")
    .replace(/\\pm\b/g, "±")
    .replace(/\\mp\b/g, "∓")
    .replace(/\\leq\b/g, "≤")
    .replace(/\\geq\b/g, "≥")
    .replace(/\\neq\b/g, "≠")
    .replace(/\\approx\b/g, "≈")
    .replace(/\\cdot\b/g, "·")
    .replace(/\\ldots\b/g, "…")
    .replace(/\\alpha\b/g, "α")
    .replace(/\\beta\b/g, "β")
    .replace(/\\gamma\b/g, "γ")
    .replace(/\\Gamma\b/g, "Γ")
    .replace(/\\delta\b/g, "δ")
    .replace(/\\Delta\b/g, "Δ")
    .replace(/\\epsilon\b/g, "ε")
    .replace(/\\theta\b/g, "θ")
    .replace(/\\lambda\b/g, "λ")
    .replace(/\\mu\b/g, "μ")
    .replace(/\\nu\b/g, "ν")
    .replace(/\\sigma\b/g, "σ")
    .replace(/\\Sigma\b/g, "Σ")
    .replace(/\\phi\b/g, "φ")
    .replace(/\\Phi\b/g, "Φ")
    .replace(/\\omega\b/g, "ω")
    .replace(/\\Omega\b/g, "Ω")
    .replace(/\\rho\b/g, "ρ")
    .replace(/\\tau\b/g, "τ");

  // Superscripts: ^{single digit} or ^digit → Unicode superscript
  s = s.replace(/\^\{(\d)\}/g, (_, d: string) => _SUP_MAP[d] ?? `^{${d}}`);
  s = s.replace(/\^(\d)(?!\d)/g, (_, d: string) => _SUP_MAP[d] ?? `^${d}`);

  // Spacing commands
  s = s.replace(/\\[,;:!]/g, " ");
  s = s.replace(/\\(?:quad|qquad)\b/g, "  ");

  // \text{...} \mathrm{...} etc. → contents (must come before generic brace removal)
  s = s.replace(/\\(?:text|mathrm|mathit|mathbf|mathsf|mathtt|operatorname)\{([^{}]+)\}/g, "$1");

  // Clean up stray braces left from non-matched commands
  s = s.replace(/\{([^{}]*)\}/g, "$1");

  // Collapse horizontal whitespace only — preserve newlines between steps
  s = s.replace(/[^\S\n]+/g, " ");
  s = s.replace(/\n{3,}/g, "\n\n");
  s = s.trim();

  return s;
}

function splitBlockMath(content: string) {
  const segments: Array<{ kind: "text" | "block"; content: string }> = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  blockMathPattern.lastIndex = 0;

  while ((match = blockMathPattern.exec(content)) !== null) {
    if (match.index > lastIndex) {
      segments.push({
        kind: "text",
        content: content.slice(lastIndex, match.index),
      });
    }
    segments.push({ kind: "block", content: match[1].trim() });
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < content.length) {
    segments.push({ kind: "text", content: content.slice(lastIndex) });
  }

  return segments.filter((segment) => segment.content.trim().length > 0);
}

function renderTextSegment(content: string, segmentIndex: number) {
  return content
    .split(/\n{2,}/)
    .map((paragraph) => sanitizeParagraph(paragraph))
    .filter(Boolean)
    .map((paragraph, paragraphIndex) => {
      const labelMatch = paragraph.match(/^(Ejercicio|Pista|Resultado final):\s*(.*)$/i);
      if (labelMatch) {
        const [, label, rest] = labelMatch;
        if (rest && shouldRenderStandaloneMath(rest)) {
          return (
            <div key={`${segmentIndex}-${paragraphIndex}`} className="math-content__label-block">
              <span className="math-content__label">{label}:</span>
              <MathFormula
                expression={rest}
                source={looksLikeLatex(rest) ? "latex" : "plain"}
                displayMode
                className="math-content__block"
              />
            </div>
          );
        }
        return (
          <p key={`${segmentIndex}-${paragraphIndex}`} className="math-content__paragraph">
            <span className="math-content__label">{label}:</span>
            {rest ? <> {renderInlineText(rest, `${segmentIndex}-${paragraphIndex}-label`)}</> : null}
          </p>
        );
      }

      if (shouldRenderStandaloneMath(paragraph)) {
        return (
          <MathFormula
            key={`${segmentIndex}-${paragraphIndex}`}
            expression={paragraph}
            source={looksLikeLatex(paragraph) ? "latex" : "plain"}
            displayMode
            className="math-content__block"
          />
        );
      }

      return (
        <p key={`${segmentIndex}-${paragraphIndex}`} className="math-content__paragraph">
          {renderInlineText(paragraph, `${segmentIndex}-${paragraphIndex}`)}
        </p>
      );
    });
}

function renderInlineText(text: string, keyPrefix: string): ReactNode[] {
  const parts: ReactNode[] = [];
  let lastIndex = 0;
  let match: RegExpExecArray | null;
  inlineMathPattern.lastIndex = 0;

  while ((match = inlineMathPattern.exec(text)) !== null) {
    if (match.index > lastIndex) {
      parts.push(<span key={`${keyPrefix}-text-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>);
    }
    parts.push(
      <MathFormula
        key={`${keyPrefix}-math-${match.index}`}
        expression={match[1]}
        source="latex"
        className="math-content__inline"
      />,
    );
    lastIndex = match.index + match[0].length;
  }

  if (lastIndex < text.length) {
    parts.push(<span key={`${keyPrefix}-tail`}>{text.slice(lastIndex)}</span>);
  }

  return parts;
}

function normalizePlainExpression(expression: string): string {
  return expression
    // Unicode superscripts produced by latexToReadable
    .replace(/⁰/g, "^0").replace(/¹/g, "^1").replace(/²/g, "^2")
    .replace(/³/g, "^3").replace(/⁴/g, "^4").replace(/⁵/g, "^5")
    .replace(/⁶/g, "^6").replace(/⁷/g, "^7").replace(/⁸/g, "^8")
    .replace(/⁹/g, "^9")
    // Unicode math symbols → LaTeX
    .replace(/∫/g, "\\int ")
    .replace(/∂/g, "\\partial ")
    .replace(/∑/g, "\\sum ")
    .replace(/∏/g, "\\prod ")
    .replace(/π/g, "\\pi ")
    .replace(/∞/g, "\\infty")
    .replace(/→/g, "\\to ")
    .replace(/×/g, "\\times ")
    .replace(/÷/g, "\\div ")
    .replace(/±/g, "\\pm ")
    .replace(/∓/g, "\\mp ")
    .replace(/≤/g, "\\leq ")
    .replace(/≥/g, "\\geq ")
    .replace(/≠/g, "\\neq ")
    .replace(/≈/g, "\\approx ")
    .replace(/·/g, "\\cdot ")
    .replace(/α/g, "\\alpha ").replace(/β/g, "\\beta ").replace(/γ/g, "\\gamma ")
    .replace(/Γ/g, "\\Gamma ").replace(/δ/g, "\\delta ").replace(/Δ/g, "\\Delta ")
    .replace(/ε/g, "\\epsilon ").replace(/θ/g, "\\theta ").replace(/λ/g, "\\lambda ")
    .replace(/μ/g, "\\mu ").replace(/ν/g, "\\nu ").replace(/σ/g, "\\sigma ")
    .replace(/Σ/g, "\\Sigma ").replace(/φ/g, "\\phi ").replace(/Φ/g, "\\Phi ")
    .replace(/ω/g, "\\omega ").replace(/Ω/g, "\\Omega ").replace(/ρ/g, "\\rho ")
    .replace(/τ/g, "\\tau ")
    // √(x) produced by latexToReadable
    .replace(/√\(([^)]+)\)/g, "\\sqrt{$1}")
    .replace(/√/g, "\\sqrt ")
    // Existing ASCII replacements
    .replace(/\*\*/g, "^")
    .replace(/\bpi\b/g, "\\pi")
    .replace(/\bsin\b/g, "\\sin")
    .replace(/\bsen\b/g, "\\sin")
    .replace(/\bcos\b/g, "\\cos")
    .replace(/\btan\b/g, "\\tan")
    .replace(/\bln\b/g, "\\ln")
    .replace(/\blog\b/g, "\\log")
    .replace(/\bsqrt\(([^()]+)\)/g, "\\sqrt{$1}")
    .replace(/\bexp\(([^()]+)\)/g, "e^{$1}")
    .replace(/->/g, "\\to ")
    .replace(/\*/g, " ");
}

function shouldRenderStandaloneMath(text: string): boolean {
  const trimmed = text.trim();
  if (!trimmed) {
    return false;
  }
  if (isNarrativeSentence(trimmed)) {
    return false;
  }
  if (looksLikeLatex(trimmed) && trimmed.split(/\s+/).length <= 12) {
    return true;
  }
  const hasMathSignal = /[=^+\-/*()]|(?:\b(?:sin|cos|tan|lim|sqrt|integral)\b)/i.test(trimmed);
  const wordCount = trimmed.split(/\s+/).length;
  const alphabeticWords = (trimmed.match(/[A-Za-zÁÉÍÓÚáéíóúñÑ]+/g) ?? []).filter(
    (word) => !/^(sin|cos|tan|lim|sqrt|integral|dx|dy|dz|dt)$/i.test(word),
  );
  return hasMathSignal && wordCount <= 8 && alphabeticWords.length <= 1;
}

function looksLikeLatex(text: string): boolean {
  return /\\(?:frac|int|lim|sqrt|sin|cos|tan|pi|to|left|right)/.test(text);
}

function sanitizeParagraph(paragraph: string): string {
  const trimmed = paragraph.trim();
  if (!trimmed || /^(undefined|null)$/i.test(trimmed)) {
    return "";
  }
  return trimmed;
}

function isNarrativeSentence(text: string): boolean {
  const wordCount = text.split(/\s+/).length;
  const hasSentencePunctuation = /[.!?]$/.test(text);
  const alphaWords = text.match(/[A-Za-zÁÉÍÓÚáéíóúñÑ]{3,}/g) ?? [];
  return wordCount > 8 || hasSentencePunctuation || alphaWords.length > 3;
}
