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
        )
      )}
    </div>
  );
}

export function MathFormula({
  expression,
  displayMode = false,
  source = "latex",
  className,
}: MathFormulaProps) {
  const latexExpression = source === "plain" ? plainMathToLatex(expression) : expression.trim();
  const html = katex.renderToString(latexExpression || "\\,", {
    displayMode,
    throwOnError: false,
    strict: "ignore",
  });
  const Tag = displayMode ? "div" : "span";

  return (
    <Tag
      className={className}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  );
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
      parts.push(
        <span key={`${keyPrefix}-text-${lastIndex}`}>{text.slice(lastIndex, match.index)}</span>
      );
    }
    parts.push(
      <MathFormula
        key={`${keyPrefix}-math-${match.index}`}
        expression={match[1]}
        source="latex"
        className="math-content__inline"
      />
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
    .replace(/\*\*/g, "^")
    .replace(/\bpi\b/g, "\\pi")
    .replace(/\bsin\b/g, "\\sin")
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
    (word) => !/^(sin|cos|tan|lim|sqrt|integral|dx|dy|dz|dt)$/i.test(word)
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
