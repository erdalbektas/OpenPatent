export const USPTO = {
  sheet: {
    width: 816,
    height: 1056,
    units: "px" as const,
    dpi: 96,
  },
  margins: {
    top: 25,
    right: 15,
    bottom: 10,
    left: 25,
  },
  fonts: {
    primary: "Arial, sans-serif",
    reference: "Arial, sans-serif",
    label: "Arial, sans-serif",
  },
  fontSizes: {
    reference: 10,
    label: 9,
    title: 14,
  },
  lineWeights: {
    visible: 1.5,
    hidden: 0.75,
    center: 0.75,
    guide: 0.5,
  },
  colors: {
    black: "#000000",
    white: "#ffffff",
    gray: "#808080",
  },
  reference: {
    start: 100,
    increment: 1,
    minHeight: 3.2,
  },
}

export function getUsableArea() {
  const { width, height } = USPTO.sheet
  const { top, right, bottom, left } = USPTO.margins
  return {
    x: left,
    y: top,
    width: width - left - right,
    height: height - top - bottom,
  }
}

export const FIGURE_NUMBER_OFFSET = { x: 15, y: 12 }
