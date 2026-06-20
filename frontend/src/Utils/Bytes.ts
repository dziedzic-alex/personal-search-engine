export function formatBytes(bytes: number): string {
  const kb = 1024;
  const mb = kb * 1024;
  const gb = mb * 1024;

  if (bytes < mb) {
    return `${formatUnit(bytes / kb)} KB`;
  }

  if (bytes < gb) {
    return `${formatUnit(bytes / mb)} MB`;
  }

  return `${formatUnit(bytes / gb)} GB`;
}

function formatUnit(value: number): string {
  const rounded = Math.round(value * 10) / 10;

  if (Number.isInteger(rounded)) {
    return rounded.toString();
  }

  return rounded.toFixed(1);
}
